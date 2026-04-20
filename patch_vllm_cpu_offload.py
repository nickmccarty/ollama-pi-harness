"""
Patch vLLM 0.19.1 to allow cpu_offload + Mamba-hybrid models.

The assertion in may_reinitialize_input_batch fires unconditionally for
hybrid Mamba+Attention architectures (like Qwen3.6 MoE) because block
size alignment always triggers re-init. The re-init only touches input
batch tensors, not model weights, so cpu_offload is safe here.

PR reference: https://github.com/vllm-project/vllm/pull/18298

Usage:
    python patch_vllm_cpu_offload.py          # apply patch
    python patch_vllm_cpu_offload.py --revert # restore original
"""

import sys
import site
import os

# Full 4-line assert block (8-space indent inside method)
ASSERT_BLOCK = """\
        assert self.offload_config.uva.cpu_offload_gb == 0, (
            "Cannot re-initialize the input batch when CPU weight offloading is enabled. "
            "See https://github.com/vllm-project/vllm/pull/18298 for more details."
        )\
"""

PATCHED_BLOCK = """\
        # [cpu_offload patch] assertion removed — re-init is safe for Mamba-hybrid models
        # assert self.offload_config.uva.cpu_offload_gb == 0, (
        #     "Cannot re-initialize the input batch when CPU weight offloading is enabled. "
        #     "See https://github.com/vllm-project/vllm/pull/18298 for more details."
        # )\
"""


def find_target_file():
    for sp in site.getsitepackages():
        candidate = os.path.join(sp, "vllm", "v1", "worker", "gpu_model_runner.py")
        if os.path.exists(candidate):
            return candidate
    return None


def apply(path, old, new, label):
    with open(path, "r") as f:
        content = f.read()
    if old not in content:
        print(f"[patch] pattern not found for '{label}' — may already be applied or file changed")
        return False
    with open(path, "w") as f:
        f.write(content.replace(old, new, 1))
    print(f"[patch] {label}")
    return True


def main():
    revert = "--revert" in sys.argv
    path = find_target_file()
    if not path:
        print("[patch] ERROR: gpu_model_runner.py not found in site-packages")
        sys.exit(1)

    print(f"[patch] target: {path}")
    if revert:
        ok = apply(path, PATCHED_BLOCK, ASSERT_BLOCK, "reverted")
    else:
        ok = apply(path, ASSERT_BLOCK, PATCHED_BLOCK, "applied")

    if ok:
        print(f"[patch] done — restart vLLM")


if __name__ == "__main__":
    main()
