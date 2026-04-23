# Evolution of the Synthesis Instruction

## Initial Version
The synthesis instruction began as a directive to output markdown starting with a `#` heading, with sections structured using 'What', 'Why', and 'How' subsections. It required numbered steps and inline code blocks, with a focus on technical details and implementation specifics. The instruction emphasized completeness, including edge cases, trade-offs, and library recommendations. It also required that each strategy include when not to use it, input boundaries, and exact numerical values for configuration parameters with workload-based justification.

## Iterative Improvements
Over time, the instruction was refined to address gaps in clarity and completeness. The initial version had a tendency to produce overly verbose outputs, which could be inefficient for certain tasks. To address this, the instruction was modified to include a count-aware synthesis mode, which allowed the model to generate a specific number of sections or strategies based on the task's requirements. This helped in managing output length and ensuring that the content was focused and relevant.

Another key improvement was the introduction of a fallback instruction for non-technical tasks, such as recipes or general knowledge. This instruction avoided the use of code blocks and focused on prose-based explanations, ensuring that the model did not hallucinate technical details when they were not required.

## Current Version
The current synthesis instruction is as follows:

```
Output ONLY the markdown starting with #. Structure each section with 'What', 'Why', 'How' subsections using numbered steps and inline code blocks. Write at least 150 words per subsection with concrete implementation details, ensuring every code snippet is complete, executable with specific tool versions, and includes error handling. Every section MUST include a complete runnable code example with both opening and closing triple-backtick fences — never leave a code block unclosed. Include edge case notes, trade-offs, and library recommendations. For each strategy, state when NOT to use it, identify input boundaries, and specify exact numerical values for all configuration parameters with workload-based justification.
```

This version of the instruction is well-tuned for the current evaluator. It provides clear and specific guidance on how to structure the output, ensuring that the content is both comprehensive and actionable. The emphasis on concrete implementation details, complete code examples, and specific numerical values helps in producing high-quality, reproducible outputs that are useful for both developers and researchers.

## Lessons Learned
Through the autoresearch program, several key insights have been gained about what makes a good synthesis instruction:

1. **Clarity and Specificity**: The instruction must be clear and specific to avoid ambiguity. This includes specifying the structure of the output, the use of code blocks, and the inclusion of implementation details.

2. **Relevance and Focus**: The instruction should guide the model to focus on the task at hand, avoiding unnecessary details that could lead to hallucination or irrelevant content.

3. **Flexibility**: The instruction should allow for flexibility in handling different types of tasks, such as technical versus non-technical tasks, by providing fallback instructions when needed.

4. **Completeness and Accuracy**: The instruction should ensure that the output is complete and accurate, with a focus on providing actionable information that can be used by the end user.

5. **Consistency**: The instruction should be consistent across different tasks and models to ensure that the output is uniform and predictable.

## Remaining Gaps
While the current synthesis instruction is well-tuned, there are still a few areas that could be improved:

1. **Handling Edge Cases**: While the instruction includes a note on edge cases, it could be more explicit in guiding the model on how to handle them, especially in complex or ambiguous scenarios.

2. **Performance Considerations**: The instruction could be enhanced to include guidance on performance considerations, such as the impact of different configuration parameters on the performance of the system.

3. **User Experience**: The instruction could be refined to improve the user experience, such as by providing more guidance on how to structure the output for different types of users (e.g., developers, researchers, end-users).

Overall, the current synthesis instruction is well-tuned and effective for the current evaluator, but there is still room for improvement in certain areas.