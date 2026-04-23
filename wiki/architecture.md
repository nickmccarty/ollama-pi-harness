# Agent Harness Architecture

## 1. Agent Loop

The agent loop processes tasks from input to output, using skills and memory. It includes parsing skills, retrieving context, planning, research, synthesizing output, and evaluation. The core loop is implemented in `agent_loop()`, which calls `parse_skills()`, `retrieve_context()`, `plan()`, `execute_skills()`, `synthesize_output()`, and `evaluate_output()` in sequence. The loop uses `memory.retrieve()` to fetch relevant context and `planner.classify_task()` to determine the appropriate skill set.

## 2. Skill Dispatch

Skill dispatch activates specific skills based on task input. Skills are registered in `REGISTRY` in `skills.py`, and can be activated explicitly via `skill_dispatcher.dispatch(skill_name)` or automatically via `skill_dispatcher.auto_dispatch(task_input)`. For example, if the task input contains the phrase "analyze this data," the `auto_dispatch()` function triggers the `data_analysis_skill` with parameters like `input_data` and `analysis_type`. A concrete example is the `text_summarization_skill`, which is activated when the input contains the keyword "summarize" and has a minimum length threshold of 500 characters.

## 3. Planner

The planner determines the execution plan for tasks, classifying type and complexity to select appropriate skills. The `planner.classify_task()` function uses a heuristic model trained in `planner/heuristic_model.pkl` to classify tasks into categories like "simple," "moderate," or "complex." For complex tasks, it triggers a multi-step plan using `planner.generate_multi_step_plan()`, which may involve skills like `research_skill`, `data_analysis_skill`, and `synthesis_skill`.

## 4. Memory

Memory stores and retrieves past observations and retrieval. It uses a similarity model, `similarity_model.pkl`, to find relevant information and compresses data using `compressor.compress()` to maintain performance. The `memory.retrieve()` function uses cosine similarity to find the top 3 most relevant observations, which are then passed to the planner and skill dispatcher for context-aware execution.

## 5. Eval Pipeline

The eval pipeline evaluates output quality using criteria and revises it if necessary. It uses `evaluator.score_output()` with a scoring model trained in `evaluator/score_model.pkl` to assign a score between 0 and 1. If the score is below 0.7, the pipeline triggers `evaluator.revise_output()` using a revision model from `evaluator/revision_model.pkl`. The pipeline also includes a verification step using `evaluator.verify_output()` to ensure compliance with constraints like length, tone, and factual accuracy.

## 6. Server Queue

The server queue manages a task queue for efficient processing. Tasks are added to the queue via `server_queue.add_task()` and processed sequentially or in parallel based on resource availability. The queue uses a priority system, where tasks with higher urgency (e.g., from `high_priority` users) are processed first. The queue is implemented using a Redis-based message broker, with task processing handled by `server_queue.worker_process()`.