# /sync-wiki completed — updated Implementation Reference in wiki/pipeline.md

**Date:** 2026-04-20
**Target:** `C:\Users\nicho\Desktop\harness-engineering\wiki\pipeline.md`

## Facts extracted

- producer=pi-qwen-32b
- evaluator=Qwen3-Coder:30b
- planner=glm4:9b
- pass_threshold=9.0
- max_search_rounds=5
- max_context_observations=4
- quality_floor=7.0
- dim_weights extracted (5 dims)
- model_map entries: 15

## What was written

- **Models by stage table**: producer, evaluator, planner, assembly models with env var overrides
- **Key constants table**: search rounds, novelty threshold/epsilon, wiggum pass threshold and max rounds, memory observation count, subtask parallelism
- **Wiggum dimension weights**: all 5 scoring dimensions with weights and descriptions
- **Memory ranking formula**: exact blending formula + quality floor + deduplication logic
- **SYNTH_INSTRUCTION**: active synthesis prompt text
- **Model map**: Ollama tag → vLLM/HF model ID mapping