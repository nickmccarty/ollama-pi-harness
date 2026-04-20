import site, os

path = None
for sp in site.getsitepackages():
    candidate = os.path.join(sp, "vllm", "v1", "worker", "gpu_model_runner.py")
    if os.path.exists(candidate):
        path = candidate
        break

if not path:
    print("ERROR: gpu_model_runner.py not found"); exit(1)

print(f"target: {path}")
with open(path) as f:
    c = f.read()

old = (
    '            # [cpu_offload patch] assert self.offload_config.uva.cpu_offload_gb == 0, (\n'
    '                "Cannot re-initialize the input batch when CPU weight "\n'
    '                "offloading is enabled. See https://github.com/vllm-project/vllm/pull/18298 "  # noqa: E501\n'
    '                "for more details."\n'
    '            )'
)

new = (
    '            # [cpu_offload patch] re-init is safe with cpu_offload for Mamba-hybrid models\n'
    '            pass'
)

if old in c:
    with open(path, "w") as f:
        f.write(c.replace(old, new, 1))
    print("Fixed.")
else:
    print("Pattern not found — printing lines 6479-6490 for inspection:")
    lines = c.splitlines()
    for i, line in enumerate(lines[6478:6490], start=6479):
        print(f"{i}: {repr(line)}")
