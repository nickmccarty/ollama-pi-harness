"""
inference.py — unified LLM backend shim.

Drop-in replacement for `import ollama` throughout the harness. Routes calls to
either the local Ollama daemon (default) or a vLLM-served OpenAI-compatible
endpoint, based on the INFERENCE_BACKEND env var.

Environment variables
---------------------
INFERENCE_BACKEND   "ollama" (default) | "vllm"
VLLM_BASE_URL       vLLM server URL (default: http://localhost:8000/v1)
VLLM_API_KEY        auth key — vLLM ignores this by default ("none")
VLLM_MODEL_MAP      JSON dict overriding the built-in Ollama-tag → HF-ID map
                    e.g. '{"pi-qwen-32b": "Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4"}'

Migration
---------
Files using `import ollama` directly:
    - replace with `import inference as ollama`  (chat attribute exists at module level)

Files using the _OllamaShim pattern (agent.py, wiggum.py, autoresearch.py):
    - replace with `from inference import OllamaLike; ollama = OllamaLike(keep_alive=_KEEP_ALIVE)`

Files calling `_ollama_raw.chat(...)` directly (skills, email, lit_review, etc.):
    - replace with `from inference import chat as _llm_chat; _llm_chat(model=..., messages=..., options=...)`

logger.py's _extract_usage() works unchanged — _OllamaResponse exposes the same
attribute names (prompt_eval_count, eval_count, total_duration, eval_duration,
prompt_eval_duration, message.thinking) via getattr.
"""

import json
import os
import time

_BACKEND      = os.environ.get("INFERENCE_BACKEND", "ollama").lower()
_VLLM_BASE    = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
_VLLM_API_KEY = os.environ.get("VLLM_API_KEY", "none")

# ---------------------------------------------------------------------------
# Model name translation: Ollama tag → vLLM / HuggingFace model ID
# ---------------------------------------------------------------------------
# vLLM serves models by their HF repo ID (or the path you pass at startup).
# Add entries here OR override at runtime via VLLM_MODEL_MAP (JSON).
_MODEL_MAP: dict[str, str] = {
    "pi-qwen-32b":                    "Qwen/Qwen2.5-32B-Instruct",
    "pi-qwen":                        "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5:32b-instruct-q4_K_M":   "Qwen/Qwen2.5-32B-Instruct",
    "qwen2.5:7b-instruct":            "Qwen/Qwen2.5-7B-Instruct",
    "Qwen3-Coder:30b":                "Qwen/QwQ-32B",        # closest served equivalent
    "glm4:9b":                        "THUDM/glm-4-9b-chat",
    "llama3.2-vision":                "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "llama3.2:3b":                    "meta-llama/Llama-3.2-3B-Instruct",
    "mistral-small3.1:24b":           "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
    "phi4:14b":                       "microsoft/phi-4",
    "nomic-embed-text":               "nomic-ai/nomic-embed-text-v1.5",
}

_env_map = os.environ.get("VLLM_MODEL_MAP")
if _env_map:
    try:
        _MODEL_MAP.update(json.loads(_env_map))
    except Exception as _e:
        print(f"  [inference] VLLM_MODEL_MAP parse error: {_e}")


def _resolve_model(name: str) -> str:
    """Return the vLLM model ID for an Ollama model tag, or the name unchanged."""
    return _MODEL_MAP.get(name, name)


# ---------------------------------------------------------------------------
# Ollama-compatible response adapter for OpenAI/vLLM responses
# ---------------------------------------------------------------------------

class _OllamaMessage:
    """
    Adapter: makes an OpenAI ChatCompletionMessage look like an Ollama message.
    Supports both attribute access (response.message.content) and the dict-style
    access used throughout the harness (response["message"]["content"]).
    """
    def __init__(self, oai_message):
        self.role    = getattr(oai_message, "role", "assistant") or "assistant"
        self.content = getattr(oai_message, "content", "") or ""
        # vLLM with Qwen3 --enable-reasoning exposes reasoning_content here
        self.thinking = getattr(oai_message, "reasoning_content", None) or ""

    # dict-style fallback for legacy code: response["message"]["content"]
    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)


class _OllamaResponse:
    """
    Wraps an OpenAI ChatCompletion to look like an Ollama ChatResponse.

    Timing fields:
      The OpenAI API body does not expose per-phase latencies. We reconstruct
      them from wall-clock wrap time. Fractions are approximations:
        eval_duration   ≈ 88 % of total  (generation dominates)
        prompt_duration ≈ 12 % of total  (prompt-eval is fast on cached prefixes)

      For tighter measurements, wire in vLLM's Prometheus /metrics endpoint
      (vllm:e2e_request_latency_seconds, vllm:time_per_output_token_seconds)
      as a post-hoc annotation pass in dashboard.py.
    """
    def __init__(self, oai_response, wall_ns: int):
        usage = getattr(oai_response, "usage", None)
        self.prompt_eval_count       = getattr(usage, "prompt_tokens",     0) or 0
        self.eval_count              = getattr(usage, "completion_tokens", 0) or 0
        self.total_duration          = wall_ns
        self.eval_duration           = int(wall_ns * 0.88)
        self.prompt_eval_duration    = int(wall_ns * 0.12)
        self.load_duration           = 0
        self.message = _OllamaMessage(oai_response.choices[0].message)
        self._oai = oai_response

    # dict-style access: response["message"]["content"]
    def __getitem__(self, key):
        if key == "message":
            return self.message
        if key == "prompt_eval_count":
            return self.prompt_eval_count
        if key == "eval_count":
            return self.eval_count
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


# ---------------------------------------------------------------------------
# Backend implementations
# ---------------------------------------------------------------------------

def _chat_ollama(model: str, messages: list, **kwargs) -> object:
    import ollama as _ollama
    return _ollama.chat(model=model, messages=messages, **kwargs)


def _chat_vllm(model: str, messages: list, **kwargs) -> _OllamaResponse:
    from openai import OpenAI
    client = OpenAI(base_url=_VLLM_BASE, api_key=_VLLM_API_KEY)

    # Strip Ollama-specific kwargs vLLM doesn't understand
    kwargs.pop("keep_alive", None)
    options = kwargs.pop("options", {}) or {}

    oai_kwargs: dict = {}
    if "temperature" in options:
        oai_kwargs["temperature"] = options["temperature"]
    if "num_predict" in options:
        oai_kwargs["max_tokens"] = options["num_predict"]
    # num_ctx is a server-startup concern for vLLM (--max-model-len), not per-request
    # think=False: Qwen3 thinking mode — vLLM equivalent is not passing /think in prompt
    # think=True would require prepending a /think system message; leave for future work

    vllm_model = _resolve_model(model)
    t0 = time.monotonic_ns()
    resp = client.chat.completions.create(
        model=vllm_model,
        messages=messages,
        **oai_kwargs,
    )
    wall_ns = time.monotonic_ns() - t0
    return _OllamaResponse(resp, wall_ns)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chat(model: str, messages: list, **kwargs) -> object:
    """
    Drop-in replacement for ollama.chat().

    Routes to vLLM or Ollama based on INFERENCE_BACKEND env var.
    Response is always compatible with logger._extract_usage() and the
    response["message"]["content"] access pattern used throughout the harness.

    Automatic Ollama fallback: if INFERENCE_BACKEND=vllm but the model has no
    entry in _MODEL_MAP (e.g. glm4:9b, llama3.2-vision, llama3.2:3b), the call
    falls back to Ollama. Only mapped producer/evaluator models go to vLLM.
    """
    if _BACKEND == "vllm" and model in _MODEL_MAP:
        return _chat_vllm(model=model, messages=messages, **kwargs)
    return _chat_ollama(model=model, messages=messages, **kwargs)


class OllamaLike:
    """
    Drop-in for the _OllamaShim pattern used in agent.py, wiggum.py, autoresearch.py.

    Before:
        def _ollama_chat(*args, **kwargs):
            kwargs.setdefault("keep_alive", _KEEP_ALIVE)
            return _ollama_raw.chat(*args, **kwargs)
        ollama = type("_OllamaShim", (), {"chat": staticmethod(_ollama_chat)})()

    After:
        from inference import OllamaLike
        ollama = OllamaLike(keep_alive=_KEEP_ALIVE)

    keep_alive is injected for Ollama calls and silently dropped for vLLM.
    """
    def __init__(self, keep_alive=None):
        self._keep_alive = keep_alive

    def chat(self, model: str = None, *args, **kwargs):
        if self._keep_alive is not None and _BACKEND == "ollama":
            kwargs.setdefault("keep_alive", self._keep_alive)
        return chat(model=model, *args, **kwargs)


# Module-level shim so `import inference as ollama` works as a drop-in
# for files that call `ollama.chat(model=..., messages=..., options=...)`.
# `chat` is already defined as a module-level function above; this alias
# makes `ollama.chat(...)` resolve correctly when the module is imported as ollama.
_module_shim = OllamaLike()
