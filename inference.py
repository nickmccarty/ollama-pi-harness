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
VLLM_MODEL_MAP      JSON dict overriding the built-in Ollama-tag → served-name map
                    e.g. '{"pi-qwen3.6": "pi-qwen3.6", "pi-qwen-32b": "pi-qwen-32b"}'

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
import re
import time

_BACKEND      = os.environ.get("INFERENCE_BACKEND", "ollama").lower()
_VLLM_BASE    = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
_VLLM_API_KEY = os.environ.get("VLLM_API_KEY", "none")

# ---------------------------------------------------------------------------
# Model name translation: Ollama tag → vLLM / HuggingFace model ID
# ---------------------------------------------------------------------------
# vLLM serves models by --served-model-name (or the HF repo ID if not set).
# The Docker command uses --served-model-name pi-qwen3.6, so the harness tag
# maps to itself (identity). Override at runtime via VLLM_MODEL_MAP if needed.
_MODEL_MAP: dict[str, str] = {
    "pi-qwen3.6":                     "pi-qwen3.6",             # --served-model-name pi-qwen3.6
    "qwen3.6:35b-a3b":                "pi-qwen3.6",             # alias → same served name
    "pi-qwen3-14b":                   "pi-qwen3-14b",           # Qwen/Qwen2.5-14B-Instruct-AWQ, --served-model-name pi-qwen3-14b
    "pi-qwen3-32b":                   "pi-qwen3-32b",           # Qwen3-32B-AWQ via vLLM (--served-model-name pi-qwen3-32b)
    "pi-qwen-32b":                    "Qwen/Qwen2.5-32B-Instruct",  # Qwen2.5-32B (distinct from Qwen3-32B)
    "pi-qwen":                        "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5:32b-instruct-q4_K_M":   "Qwen/Qwen2.5-32B-Instruct",
    "qwen2.5:7b-instruct":            "Qwen/Qwen2.5-7B-Instruct",
    "Qwen3-Coder:30b":                "Qwen/Qwen3-Coder-480B-A22B",  # HF ID; needs dedicated serve
    "gemma4:latest":                  "google/gemma-4-9b-it",
    "gemma4:26b":                     "google/gemma-4-26b-it",
    "glm4:9b":                        "THUDM/glm-4-9b-chat",
    "llama3.2-vision":                "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "llama3.2:3b":                    "meta-llama/Llama-3.2-3B-Instruct",
    "mistral-small3.1:24b":           "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
    "phi4:14b":                       "microsoft/phi-4",
    "nomic-embed-text":               "nomic-ai/nomic-embed-text-v1.5",
}

_env_map = os.environ.get("VLLM_MODEL_MAP")
# _VLLM_ROUTE: models that actually route to vLLM. None = all models (pure vLLM mode).
# When VLLM_MODEL_MAP is set, only its keys route to vLLM; everything else falls to Ollama.
# This enables hybrid routing: vLLM for large producer models, Ollama for small utilities.
_VLLM_ROUTE: set | None = None
if _env_map:
    try:
        _env_parsed = json.loads(_env_map)
        _MODEL_MAP.update(_env_parsed)          # merge for name translation
        _VLLM_ROUTE = set(_env_parsed.keys())   # only listed models go to vLLM
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
        self.role = getattr(oai_message, "role", "assistant") or "assistant"
        raw = getattr(oai_message, "content", "") or ""
        # vLLM with reasoning parser populates reasoning_content and strips tags from content.
        # Without the parser (newer vLLM dropped the flag), tags appear inline — parse manually.
        reasoning = getattr(oai_message, "reasoning_content", None) or ""
        if not reasoning:
            m = re.search(r"<think>(.*?)</think>", raw, re.DOTALL)
            if m:
                reasoning = m.group(1).strip()
                raw = raw[raw.rfind("</think>") + len("</think>"):].strip()
        self.thinking = reasoning
        self.content  = raw

    @classmethod
    def from_raw(cls, role: str, content: str, thinking: str = "") -> "_OllamaMessage":
        """Build directly from accumulated streaming parts — no parsing needed."""
        obj = cls.__new__(cls)
        obj.role    = role
        obj.content = content
        obj.thinking = thinking
        return obj

    # dict-style fallback for legacy code: response["message"]["content"]
    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)


class _OllamaResponse:
    """
    Wraps vLLM streaming output to look like an Ollama ChatResponse.

    Timing fields come from real wall-clock measurements taken during streaming:
      prompt_eval_duration = time from request start to first content token (TTFT / prefill)
      eval_duration        = time from first token to stream end (generation)
      total_duration       = end-to-end wall time (prompt + eval + overhead)

    These are actual measurements, not approximations. They propagate into
    runs.jsonl, the dashboard tok/s charts, and benchmark comparisons.
    """
    def __init__(
        self,
        message:          "_OllamaMessage",
        prompt_tokens:    int,
        completion_tokens: int,
        total_ns:         int,
        prompt_ns:        int,   # TTFT: from request start to first generated token
        eval_ns:          int,   # from first token to stream end
    ):
        self.prompt_eval_count    = prompt_tokens
        self.eval_count           = completion_tokens
        self.total_duration       = total_ns
        self.prompt_eval_duration = prompt_ns
        self.eval_duration        = eval_ns
        self.load_duration        = 0
        self.message              = message

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
    # Ollama expects `think` as a top-level kwarg, not inside options.
    # Extract it from options dict if present and promote it.
    options = kwargs.get("options") or {}
    if "think" in options:
        options = dict(options)
        kwargs["think"] = options.pop("think")
        kwargs["options"] = options
    return _ollama.chat(model=model, messages=messages, **kwargs)


def _stream_vllm_call(client, vllm_model: str, messages: list, oai_kwargs: dict):
    """
    Execute one streaming vLLM completion.

    Returns (message, prompt_tokens, completion_tokens, total_ns, prompt_ns, eval_ns).

    Streaming gives us real per-phase timing:
      prompt_ns = TTFT (prefill latency) — time from request dispatch to first content token
      eval_ns   = generation latency — time from first token to stream end
    This replaces the previous 0.88/0.12 wall-clock approximation.
    """
    t0      = time.monotonic_ns()
    t_first = None

    content_parts   = []
    reasoning_parts = []
    prompt_tokens   = 0
    completion_tokens = 0

    stream = client.chat.completions.create(
        model=vllm_model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        **oai_kwargs,
    )

    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta
            c = delta.content or ""
            r = getattr(delta, "reasoning_content", None) or ""
            if t_first is None and (c or r):
                t_first = time.monotonic_ns()
            if c:
                content_parts.append(c)
            if r:
                reasoning_parts.append(r)
        if getattr(chunk, "usage", None):
            prompt_tokens     = chunk.usage.prompt_tokens     or 0
            completion_tokens = chunk.usage.completion_tokens or 0

    t_end = time.monotonic_ns()
    if t_first is None:
        t_first = t_end  # model returned nothing — avoid negative intervals

    raw_content = "".join(content_parts)
    reasoning   = "".join(reasoning_parts)

    # Handle inline <think> tags when the reasoning parser wasn't active
    if not reasoning:
        m = re.search(r"<think>(.*?)</think>", raw_content, re.DOTALL)
        if m:
            reasoning   = m.group(1).strip()
            raw_content = raw_content[raw_content.rfind("</think>") + len("</think>"):].strip()

    msg = _OllamaMessage.from_raw("assistant", raw_content, reasoning)
    return (
        msg,
        prompt_tokens,
        completion_tokens,
        t_end - t0,      # total_ns
        t_first - t0,    # prompt_ns  (TTFT)
        t_end - t_first, # eval_ns    (generation)
    )


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
    #
    # Thinking mode: always emit enable_thinking for Qwen/QwQ vLLM models.
    # Default to False when the caller didn't specify — the vLLM server may be running
    # a thinking model (e.g. Qwen3.6) even when the Ollama tag suggests otherwise
    # (e.g. pi-qwen-32b → Qwen/Qwen2.5-32B-Instruct resolves to the loaded Qwen3.6).
    # Without an explicit enable_thinking=false, Qwen3.6 enters unbounded reasoning
    # and never returns within the num_predict budget.
    vllm_name = _resolve_model(model).lower()
    if any(k in vllm_name for k in ("qwen", "qwq")):
        chat_tmpl: dict = {}
        if "think" in options:
            chat_tmpl["enable_thinking"] = bool(options["think"])
        else:
            chat_tmpl["enable_thinking"] = False  # safe default: no unbounded reasoning
        if "preserve_thinking" in options:
            chat_tmpl["preserve_thinking"] = bool(options["preserve_thinking"])
        oai_kwargs["extra_body"] = {"chat_template_kwargs": chat_tmpl}

    vllm_model = _resolve_model(model)

    # Retry up to 2× on context-length or server-disconnect errors.
    # Server disconnects (RemoteProtocolError / APIConnectionError with "Server disconnected")
    # are the vLLM OOM signal: the server crashes under KV-cache pressure from a large
    # context. We treat them identically to explicit context-length rejections: truncate
    # the longest non-system message and retry with halved max_tokens.
    #
    # Critical: never truncate the system prompt — it contains the task framing and
    # skill instructions. Truncating it silently corrupts all downstream behaviour.
    # Instead, target the longest non-system message. If only system messages exist
    # (degenerate case), fall back to the longest overall.
    # Keep head (60%) + tail (20%) rather than just head, so both the instruction
    # preamble and the most recent context survive the cut.
    _messages = list(messages)
    for attempt in range(3):
        try:
            msg, ptok, ctok, total_ns, prompt_ns, eval_ns = _stream_vllm_call(
                client, vllm_model, _messages, oai_kwargs,
            )
            return _OllamaResponse(msg, ptok, ctok, total_ns, prompt_ns, eval_ns)
        except Exception as exc:
            exc_str = str(exc)
            _is_ctx_err = "maximum context length" in exc_str
            _is_disconnect = (
                "Server disconnected" in exc_str
                or "RemoteProtocolError" in exc_str
                or ("Connection error" in exc_str and attempt == 0)
            )
            if (_is_ctx_err or _is_disconnect) and attempt < 2:
                reason = "context too long" if _is_ctx_err else "server disconnect (OOM)"
                candidates = [
                    (i, len(str(_messages[i].get("content", "") or "")))
                    for i, m in enumerate(_messages)
                    if _messages[i].get("role") != "system"
                ]
                if not candidates:
                    # Only system messages — must truncate to proceed (log a warning)
                    candidates = [(i, len(str(_messages[i].get("content", "") or "")))
                                  for i in range(len(_messages))]
                    print("  [inference] WARNING: only system messages remain — "
                          "truncating system prompt to fit context window")

                longest_idx = max(candidates, key=lambda x: x[1])[0]
                content  = str(_messages[longest_idx].get("content", "") or "")
                keep_head = int(len(content) * 0.60)
                keep_tail = int(len(content) * 0.20)
                truncated = content[:keep_head] + "\n…[truncated]…\n" + content[-keep_tail:]
                _messages[longest_idx] = {**_messages[longest_idx], "content": truncated}
                if "max_tokens" in oai_kwargs:
                    oai_kwargs = dict(oai_kwargs)
                    oai_kwargs["max_tokens"] = max(256, oai_kwargs["max_tokens"] // 2)
                role = _messages[longest_idx].get("role", "?")
                print(f"  [inference] {reason} — truncated {role} msg[{longest_idx}] "
                      f"({len(content)}→{len(truncated)} chars), "
                      f"max_tokens={oai_kwargs.get('max_tokens', '?')}, retry {attempt+1}/2")
            else:
                raise


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chat(model: str, messages: list, **kwargs) -> object:
    """
    Drop-in replacement for ollama.chat().

    Routes to vLLM or Ollama based on INFERENCE_BACKEND and VLLM_MODEL_MAP.

    Hybrid routing: when VLLM_MODEL_MAP is set, only the listed models go to vLLM;
    everything else (small utilities, evaluators) falls back to Ollama. This lets
    vLLM serve the large producer model while Ollama handles glm4:9b, selene-mini, etc.
    When VLLM_MODEL_MAP is unset (_VLLM_ROUTE is None), all calls go to vLLM.
    """
    if _BACKEND == "vllm" and (_VLLM_ROUTE is None or model in _VLLM_ROUTE):
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


# ---------------------------------------------------------------------------
# Embedding API
# ---------------------------------------------------------------------------

_LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"   # ~22MB, fast, 384 dims


def _embed_vllm(texts: list[str]) -> list[list[float]]:
    """Embed via vLLM /v1/embeddings using the first served model."""
    from openai import OpenAI
    client = OpenAI(base_url=_VLLM_BASE, api_key=_VLLM_API_KEY)
    embed_model = next(iter(_MODEL_MAP.values())) if _MODEL_MAP else "default"
    resp = client.embeddings.create(model=embed_model, input=texts)
    return [d.embedding for d in resp.data]


_LOCAL_EMBED_INSTANCE = None  # module-level cache — avoids reloading weights each call


def _embed_local(texts: list[str]) -> list[list[float]]:
    """Embed via sentence-transformers (all-MiniLM-L6-v2, local, no API)."""
    global _LOCAL_EMBED_INSTANCE
    if _LOCAL_EMBED_INSTANCE is None:
        from sentence_transformers import SentenceTransformer
        _LOCAL_EMBED_INSTANCE = SentenceTransformer(_LOCAL_EMBED_MODEL)
    return _LOCAL_EMBED_INSTANCE.encode(texts, show_progress_bar=False).tolist()


def embed(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts using the current backend.

    vLLM backend: uses /v1/embeddings with the served model (same Qwen instance,
    no extra VRAM). Falls back to sentence-transformers on any error.
    Ollama backend: uses sentence-transformers directly.

    Returns list of float vectors, one per input text.
    """
    if _BACKEND == "vllm":
        try:
            return _embed_vllm(texts)
        except Exception as e:
            print(f"  [inference:embed] vLLM embed failed ({e}) — falling back to local")
    return _embed_local(texts)


def get_embedding_function(device: str = "cpu"):
    """
    Return a ChromaDB-compatible EmbeddingFunction.

    Always returns SentenceTransformerEmbeddingFunction (384-dim, local).
    vLLM /v1/embeddings is only available when the served model is started with
    --task embed, which is separate from the generate instance. Until a dedicated
    embed endpoint is available, both backends use the same local model so that
    ChromaDB collections stay compatible across backend switches.
    """
    from chromadb.utils import embedding_functions
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=_LOCAL_EMBED_MODEL,
        device=device,
    )


def get_embed_collection_suffix() -> str:
    """
    Collection name suffix for backend isolation.

    Returns "" always: both Ollama and vLLM backends use the same local
    sentence-transformers model (384-dim), so no collection isolation is needed.
    If a dedicated vLLM embed endpoint (--task embed) is added in future, this
    should probe the actual embedding dimension and return "_vllm" when different.
    """
    return ""


