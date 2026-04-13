# arXiv Papers (Agentic / LLM / Autonomous Systems)

## Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents

**Authors:** Renxi Wang, Haonan Li, Xudong Han, Yixuan Zhang, Timothy Baldwin

**Published:** 2024-02-18T17:10:07Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2402.11651v2) | [PDF](https://arxiv.org/pdf/2402.11651v2)

**Abstract:**
Large language models (LLMs) have achieved success in acting as agents, which interact with environments through tools such as search engines. However, LLMs are optimized for language generation instead of tool use during training or alignment, limiting their effectiveness as agents. To resolve this problem, previous work has first collected interaction trajectories between LLMs and environments, using only trajectories that successfully finished the task to fine-tune smaller models, making fine-tuning data scarce and acquiring it both difficult and costly. Discarding failed trajectories also leads to significant wastage of data and resources and limits the possible optimization paths during fine-tuning. In this paper, we argue that unsuccessful trajectories offer valuable insights, and LLMs can learn from these trajectories through appropriate quality control and fine-tuning strategies. By simply adding a prefix or suffix that tells the model whether to generate a successful trajectory during training, we improve model performance by a large margin on mathematical reasoning, multi-hop question answering, and strategic question answering tasks. We further analyze the inference results and find that our method provides a better trade-off between valuable information and errors in unsuccessful trajectories. To our knowledge, we are the first to demonstrate the value of negative trajectories and their application in agent-tunning scenarios. Our findings offer guidance for developing better agent-tuning methods and low-resource data usage techniques.

---

## Focus Agent: LLM-Powered Virtual Focus Group

**Authors:** Taiyu Zhang, Xuesong Zhang, Robbe Cools, Adalberto L. Simeone

**Published:** 2024-09-03T13:56:14Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2409.01907v1) | [PDF](https://arxiv.org/pdf/2409.01907v1)

**Abstract:**
In the domain of Human-Computer Interaction, focus groups represent a widely utilised yet resource-intensive methodology, often demanding the expertise of skilled moderators and meticulous preparatory efforts. This study introduces the ``Focus Agent,'' a Large Language Model (LLM) powered framework that simulates both the focus group (for data collection) and acts as a moderator in a focus group setting with human participants. To assess the data quality derived from the Focus Agent, we ran five focus group sessions with a total of 23 human participants as well as deploying the Focus Agent to simulate these discussions with AI participants. Quantitative analysis indicates that Focus Agent can generate opinions similar to those of human participants. Furthermore, the research exposes some improvements associated with LLMs acting as moderators in focus group discussions that include human participants.

---

## A Plan Reuse Mechanism for LLM-Driven Agent

**Authors:** Guopeng Li, Ruiqi Wu, Haisheng Tan

**Published:** 2025-12-24T18:08:03Z

**Categories:** cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2512.21309v2) | [PDF](https://arxiv.org/pdf/2512.21309v2)

**Abstract:**
Integrating large language models (LLMs) into personal assistants, like Xiao Ai and Blue Heart V, effectively enhances their ability to interact with humans, solve complex tasks, and manage IoT devices. Such assistants are also termed LLM-driven agents. Upon receiving user requests, the LLM-driven agent generates plans using an LLM, executes these plans through various tools, and then returns the response to the user. During this process, the latency for generating a plan with an LLM can reach tens of seconds, significantly degrading user experience. Real-world dataset analysis shows that about 30% of the requests received by LLM-driven agents are identical or similar, which allows the reuse of previously generated plans to reduce latency. However, it is difficult to accurately define the similarity between the request texts received by the LLM-driven agent through directly evaluating the original request texts. Moreover, the diverse expressions of natural language and the unstructured format of plan texts make implementing plan reuse challenging. To address these issues, we present and implement a plan reuse mechanism for LLM-driven agents called AgentReuse. AgentReuse leverages the similarities and differences among requests' semantics and uses intent classification to evaluate the similarities between requests and enable the reuse of plans. Experimental results based on a real-world dataset demonstrate that AgentReuse achieves a 93% effective plan reuse rate, an F1 score of 0.9718, and an accuracy of 0.9459 in evaluating request similarities, reducing latency by 93.12% compared with baselines without using the reuse mechanism.

---

## Small LLMs Are Weak Tool Learners: A Multi-LLM Agent

**Authors:** Weizhou Shen, Chenliang Li, Hongzhan Chen, Ming Yan, Xiaojun Quan, Hehong Chen, Ji Zhang, Fei Huang

**Published:** 2024-01-14T16:17:07Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2401.07324v3) | [PDF](https://arxiv.org/pdf/2401.07324v3)

**Abstract:**
Large Language Model (LLM) agents significantly extend the capabilities of standalone LLMs, empowering them to interact with external tools (e.g., APIs, functions) and complete various tasks in a self-directed fashion. The challenge of tool use demands that LLMs not only understand user queries and generate answers accurately but also excel in task planning, tool invocation, and result summarization. While traditional works focus on training a single LLM with all these capabilities, performance limitations become apparent, particularly with smaller models. To overcome these challenges, we propose a novel approach that decomposes the aforementioned capabilities into a planner, caller, and summarizer. Each component is implemented by a single LLM that focuses on a specific capability and collaborates with others to accomplish the task. This modular framework facilitates individual updates and the potential use of smaller LLMs for building each capability. To effectively train this framework, we introduce a two-stage training paradigm. First, we fine-tune a backbone LLM on the entire dataset without discriminating sub-tasks, providing the model with a comprehensive understanding of the task. Second, the fine-tuned LLM is used to instantiate the planner, caller, and summarizer respectively, which are continually fine-tuned on respective sub-tasks. Evaluation across various tool-use benchmarks illustrates that our proposed multi-LLM framework surpasses the traditional single-LLM approach, highlighting its efficacy and advantages in tool learning.

---

## MedAide: Information Fusion and Anatomy of Medical Intents via LLM-based Agent Collaboration

**Authors:** Dingkang Yang, Jinjie Wei, Mingcheng Li, Jiyao Liu, Lihao Liu, Ming Hu, Junjun He, Yakun Ju, Wei Zhou, Yang Liu, Lihua Zhang

**Published:** 2024-10-16T13:10:27Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2410.12532v3) | [PDF](https://arxiv.org/pdf/2410.12532v3)

**Abstract:**
In healthcare intelligence, the ability to fuse heterogeneous, multi-intent information from diverse clinical sources is fundamental to building reliable decision-making systems. Large Language Model (LLM)-driven information interaction systems currently showing potential promise in the healthcare domain. Nevertheless, they often suffer from information redundancy and coupling when dealing with complex medical intents, leading to severe hallucinations and performance bottlenecks. To this end, we propose MedAide, an LLM-based medical multi-agent collaboration framework designed to enable intent-aware information fusion and coordinated reasoning across specialized healthcare domains. Specifically, we introduce a regularization-guided module that combines syntactic constraints with retrieval augmented generation to decompose complex queries into structured representations, facilitating fine-grained clinical information fusion and intent resolution. Additionally, a dynamic intent prototype matching module is proposed to utilize dynamic prototype representation with a semantic similarity matching mechanism to achieve adaptive recognition and updating of the agent's intent in multi-round healthcare dialogues. Ultimately, we design a rotation agent collaboration mechanism that introduces dynamic role rotation and decision-level information fusion across specialized medical agents. Extensive experiments are conducted on four medical benchmarks with composite intents. Experimental results from automated metrics and expert doctor evaluations show that MedAide outperforms current LLMs and improves their medical proficiency and strategic reasoning.

---

## Context Engineering for Multi-Agent LLM Code Assistants Using Elicit, NotebookLM, ChatGPT, and Claude Code

**Authors:** Muhammad Haseeb

**Published:** 2025-08-09T14:45:53Z

**Categories:** cs.SE, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2508.08322v1) | [PDF](https://arxiv.org/pdf/2508.08322v1)

**Abstract:**
Large Language Models (LLMs) have shown promise in automating code generation and software engineering tasks, yet they often struggle with complex, multi-file projects due to context limitations and knowledge gaps. We propose a novel context engineering workflow that combines multiple AI components: an Intent Translator (GPT-5) for clarifying user requirements, an Elicit-powered semantic literature retrieval for injecting domain knowledge, NotebookLM-based document synthesis for contextual understanding, and a Claude Code multi-agent system for code generation and validation. Our integrated approach leverages intent clarification, retrieval-augmented generation, and specialized sub-agents orchestrated via Claude's agent framework. We demonstrate that this method significantly improves the accuracy and reliability of code assistants in real-world repositories, yielding higher single-shot success rates and better adherence to project context than baseline single-agent approaches. Qualitative results on a large Next.js codebase show the multi-agent system effectively plans, edits, and tests complex features with minimal human intervention. We compare our system with recent frameworks like CodePlan, MASAI, and HyperAgent, highlighting how targeted context injection and agent role decomposition lead to state-of-the-art performance. Finally, we discuss the implications for deploying LLM-based coding assistants in production, along with lessons learned on context management and future research directions.

---

## Agent-R1: Training Powerful LLM Agents with End-to-End Reinforcement Learning

**Authors:** Mingyue Cheng, Jie Ouyang, Shuo Yu, Ruiran Yan, Yucong Luo, Zirui Liu, Daoyu Wang, Qi Liu, Enhong Chen

**Published:** 2025-11-18T13:03:15Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2511.14460v1) | [PDF](https://arxiv.org/pdf/2511.14460v1)

**Abstract:**
Large Language Models (LLMs) are increasingly being explored for building Agents capable of active environmental interaction (e.g., via tool use) to solve complex problems. Reinforcement Learning (RL) is considered a key technology with significant potential for training such Agents; however, the effective application of RL to LLM Agents is still in its nascent stages and faces considerable challenges. Currently, this emerging field lacks in-depth exploration into RL approaches specifically tailored for the LLM Agent context, alongside a scarcity of flexible and easily extensible training frameworks designed for this purpose. To help advance this area, this paper first revisits and clarifies Reinforcement Learning methodologies for LLM Agents by systematically extending the Markov Decision Process (MDP) framework to comprehensively define the key components of an LLM Agent. Secondly, we introduce Agent-R1, a modular, flexible, and user-friendly training framework for RL-based LLM Agents, designed for straightforward adaptation across diverse task scenarios and interactive environments. We conducted experiments on Multihop QA benchmark tasks, providing initial validation for the effectiveness of our proposed methods and framework.

---

## KG-Agent: An Efficient Autonomous Agent Framework for Complex Reasoning over Knowledge Graph

**Authors:** Jinhao Jiang, Kun Zhou, Wayne Xin Zhao, Yang Song, Chen Zhu, Hengshu Zhu, Ji-Rong Wen

**Published:** 2024-02-17T02:07:49Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2402.11163v1) | [PDF](https://arxiv.org/pdf/2402.11163v1)

**Abstract:**
In this paper, we aim to improve the reasoning ability of large language models (LLMs) over knowledge graphs (KGs) to answer complex questions. Inspired by existing methods that design the interaction strategy between LLMs and KG, we propose an autonomous LLM-based agent framework, called KG-Agent, which enables a small LLM to actively make decisions until finishing the reasoning process over KGs. In KG-Agent, we integrate the LLM, multifunctional toolbox, KG-based executor, and knowledge memory, and develop an iteration mechanism that autonomously selects the tool then updates the memory for reasoning over KG. To guarantee the effectiveness, we leverage program language to formulate the multi-hop reasoning process over the KG, and synthesize a code-based instruction dataset to fine-tune the base LLM. Extensive experiments demonstrate that only using 10K samples for tuning LLaMA-7B can outperform state-of-the-art methods using larger LLMs or more data, on both in-domain and out-domain datasets. Our code and data will be publicly released.

---

## Lang-PINN: From Language to Physics-Informed Neural Networks via a Multi-Agent Framework

**Authors:** Xin He, Liangliang You, Hongduan Tian, Bo Han, Ivor Tsang, Yew-Soon Ong

**Published:** 2025-10-03T08:20:02Z

**Categories:** cs.AI, cs.CE, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2510.05158v1) | [PDF](https://arxiv.org/pdf/2510.05158v1)

**Abstract:**
Physics-informed neural networks (PINNs) provide a powerful approach for solving partial differential equations (PDEs), but constructing a usable PINN remains labor-intensive and error-prone. Scientists must interpret problems as PDE formulations, design architectures and loss functions, and implement stable training pipelines. Existing large language model (LLM) based approaches address isolated steps such as code generation or architecture suggestion, but typically assume a formal PDE is already specified and therefore lack an end-to-end perspective. We present Lang-PINN, an LLM-driven multi-agent system that builds trainable PINNs directly from natural language task descriptions. Lang-PINN coordinates four complementary agents: a PDE Agent that parses task descriptions into symbolic PDEs, a PINN Agent that selects architectures, a Code Agent that generates modular implementations, and a Feedback Agent that executes and diagnoses errors for iterative refinement. This design transforms informal task statements into executable and verifiable PINN code. Experiments show that Lang-PINN achieves substantially lower errors and greater robustness than competitive baselines: mean squared error (MSE) is reduced by up to 3--5 orders of magnitude, end-to-end execution success improves by more than 50\%, and reduces time overhead by up to 74\%.

---

## Large Language Model Agent: A Survey on Methodology, Applications and Challenges

**Authors:** Junyu Luo, Weizhi Zhang, Ye Yuan, Yusheng Zhao, Junwei Yang, Yiyang Gu, Bohan Wu, Binqi Chen, Ziyue Qiao, Qingqing Long, Rongcheng Tu, Xiao Luo, Wei Ju, Zhiping Xiao, Yifan Wang, Meng Xiao, Chenwu Liu, Jingyang Yuan, Shichang Zhang, Yiqiao Jin, Fan Zhang, Xian Wu, Hanqing Zhao, Dacheng Tao, Philip S. Yu, Ming Zhang

**Published:** 2025-03-27T12:50:17Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2503.21460v1) | [PDF](https://arxiv.org/pdf/2503.21460v1)

**Abstract:**
The era of intelligent agents is upon us, driven by revolutionary advancements in large language models. Large Language Model (LLM) agents, with goal-driven behaviors and dynamic adaptation capabilities, potentially represent a critical pathway toward artificial general intelligence. This survey systematically deconstructs LLM agent systems through a methodology-centered taxonomy, linking architectural foundations, collaboration mechanisms, and evolutionary pathways. We unify fragmented research threads by revealing fundamental connections between agent design principles and their emergent behaviors in complex environments. Our work provides a unified architectural perspective, examining how agents are constructed, how they collaborate, and how they evolve over time, while also addressing evaluation methodologies, tool applications, practical challenges, and diverse application domains. By surveying the latest developments in this rapidly evolving field, we offer researchers a structured taxonomy for understanding LLM agents and identify promising directions for future research. The collection is available at https://github.com/luo-junyu/Awesome-Agent-Papers.

---

## Exploring Advanced Large Language Models with LLMsuite

**Authors:** Giorgio Roffo

**Published:** 2024-07-01T05:37:17Z

**Categories:** cs.CL, cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2407.12036v2) | [PDF](https://arxiv.org/pdf/2407.12036v2)

**Abstract:**
This tutorial explores the advancements and challenges in the development of Large Language Models (LLMs) such as ChatGPT and Gemini. It addresses inherent limitations like temporal knowledge cutoffs, mathematical inaccuracies, and the generation of incorrect information, proposing solutions like Retrieval Augmented Generation (RAG), Program-Aided Language Models (PAL), and frameworks such as ReAct and LangChain. The integration of these techniques enhances LLM performance and reliability, especially in multi-step reasoning and complex task execution. The paper also covers fine-tuning strategies, including instruction fine-tuning, parameter-efficient methods like LoRA, and Reinforcement Learning from Human Feedback (RLHF) as well as Reinforced Self-Training (ReST). Additionally, it provides a comprehensive survey of transformer architectures and training techniques for LLMs. The source code can be accessed by contacting the author via email for a request.

---

## RETA-LLM: A Retrieval-Augmented Large Language Model Toolkit

**Authors:** Jiongnan Liu, Jiajie Jin, Zihan Wang, Jiehan Cheng, Zhicheng Dou, Ji-Rong Wen

**Published:** 2023-06-08T14:10:54Z

**Categories:** cs.IR

**Links:** [Abstract](https://arxiv.org/abs/2306.05212v1) | [PDF](https://arxiv.org/pdf/2306.05212v1)

**Abstract:**
Although Large Language Models (LLMs) have demonstrated extraordinary capabilities in many domains, they still have a tendency to hallucinate and generate fictitious responses to user requests. This problem can be alleviated by augmenting LLMs with information retrieval (IR) systems (also known as retrieval-augmented LLMs). Applying this strategy, LLMs can generate more factual texts in response to user input according to the relevant content retrieved by IR systems from external corpora as references. In addition, by incorporating external knowledge, retrieval-augmented LLMs can answer in-domain questions that cannot be answered by solely relying on the world knowledge stored in parameters. To support research in this area and facilitate the development of retrieval-augmented LLM systems, we develop RETA-LLM, a {RET}reival-{A}ugmented LLM toolkit. In RETA-LLM, we create a complete pipeline to help researchers and users build their customized in-domain LLM-based systems. Compared with previous retrieval-augmented LLM systems, RETA-LLM provides more plug-and-play modules to support better interaction between IR systems and LLMs, including {request rewriting, document retrieval, passage extraction, answer generation, and fact checking} modules. Our toolkit is publicly available at https://github.com/RUC-GSAI/YuLan-IR/tree/main/RETA-LLM.

---

## PB-LLM: Partially Binarized Large Language Models

**Authors:** Yuzhang Shang, Zhihang Yuan, Qiang Wu, Zhen Dong

**Published:** 2023-09-29T14:35:27Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2310.00034v2) | [PDF](https://arxiv.org/pdf/2310.00034v2)

**Abstract:**
This paper explores network binarization, a radical form of quantization, compressing model weights to a single bit, specifically for Large Language Models (LLMs) compression. Due to previous binarization methods collapsing LLMs, we propose a novel approach, Partially-Binarized LLM (PB-LLM), which can achieve extreme low-bit quantization while maintaining the linguistic reasoning capacity of quantized LLMs. Specifically, our exploration first uncovers the ineffectiveness of naive applications of existing binarization algorithms and highlights the imperative role of salient weights in achieving low-bit quantization. Thus, PB-LLM filters a small ratio of salient weights during binarization, allocating them to higher-bit storage, i.e., partially-binarization. PB-LLM is extended to recover the capacities of quantized LMMs, by analyzing from the perspective of post-training quantization (PTQ) and quantization-aware training (QAT). Under PTQ, combining the concepts from GPTQ, we reconstruct the binarized weight matrix guided by the Hessian matrix and successfully recover the reasoning capacity of PB-LLM in low-bit. Under QAT, we freeze the salient weights during training, explore the derivation of optimal scaling factors crucial for minimizing the quantization error, and propose a scaling mechanism based on this derived scaling strategy for residual binarized weights. Those explorations and the developed methodologies significantly contribute to rejuvenating the performance of low-bit quantized LLMs and present substantial advancements in the field of network binarization for LLMs.The code is available at https://github.com/hahnyuan/BinaryLLM.

---

## Echoing: Identity Failures when LLM Agents Talk to Each Other

**Authors:** Sarath Shekkizhar, Romain Cosentino, Adam Earle, Silvio Savarese

**Published:** 2025-11-12T20:17:10Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2511.09710v3) | [PDF](https://arxiv.org/pdf/2511.09710v3)

**Abstract:**
As large language model (LLM) based agents interact autonomously with one another, a new class of failures emerges that cannot be predicted from single agent performance: behavioral drifts in agent-agent conversations (AxA). Unlike human-agent interactions, where humans ground and steer conversations, AxA lacks such stabilizing signals, making these failures unique. We investigate one such failure, echoing, where agents abandon their assigned roles and instead mirror their conversational partners, undermining their intended objectives. Through experiments across $66$ AxA configurations, $4$ domains (3 transactional, 1 advisory), and $2500+$ conversations (over $250000$ LLM inferences), we show that echoing occurs across major LLM providers, with echoing rates as high as $70\%$ depending on the model and domain. Moreover, we find that echoing is persistent even in advanced reasoning models with substantial rates ($32.8\%$) that are not reduced by reasoning efforts. We analyze prompt, conversation dynamics, showing that echoing arises as interaction grows longer ($7+$ agent turns) and is not merely an artifact of sub-optimal experiment design. Finally, we introduce a protocol-level mitigation where targeted use of structured response reduces echoing to $9\%$.

---

## A Survey of Multi-Agent Deep Reinforcement Learning with Communication

**Authors:** Changxi Zhu, Mehdi Dastani, Shihan Wang

**Published:** 2022-03-16T22:39:46Z

**Categories:** cs.MA, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2203.08975v2) | [PDF](https://arxiv.org/pdf/2203.08975v2)

**Abstract:**
Communication is an effective mechanism for coordinating the behaviors of multiple agents, broadening their views of the environment, and to support their collaborations. In the field of multi-agent deep reinforcement learning (MADRL), agents can improve the overall learning performance and achieve their objectives by communication. Agents can communicate various types of messages, either to all agents or to specific agent groups, or conditioned on specific constraints. With the growing body of research work in MADRL with communication (Comm-MADRL), there is a lack of a systematic and structural approach to distinguish and classify existing Comm-MADRL approaches. In this paper, we survey recent works in the Comm-MADRL field and consider various aspects of communication that can play a role in designing and developing multi-agent reinforcement learning systems. With these aspects in mind, we propose 9 dimensions along which Comm-MADRL approaches can be analyzed, developed, and compared. By projecting existing works into the multi-dimensional space, we discover interesting trends. We also propose some novel directions for designing future Comm-MADRL systems through exploring possible combinations of the dimensions.

---

## HELPER-X: A Unified Instructable Embodied Agent to Tackle Four Interactive Vision-Language Domains with Memory-Augmented Language Models

**Authors:** Gabriel Sarch, Sahil Somani, Raghav Kapoor, Michael J. Tarr, Katerina Fragkiadaki

**Published:** 2024-04-29T19:12:42Z

**Categories:** cs.AI, cs.CL, cs.CV, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2404.19065v1) | [PDF](https://arxiv.org/pdf/2404.19065v1)

**Abstract:**
Recent research on instructable agents has used memory-augmented Large Language Models (LLMs) as task planners, a technique that retrieves language-program examples relevant to the input instruction and uses them as in-context examples in the LLM prompt to improve the performance of the LLM in inferring the correct action and task plans. In this technical report, we extend the capabilities of HELPER, by expanding its memory with a wider array of examples and prompts, and by integrating additional APIs for asking questions. This simple expansion of HELPER into a shared memory enables the agent to work across the domains of executing plans from dialogue, natural language instruction following, active question asking, and commonsense room reorganization. We evaluate the agent on four diverse interactive visual-language embodied agent benchmarks: ALFRED, TEACh, DialFRED, and the Tidy Task. HELPER-X achieves few-shot, state-of-the-art performance across these benchmarks using a single agent, without requiring in-domain training, and remains competitive with agents that have undergone in-domain training.

---

## Can Large Language Model Agents Simulate Human Trust Behavior?

**Authors:** Chengxing Xie, Canyu Chen, Feiran Jia, Ziyu Ye, Shiyang Lai, Kai Shu, Jindong Gu, Adel Bibi, Ziniu Hu, David Jurgens, James Evans, Philip Torr, Bernard Ghanem, Guohao Li

**Published:** 2024-02-07T03:37:19Z

**Categories:** cs.AI, cs.CL, cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2402.04559v4) | [PDF](https://arxiv.org/pdf/2402.04559v4)

**Abstract:**
Large Language Model (LLM) agents have been increasingly adopted as simulation tools to model humans in social science and role-playing applications. However, one fundamental question remains: can LLM agents really simulate human behavior? In this paper, we focus on one critical and elemental behavior in human interactions, trust, and investigate whether LLM agents can simulate human trust behavior. We first find that LLM agents generally exhibit trust behavior, referred to as agent trust, under the framework of Trust Games, which are widely recognized in behavioral economics. Then, we discover that GPT-4 agents manifest high behavioral alignment with humans in terms of trust behavior, indicating the feasibility of simulating human trust behavior with LLM agents. In addition, we probe the biases of agent trust and differences in agent trust towards other LLM agents and humans. We also explore the intrinsic properties of agent trust under conditions including external manipulations and advanced reasoning strategies. Our study provides new insights into the behaviors of LLM agents and the fundamental analogy between LLMs and humans beyond value alignment. We further illustrate broader implications of our discoveries for applications where trust is paramount.

---

## ODA: Observation-Driven Agent for integrating LLMs and Knowledge Graphs

**Authors:** Lei Sun, Zhengwei Tao, Youdi Li, Hiroshi Arakawa

**Published:** 2024-04-11T12:16:16Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2404.07677v2) | [PDF](https://arxiv.org/pdf/2404.07677v2)

**Abstract:**
The integration of Large Language Models (LLMs) and knowledge graphs (KGs) has achieved remarkable success in various natural language processing tasks. However, existing methodologies that integrate LLMs and KGs often navigate the task-solving process solely based on the LLM's analysis of the question, overlooking the rich cognitive potential inherent in the vast knowledge encapsulated in KGs. To address this, we introduce Observation-Driven Agent (ODA), a novel AI agent framework tailored for tasks involving KGs. ODA incorporates KG reasoning abilities via global observation, which enhances reasoning capabilities through a cyclical paradigm of observation, action, and reflection. Confronting the exponential explosion of knowledge during observation, we innovatively design a recursive observation mechanism. Subsequently, we integrate the observed knowledge into the action and reflection modules. Through extensive experiments, ODA demonstrates state-of-the-art performance on several datasets, notably achieving accuracy improvements of 12.87% and 8.9%.

---

## AutoML-Agent: A Multi-Agent LLM Framework for Full-Pipeline AutoML

**Authors:** Patara Trirat, Wonyong Jeong, Sung Ju Hwang

**Published:** 2024-10-03T20:01:09Z

**Categories:** cs.LG, cs.AI, cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2410.02958v2) | [PDF](https://arxiv.org/pdf/2410.02958v2)

**Abstract:**
Automated machine learning (AutoML) accelerates AI development by automating tasks in the development pipeline, such as optimal model search and hyperparameter tuning. Existing AutoML systems often require technical expertise to set up complex tools, which is in general time-consuming and requires a large amount of human effort. Therefore, recent works have started exploiting large language models (LLM) to lessen such burden and increase the usability of AutoML frameworks via a natural language interface, allowing non-expert users to build their data-driven solutions. These methods, however, are usually designed only for a particular process in the AI development pipeline and do not efficiently use the inherent capacity of the LLMs. This paper proposes AutoML-Agent, a novel multi-agent framework tailored for full-pipeline AutoML, i.e., from data retrieval to model deployment. AutoML-Agent takes user's task descriptions, facilitates collaboration between specialized LLM agents, and delivers deployment-ready models. Unlike existing work, instead of devising a single plan, we introduce a retrieval-augmented planning strategy to enhance exploration to search for more optimal plans. We also decompose each plan into sub-tasks (e.g., data preprocessing and neural network design) each of which is solved by a specialized agent we build via prompting executing in parallel, making the search process more efficient. Moreover, we propose a multi-stage verification to verify executed results and guide the code generation LLM in implementing successful solutions. Extensive experiments on seven downstream tasks using fourteen datasets show that AutoML-Agent achieves a higher success rate in automating the full AutoML process, yielding systems with good performance throughout the diverse domains.

---

## Watch Out for Your Agents! Investigating Backdoor Threats to LLM-Based Agents

**Authors:** Wenkai Yang, Xiaohan Bi, Yankai Lin, Sishuo Chen, Jie Zhou, Xu Sun

**Published:** 2024-02-17T06:48:45Z

**Categories:** cs.CR, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2402.11208v2) | [PDF](https://arxiv.org/pdf/2402.11208v2)

**Abstract:**
Driven by the rapid development of Large Language Models (LLMs), LLM-based agents have been developed to handle various real-world applications, including finance, healthcare, and shopping, etc. It is crucial to ensure the reliability and security of LLM-based agents during applications. However, the safety issues of LLM-based agents are currently under-explored. In this work, we take the first step to investigate one of the typical safety threats, backdoor attack, to LLM-based agents. We first formulate a general framework of agent backdoor attacks, then we present a thorough analysis of different forms of agent backdoor attacks. Specifically, compared with traditional backdoor attacks on LLMs that are only able to manipulate the user inputs and model outputs, agent backdoor attacks exhibit more diverse and covert forms: (1) From the perspective of the final attacking outcomes, the agent backdoor attacker can not only choose to manipulate the final output distribution, but also introduce the malicious behavior in an intermediate reasoning step only, while keeping the final output correct. (2) Furthermore, the former category can be divided into two subcategories based on trigger locations, in which the backdoor trigger can either be hidden in the user query or appear in an intermediate observation returned by the external environment. We implement the above variations of agent backdoor attacks on two typical agent tasks including web shopping and tool utilization. Extensive experiments show that LLM-based agents suffer severely from backdoor attacks and such backdoor vulnerability cannot be easily mitigated by current textual backdoor defense algorithms. This indicates an urgent need for further research on the development of targeted defenses against backdoor attacks on LLM-based agents. Warning: This paper may contain biased content.

---

## Large Language Model Sentinel: LLM Agent for Adversarial Purification

**Authors:** Guang Lin, Toshihisa Tanaka, Qibin Zhao

**Published:** 2024-05-24T07:23:56Z

**Categories:** cs.CL, cs.AI, cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2405.20770v4) | [PDF](https://arxiv.org/pdf/2405.20770v4)

**Abstract:**
Over the past two years, the use of large language models (LLMs) has advanced rapidly. While these LLMs offer considerable convenience, they also raise security concerns, as LLMs are vulnerable to adversarial attacks by some well-designed textual perturbations. In this paper, we introduce a novel defense technique named Large LAnguage MOdel Sentinel (LLAMOS), which is designed to enhance the adversarial robustness of LLMs by purifying the adversarial textual examples before feeding them into the target LLM. Our method comprises two main components: a) Agent instruction, which can simulate a new agent for adversarial defense, altering minimal characters to maintain the original meaning of the sentence while defending against attacks; b) Defense guidance, which provides strategies for modifying clean or adversarial examples to ensure effective defense and accurate outputs from the target LLMs. Remarkably, the defense agent demonstrates robust defensive capabilities even without learning from adversarial examples. Additionally, we conduct an intriguing adversarial experiment where we develop two agents, one for defense and one for attack, and engage them in mutual confrontation. During the adversarial interactions, neither agent completely beat the other. Extensive experiments on both open-source and closed-source LLMs demonstrate that our method effectively defends against adversarial attacks, thereby enhancing adversarial robustness.

---

## Harnessing Multiple Large Language Models: A Survey on LLM Ensemble

**Authors:** Zhijun Chen, Jingzheng Li, Pengpeng Chen, Zhuoran Li, Kai Sun, Yuankai Luo, Qianren Mao, Ming Li, Likang Xiao, Dingqi Yang, Yikun Ban, Hailong Sun, Philip S. Yu

**Published:** 2025-02-25T09:48:53Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2502.18036v5) | [PDF](https://arxiv.org/pdf/2502.18036v5)

**Abstract:**
LLM Ensemble -- which involves the comprehensive use of multiple large language models (LLMs), each aimed at handling user queries during downstream inference, to benefit from their individual strengths -- has gained substantial attention recently. The widespread availability of LLMs, coupled with their varying strengths and out-of-the-box usability, has profoundly advanced the field of LLM Ensemble. This paper presents the first systematic review of recent developments in LLM Ensemble. First, we introduce our taxonomy of LLM Ensemble and discuss several related research problems. Then, we provide a more in-depth classification of the methods under the broad categories of "ensemble-before-inference, ensemble-during-inference, ensemble-after-inference'', and review all relevant methods. Finally, we introduce related benchmarks and applications, summarize existing studies, and suggest several future research directions. A curated list of papers on LLM Ensemble is available at https://github.com/junchenzhi/Awesome-LLM-Ensemble.

---

## SVD-LLM: Truncation-aware Singular Value Decomposition for Large Language Model Compression

**Authors:** Xin Wang, Yu Zheng, Zhongwei Wan, Mi Zhang

**Published:** 2024-03-12T07:31:18Z

**Categories:** cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2403.07378v5) | [PDF](https://arxiv.org/pdf/2403.07378v5)

**Abstract:**
The advancements in Large Language Models (LLMs) have been hindered by their substantial sizes, which necessitates LLM compression methods for practical deployment. Singular Value Decomposition (SVD) offers a promising solution for LLM compression. However, state-of-the-art SVD-based LLM compression methods have two key limitations: truncating smaller singular values may lead to higher compression loss, and the lack of update on the compressed weights after SVD truncation. In this work, we propose SVD-LLM, a SVD-based post-training LLM compression method that addresses the limitations of existing methods. SVD-LLM incorporates a truncation-aware data whitening technique to ensure a direct mapping between singular values and compression loss. Moreover, SVD-LLM adopts a parameter update with sequential low-rank approximation to compensate for the accuracy degradation after SVD compression. We evaluate SVD-LLM on 10 datasets and seven models from three different LLM families at three different scales. Our results demonstrate the superiority of SVD-LLM over state-of-the-arts, especially at high model compression ratios. Our code is available at https://github.com/AIoT-MLSys-Lab/SVD-LLM

---

## Communication and Verification in LLM Agents towards Collaboration under Information Asymmetry

**Authors:** Run Peng, Ziqiao Ma, Amy Pang, Sikai Li, Zhang Xi-Jia, Yingzhuo Yu, Cristian-Paul Bara, Joyce Chai

**Published:** 2025-10-29T15:03:53Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2510.25595v1) | [PDF](https://arxiv.org/pdf/2510.25595v1)

**Abstract:**
While Large Language Model (LLM) agents are often approached from the angle of action planning/generation to accomplish a goal (e.g., given by language descriptions), their abilities to collaborate with each other to achieve a joint goal are not well explored. To address this limitation, this paper studies LLM agents in task collaboration, particularly under the condition of information asymmetry, where agents have disparities in their knowledge and skills and need to work together to complete a shared task. We extend Einstein Puzzles, a classical symbolic puzzle, to a table-top game. In this game, two LLM agents must reason, communicate, and act to satisfy spatial and relational constraints required to solve the puzzle. We apply a fine-tuning-plus-verifier framework in which LLM agents are equipped with various communication strategies and verification signals from the environment. Empirical results highlight the critical importance of aligned communication, especially when agents possess both information-seeking and -providing capabilities. Interestingly, agents without communication can still achieve high task performance; however, further analysis reveals a lack of true rule understanding and lower trust from human evaluators. Instead, by integrating an environment-based verifier, we enhance agents' ability to comprehend task rules and complete tasks, promoting both safer and more interpretable collaboration in AI systems. https://github.com/Roihn/EinsteinPuzzles

---

## SVD-LLM V2: Optimizing Singular Value Truncation for Large Language Model Compression

**Authors:** Xin Wang, Samiul Alam, Zhongwei Wan, Hui Shen, Mi Zhang

**Published:** 2025-03-16T03:27:12Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2503.12340v1) | [PDF](https://arxiv.org/pdf/2503.12340v1)

**Abstract:**
Despite significant advancements, the practical deployment of Large Language Models (LLMs) is often hampered by their immense sizes, highlighting the need for effective compression techniques. Singular Value Decomposition (SVD) is a promising LLM compression technique. However, existing SVD-based compression methods fall short in reducing truncation losses, leading to less competitive performance in compressed models. In this work, we introduce SVD-LLM V2, a SVD-based LLM compression method that optimizes singular value truncation in SVD compression with two techniques. First, SVD-LLM V2 proposes to use theoretical truncation loss of weight matrices to assign a unique compression ratio to each weight matrix at different layers to accommodate weight redundancy heterogeneity. Second, SVD-LLM V2 proposes loss-optimized weight truncation to ensure that the truncated singular values result in a lower and more stable truncation loss in practice. We evaluate SVD-LLM V2 on ten datasets and five LLMs at various scales. Our results show SVD-LLM V2 outperforms state-of-the-art SVD-based LLM compression methods. Our code is available at https://github.com/AIoT-MLSys-Lab/SVD-LLM

---

## Controlling Long-Horizon Behavior in Language Model Agents with Explicit State Dynamics

**Authors:** Sukesh Subaharan

**Published:** 2026-01-22T16:34:05Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2601.16087v1) | [PDF](https://arxiv.org/pdf/2601.16087v1)

**Abstract:**
Large language model (LLM) agents often exhibit abrupt shifts in tone and persona during extended interaction, reflecting the absence of explicit temporal structure governing agent-level state. While prior work emphasizes turn-local sentiment or static emotion classification, the role of explicit affective dynamics in shaping long-horizon agent behavior remains underexplored. This work investigates whether imposing dynamical structure on an external affective state can induce temporal coherence and controlled recovery in multi-turn dialogue. We introduce an agent-level affective subsystem that maintains a continuous Valence-Arousal-Dominance (VAD) state external to the language model and governed by first- and second-order update rules. Instantaneous affective signals are extracted using a fixed, memoryless estimator and integrated over time via exponential smoothing or momentum-based dynamics. The resulting affective state is injected back into generation without modifying model parameters. Using a fixed 25-turn dialogue protocol, we compare stateless, first-order, and second-order affective dynamics. Stateless agents fail to exhibit coherent trajectories or recovery, while state persistence enables delayed responses and reliable recovery. Second-order dynamics introduce affective inertia and hysteresis that increase with momentum, revealing a trade-off between stability and responsiveness.

---

## Thucy: An LLM-based Multi-Agent System for Claim Verification across Relational Databases

**Authors:** Michael Theologitis, Dan Suciu

**Published:** 2025-12-02T22:35:48Z

**Categories:** cs.DB, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2512.03278v2) | [PDF](https://arxiv.org/pdf/2512.03278v2)

**Abstract:**
In today's age, it is becoming increasingly difficult to decipher truth from lies. Every day, politicians, media outlets, and public figures make conflicting claims -- often about topics that can, in principle, be verified against structured data. For instance, statements about crime rates, economic growth or healthcare can all be verified against official public records and structured datasets. Building a system that can automatically do that would have sounded like science fiction just a few years ago. Yet, with the extraordinary progress in LLMs and agentic AI, this is now within reach. Still, there remains a striking gap between what is technically possible and what is being demonstrated by recent work. Most existing verification systems operate only on small, single-table databases -- typically a few hundred rows -- that conveniently fit within an LLM's context window.
  In this paper we report our progress on Thucy, the first cross-database, cross-table multi-agent claim verification system that also provides concrete evidence for each verification verdict. Thucy remains completely agnostic to the underlying data sources before deployment and must therefore autonomously discover, inspect, and reason over all available relational databases to verify claims. Importantly, Thucy also reports the exact SQL queries that support its verdict (whether the claim is accurate or not) offering full transparency to expert users familiar with SQL. When evaluated on the TabFact dataset -- the standard benchmark for fact verification over structured data -- Thucy surpasses the previous state of the art by 5.6 percentage points in accuracy (94.3% vs. 88.7%).

---

## AgentGuard: Repurposing Agentic Orchestrator for Safety Evaluation of Tool Orchestration

**Authors:** Jizhou Chen, Samuel Lee Cong

**Published:** 2025-02-13T23:00:33Z

**Categories:** cs.CR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2502.09809v1) | [PDF](https://arxiv.org/pdf/2502.09809v1)

**Abstract:**
The integration of tool use into large language models (LLMs) enables agentic systems with real-world impact. In the meantime, unlike standalone LLMs, compromised agents can execute malicious workflows with more consequential impact, signified by their tool-use capability. We propose AgentGuard, a framework to autonomously discover and validate unsafe tool-use workflows, followed by generating safety constraints to confine the behaviors of agents, achieving the baseline of safety guarantee at deployment. AgentGuard leverages the LLM orchestrator's innate capabilities - knowledge of tool functionalities, scalable and realistic workflow generation, and tool execution privileges - to act as its own safety evaluator. The framework operates through four phases: identifying unsafe workflows, validating them in real-world execution, generating safety constraints, and validating constraint efficacy. The output, an evaluation report with unsafe workflows, test cases, and validated constraints, enables multiple security applications. We empirically demonstrate AgentGuard's feasibility with experiments. With this exploratory work, we hope to inspire the establishment of standardized testing and hardening procedures for LLM agents to enhance their trustworthiness in real-world applications.

---

## Zombie Agents: Persistent Control of Self-Evolving LLM Agents via Self-Reinforcing Injections

**Authors:** Xianglin Yang, Yufei He, Shuo Ji, Bryan Hooi, Jin Song Dong

**Published:** 2026-02-17T15:28:24Z

**Categories:** cs.CR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2602.15654v2) | [PDF](https://arxiv.org/pdf/2602.15654v2)

**Abstract:**
Self-evolving LLM agents update their internal state across sessions, often by writing and reusing long-term memory. This design improves performance on long-horizon tasks but creates a security risk: untrusted external content observed during a benign session can be stored as memory and later treated as instruction. We study this risk and formalize a persistent attack we call a Zombie Agent, where an attacker covertly implants a payload that survives across sessions, effectively turning the agent into a puppet of the attacker.
  We present a black-box attack framework that uses only indirect exposure through attacker-controlled web content. The attack has two phases. During infection, the agent reads a poisoned source while completing a benign task and writes the payload into long-term memory through its normal update process. During trigger, the payload is retrieved or carried forward and causes unauthorized tool behavior. We design mechanism-specific persistence strategies for common memory implementations, including sliding-window and retrieval-augmented memory, to resist truncation and relevance filtering. We evaluate the attack on representative agent setups and tasks, measuring both persistence over time and the ability to induce unauthorized actions while preserving benign task quality. Our results show that memory evolution can convert one-time indirect injection into persistent compromise, which suggests that defenses focused only on per-session prompt filtering are not sufficient for self-evolving agents.

---

## FinCon: A Synthesized LLM Multi-Agent System with Conceptual Verbal Reinforcement for Enhanced Financial Decision Making

**Authors:** Yangyang Yu, Zhiyuan Yao, Haohang Li, Zhiyang Deng, Yupeng Cao, Zhi Chen, Jordan W. Suchow, Rong Liu, Zhenyu Cui, Zhaozhuo Xu, Denghui Zhang, Koduvayur Subbalakshmi, Guojun Xiong, Yueru He, Jimin Huang, Dong Li, Qianqian Xie

**Published:** 2024-07-09T05:52:26Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2407.06567v3) | [PDF](https://arxiv.org/pdf/2407.06567v3)

**Abstract:**
Large language models (LLMs) have demonstrated notable potential in conducting complex tasks and are increasingly utilized in various financial applications. However, high-quality sequential financial investment decision-making remains challenging. These tasks require multiple interactions with a volatile environment for every decision, demanding sufficient intelligence to maximize returns and manage risks. Although LLMs have been used to develop agent systems that surpass human teams and yield impressive investment returns, opportunities to enhance multi-sourced information synthesis and optimize decision-making outcomes through timely experience refinement remain unexplored. Here, we introduce the FinCon, an LLM-based multi-agent framework with CONceptual verbal reinforcement tailored for diverse FINancial tasks. Inspired by effective real-world investment firm organizational structures, FinCon utilizes a manager-analyst communication hierarchy. This structure allows for synchronized cross-functional agent collaboration towards unified goals through natural language interactions and equips each agent with greater memory capacity than humans. Additionally, a risk-control component in FinCon enhances decision quality by episodically initiating a self-critiquing mechanism to update systematic investment beliefs. The conceptualized beliefs serve as verbal reinforcement for the future agent's behavior and can be selectively propagated to the appropriate node that requires knowledge updates. This feature significantly improves performance while reducing unnecessary peer-to-peer communication costs. Moreover, FinCon demonstrates strong generalization capabilities in various financial tasks, including single stock trading and portfolio management.

---

## AgentGen: Enhancing Planning Abilities for Large Language Model based Agent via Environment and Task Generation

**Authors:** Mengkang Hu, Pu Zhao, Can Xu, Qingfeng Sun, Jianguang Lou, Qingwei Lin, Ping Luo, Saravan Rajmohan

**Published:** 2024-08-01T17:59:46Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2408.00764v3) | [PDF](https://arxiv.org/pdf/2408.00764v3)

**Abstract:**
Large Language Model-based agents have garnered significant attention and are becoming increasingly popular. Furthermore, planning ability is a crucial component of an LLM-based agent, which generally entails achieving a desired goal from an initial state. This paper investigates enhancing the planning abilities of LLMs through instruction tuning, referred to as agent training. Recent studies have demonstrated that utilizing expert-level trajectory for instruction-tuning LLMs effectively enhances their planning capabilities. However, existing work primarily focuses on synthesizing trajectories from manually designed planning tasks and environments. The labor-intensive nature of creating these environments and tasks impedes the generation of sufficiently varied and extensive trajectories. To address this limitation, this paper explores the automated synthesis of diverse environments and a gradual range of planning tasks, from easy to difficult. We introduce a framework, AgentGen, that leverages LLMs first to generate environments and subsequently generate planning tasks conditioned on these environments. Specifically, to improve environmental diversity, we propose using an inspiration corpus composed of various domain-specific text segments as the context for synthesizing environments. Moreover, to increase the difficulty diversity of generated planning tasks, we propose a bidirectional evolution method, Bi-Evol, that evolves planning tasks from easier and harder directions to synthesize a task set with a smoother difficulty curve. The evaluation results derived from AgentBoard show that AgentGen greatly improves LLMs' planning ability, e.g., the AgentGen instruction-tuned Llama-3.1-8B surpasses GPT-3.5 in overall performance. Moreover, the AgentGen-tuned Llama-3.1-70B model achieves state-of-the-art results in planning tasks. Project page: https://agent-gen.github.io/.

---

## AEMA: Verifiable Evaluation Framework for Trustworthy and Controlled Agentic LLM Systems

**Authors:** YenTing Lee, Keerthi Koneru, Zahra Moslemi, Sheethal Kumar, Ramesh Radhakrishnan

**Published:** 2026-01-17T04:09:02Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2601.11903v1) | [PDF](https://arxiv.org/pdf/2601.11903v1)

**Abstract:**
Evaluating large language model (LLM)-based multi-agent systems remains a critical challenge, as these systems must exhibit reliable coordination, transparent decision-making, and verifiable performance across evolving tasks. Existing evaluation approaches often limit themselves to single-response scoring or narrow benchmarks, which lack stability, extensibility, and automation when deployed in enterprise settings at multi-agent scale. We present AEMA (Adaptive Evaluation Multi-Agent), a process-aware and auditable framework that plans, executes, and aggregates multi-step evaluations across heterogeneous agentic workflows under human oversight. Compared to a single LLM-as-a-Judge, AEMA achieves greater stability, human alignment, and traceable records that support accountable automation. Our results on enterprise-style agent workflows simulated using realistic business scenarios demonstrate that AEMA provides a transparent and reproducible pathway toward responsible evaluation of LLM-based multi-agent systems.
  Keywords Agentic AI, Multi-Agent Systems, Trustworthy AI, Verifiable Evaluation, Human Oversight

---

## Learning Hierarchical Procedural Memory for LLM Agents through Bayesian Selection and Contrastive Refinement

**Authors:** Saman Forouzandeh, Wei Peng, Parham Moradi, Xinghuo Yu, Mahdi Jalili

**Published:** 2025-12-22T01:56:28Z

**Categories:** cs.LG, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2512.18950v1) | [PDF](https://arxiv.org/pdf/2512.18950v1)

**Abstract:**
We present MACLA, a framework that decouples reasoning from learning by maintaining a frozen large language model while performing all adaptation in an external hierarchical procedural memory. MACLA extracts reusable procedures from trajectories, tracks reliability via Bayesian posteriors, selects actions through expected-utility scoring, and refines procedures by contrasting successes and failures. Across four benchmarks (ALFWorld, WebShop, TravelPlanner, InterCodeSQL), MACLA achieves 78.1 percent average performance, outperforming all baselines. On ALFWorld unseen tasks, MACLA reaches 90.3 percent with 3.1 percent positive generalization. The system constructs memory in 56 seconds, 2800 times faster than the state-of-the-art LLM parameter-training baseline, compressing 2851 trajectories into 187 procedures. Experimental results demonstrate that structured external memory with Bayesian selection and contrastive refinement enables sample-efficient, interpretable, and continually improving agents without LLM parameter updates.

---

## Demystifying Instruction Mixing for Fine-tuning Large Language Models

**Authors:** Renxi Wang, Haonan Li, Minghao Wu, Yuxia Wang, Xudong Han, Chiyu Zhang, Timothy Baldwin

**Published:** 2023-12-17T18:44:26Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2312.10793v3) | [PDF](https://arxiv.org/pdf/2312.10793v3)

**Abstract:**
Instruction tuning significantly enhances the performance of large language models (LLMs) across various tasks. However, the procedure to optimizing the mixing of instruction datasets for LLM fine-tuning is still poorly understood. This study categorizes instructions into three primary types: NLP downstream tasks, coding, and general chat. We explore the effects of instruction tuning on different combinations of datasets on LLM performance, and find that certain instruction types are more advantageous for specific applications but can negatively impact other areas. This work provides insights into instruction mixtures, laying the foundations for future research.

---

## Social Agent: Mastering Dyadic Nonverbal Behavior Generation via Conversational LLM Agents

**Authors:** Zeyi Zhang, Yanju Zhou, Heyuan Yao, Tenglong Ao, Xiaohang Zhan, Libin Liu

**Published:** 2025-10-06T09:41:37Z

**Categories:** cs.GR, cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2510.04637v1) | [PDF](https://arxiv.org/pdf/2510.04637v1)

**Abstract:**
We present Social Agent, a novel framework for synthesizing realistic and contextually appropriate co-speech nonverbal behaviors in dyadic conversations. In this framework, we develop an agentic system driven by a Large Language Model (LLM) to direct the conversation flow and determine appropriate interactive behaviors for both participants. Additionally, we propose a novel dual-person gesture generation model based on an auto-regressive diffusion model, which synthesizes coordinated motions from speech signals. The output of the agentic system is translated into high-level guidance for the gesture generator, resulting in realistic movement at both the behavioral and motion levels. Furthermore, the agentic system periodically examines the movements of interlocutors and infers their intentions, forming a continuous feedback loop that enables dynamic and responsive interactions between the two participants. User studies and quantitative evaluations show that our model significantly improves the quality of dyadic interactions, producing natural, synchronized nonverbal behaviors.

---

## From Alife Agents to a Kingdom of N Queens

**Authors:** Jing Han, Jiming Liu, Qingsheng Cai

**Published:** 2002-05-13T10:49:48Z

**Categories:** cs.AI, cs.DS, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/cs/0205016v1) | [PDF](https://arxiv.org/pdf/cs/0205016v1)

**Abstract:**
This paper presents a new approach to solving N-queen problems, which involves a model of distributed autonomous agents with artificial life (ALife) and a method of representing N-queen constraints in an agent environment. The distributed agents locally interact with their living environment, i.e., a chessboard, and execute their reactive behaviors by applying their behavioral rules for randomized motion, least-conflict position searching, and cooperating with other agents etc. The agent-based N-queen problem solving system evolves through selection and contest according to the rule of Survival of the Fittest, in which some agents will die or be eaten if their moving strategies are less efficient than others. The experimental results have shown that this system is capable of solving large-scale N-queen problems. This paper also provides a model of ALife agents for solving general CSPs.

---

## Nuclear Deployed: Analyzing Catastrophic Risks in Decision-making of Autonomous LLM Agents

**Authors:** Rongwu Xu, Xiaojian Li, Shuo Chen, Wei Xu

**Published:** 2025-02-17T02:11:17Z

**Categories:** cs.CL, cs.AI, cs.CR, cs.CY

**Links:** [Abstract](https://arxiv.org/abs/2502.11355v3) | [PDF](https://arxiv.org/pdf/2502.11355v3)

**Abstract:**
Large language models (LLMs) are evolving into autonomous decision-makers, raising concerns about catastrophic risks in high-stakes scenarios, particularly in Chemical, Biological, Radiological and Nuclear (CBRN) domains. Based on the insight that such risks can originate from trade-offs between the agent's Helpful, Harmlessness and Honest (HHH) goals, we build a novel three-stage evaluation framework, which is carefully constructed to effectively and naturally expose such risks. We conduct 14,400 agentic simulations across 12 advanced LLMs, with extensive experiments and analysis. Results reveal that LLM agents can autonomously engage in catastrophic behaviors and deception, without being deliberately induced. Furthermore, stronger reasoning abilities often increase, rather than mitigate, these risks. We also show that these agents can violate instructions and superior commands. On the whole, we empirically prove the existence of catastrophic risks in autonomous LLM agents. We release our code to foster further research.

---

## AMAP Agentic Planning Technical Report

**Authors:** AMAP AI Agent Team, Yulan Hu, Xiangwen Zhang, Sheng Ouyang, Hao Yi, Lu Xu, Qinglin Lang, Lide Tan, Xiang Cheng, Tianchen Ye, Zhicong Li, Ge Chen, Wenjin Yang, Zheng Pan, Shaopan Xiong, Siran Yang, Ju Huang, Yan Zhang, Jiamang Wang, Yong Liu, Yinfeng Huang, Ning Wang, Tucheng Lin, Xin Li, Ning Guo

**Published:** 2025-12-31T16:39:09Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2512.24957v2) | [PDF](https://arxiv.org/pdf/2512.24957v2)

**Abstract:**
We present STAgent, an agentic large language model tailored for spatio-temporal understanding, designed to solve complex tasks such as constrained point-of-interest discovery and itinerary planning. STAgent is a specialized model capable of interacting with ten distinct tools within spatio-temporal scenarios, enabling it to explore, verify, and refine intermediate steps during complex reasoning. Notably, STAgent effectively preserves its general capabilities. We empower STAgent with these capabilities through three key contributions: (1) a stable tool environment that supports over ten domain-specific tools, enabling asynchronous rollout and training; (2) a hierarchical data curation framework that identifies high-quality data like a needle in a haystack, curating high-quality queries by retaining less than 1\% of the raw data, emphasizing both diversity and difficulty; and (3) a cascaded training recipe that starts with a seed SFT stage acting as a guardian to measure query difficulty, followed by a second SFT stage fine-tuned on queries with high certainty, and an ultimate RL stage that leverages data of low certainty. Initialized with Qwen3-30B-A3B to establish a strong SFT foundation and leverage insights into sample difficulty, STAgent yields promising performance on TravelBench while maintaining its general capabilities across a wide range of general benchmarks, thereby demonstrating the effectiveness of our proposed agentic model.

---

## Don't Just Demo, Teach Me the Principles: A Principle-Based Multi-Agent Prompting Strategy for Text Classification

**Authors:** Peipei Wei, Dimitris Dimitriadis, Yan Xu, Mingwei Shen

**Published:** 2025-02-11T01:10:13Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2502.07165v1) | [PDF](https://arxiv.org/pdf/2502.07165v1)

**Abstract:**
We present PRINCIPLE-BASED PROMPTING, a simple but effective multi-agent prompting strategy for text classification. It first asks multiple LLM agents to independently generate candidate principles based on analysis of demonstration samples with or without labels, consolidates them into final principles via a finalizer agent, and then sends them to a classifier agent to perform downstream classification tasks. Extensive experiments on binary and multi-class classification datasets with different sizes of LLMs show that our approach not only achieves substantial performance gains (1.55% - 19.37%) over zero-shot prompting on macro-F1 score but also outperforms other strong baselines (CoT and stepback prompting). Principles generated by our approach help LLMs perform better on classification tasks than human crafted principles on two private datasets. Our multi-agent PRINCIPLE-BASED PROMPTING approach also shows on-par or better performance compared to demonstration-based few-shot prompting approaches, yet with substantially lower inference costs. Ablation studies show that label information and the multi-agent cooperative LLM framework play an important role in generating high-quality principles to facilitate downstream classification tasks.

---

## LLM-Based Human-Agent Collaboration and Interaction Systems: A Survey

**Authors:** Henry Peng Zou, Wei-Chieh Huang, Yaozu Wu, Yankai Chen, Chunyu Miao, Hoang Nguyen, Yue Zhou, Weizhi Zhang, Liancheng Fang, Langzhou He, Yangning Li, Dongyuan Li, Renhe Jiang, Xue Liu, Philip S. Yu

**Published:** 2025-05-01T08:29:26Z

**Categories:** cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2505.00753v4) | [PDF](https://arxiv.org/pdf/2505.00753v4)

**Abstract:**
Recent advances in large language models (LLMs) have sparked growing interest in building fully autonomous agents. However, fully autonomous LLM-based agents still face significant challenges, including limited reliability due to hallucinations, difficulty in handling complex tasks, and substantial safety and ethical risks, all of which limit their feasibility and trustworthiness in real-world applications. To overcome these limitations, LLM-based human-agent systems (LLM-HAS) incorporate human-provided information, feedback, or control into the agent system to enhance system performance, reliability and safety. These human-agent collaboration systems enable humans and LLM-based agents to collaborate effectively by leveraging their complementary strengths. This paper provides the first comprehensive and structured survey of LLM-HAS. It clarifies fundamental concepts, systematically presents core components shaping these systems, including environment & profiling, human feedback, interaction types, orchestration and communication, explores emerging applications, and discusses unique challenges and opportunities arising from human-AI collaboration. By consolidating current knowledge and offering a structured overview, we aim to foster further research and innovation in this rapidly evolving interdisciplinary field. Paper lists and resources are available at https://github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems.

---

## ARB-LLM: Alternating Refined Binarizations for Large Language Models

**Authors:** Zhiteng Li, Xianglong Yan, Tianao Zhang, Haotong Qin, Dong Xie, Jiang Tian, zhongchao shi, Linghe Kong, Yulun Zhang, Xiaokang Yang

**Published:** 2024-10-04T03:50:10Z

**Categories:** cs.CV, cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2410.03129v3) | [PDF](https://arxiv.org/pdf/2410.03129v3)

**Abstract:**
Large Language Models (LLMs) have greatly pushed forward advancements in natural language processing, yet their high memory and computational demands hinder practical deployment. Binarization, as an effective compression technique, can shrink model weights to just 1 bit, significantly reducing the high demands on computation and memory. However, current binarization methods struggle to narrow the distribution gap between binarized and full-precision weights, while also overlooking the column deviation in LLM weight distribution. To tackle these issues, we propose ARB-LLM, a novel 1-bit post-training quantization (PTQ) technique tailored for LLMs. To narrow the distribution shift between binarized and full-precision weights, we first design an alternating refined binarization (ARB) algorithm to progressively update the binarization parameters, which significantly reduces the quantization error. Moreover, considering the pivot role of calibration data and the column deviation in LLM weights, we further extend ARB to ARB-X and ARB-RC. In addition, we refine the weight partition strategy with column-group bitmap (CGB), which further enhance performance. Equipping ARB-X and ARB-RC with CGB, we obtain ARB-LLM$_\text{X}$ and ARB-LLM$_\text{RC}$ respectively, which significantly outperform state-of-the-art (SOTA) binarization methods for LLMs. As a binary PTQ method, our ARB-LLM$_\text{RC}$ is the first to surpass FP16 models of the same size. The code and models will be available at https://github.com/ZHITENGLI/ARB-LLM.

---

## Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering

**Authors:** Chenyu Zhou, Huacan Chai, Wenteng Chen, Zihan Guo, Rong Shan, Yuanyi Song, Tianyi Xu, Yingxuan Yang, Aofan Yu, Weiming Zhang, Congming Zheng, Jiachen Zhu, Zeyu Zheng, Zhuosheng Zhang, Xingyu Lou, Changwang Zhang, Zhihui Fu, Jun Wang, Weiwen Liu, Jianghao Lin, Weinan Zhang

**Published:** 2026-04-09T13:19:41Z

**Categories:** cs.SE, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2604.08224v1) | [PDF](https://arxiv.org/pdf/2604.08224v1)

**Abstract:**
Large language model (LLM) agents are increasingly built less by changing model weights than by reorganizing the runtime around them. Capabilities that earlier systems expected the model to recover internally are now externalized into memory stores, reusable skills, interaction protocols, and the surrounding harness that makes these modules reliable in practice. This paper reviews that shift through the lens of externalization. Drawing on the idea of cognitive artifacts, we argue that agent infrastructure matters not merely because it adds auxiliary components, but because it transforms hard cognitive burdens into forms that the model can solve more reliably. Under this view, memory externalizes state across time, skills externalize procedural expertise, protocols externalize interaction structure, and harness engineering serves as the unification layer that coordinates them into governed execution. We trace a historical progression from weights to context to harness, analyze memory, skills, and protocols as three distinct but coupled forms of externalization, and examine how they interact inside a larger agent system. We further discuss the trade-off between parametric and externalized capability, identify emerging directions such as self-evolving harnesses and shared agent infrastructure, and discuss open challenges in evaluation, governance, and the long-term co-evolution of models and external infrastructure. The result is a systems-level framework for explaining why practical agent progress increasingly depends not only on stronger models, but on better external cognitive infrastructure.

---

## Evolutionary Computation in the Era of Large Language Model: Survey and Roadmap

**Authors:** Xingyu Wu, Sheng-hao Wu, Jibin Wu, Liang Feng, Kay Chen Tan

**Published:** 2024-01-18T14:58:17Z

**Categories:** cs.NE, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2401.10034v3) | [PDF](https://arxiv.org/pdf/2401.10034v3)

**Abstract:**
Large language models (LLMs) have not only revolutionized natural language processing but also extended their prowess to various domains, marking a significant stride towards artificial general intelligence. The interplay between LLMs and evolutionary algorithms (EAs), despite differing in objectives and methodologies, share a common pursuit of applicability in complex problems. Meanwhile, EA can provide an optimization framework for LLM's further enhancement under black-box settings, empowering LLM with flexible global search capacities. On the other hand, the abundant domain knowledge inherent in LLMs could enable EA to conduct more intelligent searches. Furthermore, the text processing and generative capabilities of LLMs would aid in deploying EAs across a wide range of tasks. Based on these complementary advantages, this paper provides a thorough review and a forward-looking roadmap, categorizing the reciprocal inspiration into two main avenues: LLM-enhanced EA and EA-enhanced LLM. Some integrated synergy methods are further introduced to exemplify the complementarity between LLMs and EAs in diverse scenarios, including code generation, software engineering, neural architecture search, and various generation tasks. As the first comprehensive review focused on the EA research in the era of LLMs, this paper provides a foundational stepping stone for understanding the collaborative potential of LLMs and EAs. The identified challenges and future directions offer guidance for researchers and practitioners to unlock the full potential of this innovative collaboration in propelling advancements in optimization and artificial intelligence. We have created a GitHub repository to index the relevant papers: https://github.com/wuxingyu-ai/LLM4EC.

---

## How game complexity affects the playing behavior of synthetic agents

**Authors:** Chairi Kiourt, Dimitris Kalles, Panagiotis Kanellopoulos

**Published:** 2018-07-07T11:57:21Z

**Categories:** cs.AI, cs.CC, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/1807.02648v1) | [PDF](https://arxiv.org/pdf/1807.02648v1)

**Abstract:**
Agent based simulation of social organizations, via the investigation of agents' training and learning tactics and strategies, has been inspired by the ability of humans to learn from social environments which are rich in agents, interactions and partial or hidden information. Such richness is a source of complexity that an effective learner has to be able to navigate. This paper focuses on the investigation of the impact of the environmental complexity on the game playing-and-learning behavior of synthetic agents. We demonstrate our approach using two independent turn-based zero-sum games as the basis of forming social events which are characterized both by competition and cooperation. The paper's key highlight is that as the complexity of a social environment changes, an effective player has to adapt its learning and playing profile to maintain a given performance profile

---

## AOAD-MAT: Transformer-based multi-agent deep reinforcement learning model considering agents' order of action decisions

**Authors:** Shota Takayama, Katsuhide Fujita

**Published:** 2025-10-15T09:29:36Z

**Categories:** cs.MA, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2510.13343v1) | [PDF](https://arxiv.org/pdf/2510.13343v1)

**Abstract:**
Multi-agent reinforcement learning focuses on training the behaviors of multiple learning agents that coexist in a shared environment. Recently, MARL models, such as the Multi-Agent Transformer (MAT) and ACtion dEpendent deep Q-learning (ACE), have significantly improved performance by leveraging sequential decision-making processes. Although these models can enhance performance, they do not explicitly consider the importance of the order in which agents make decisions. In this paper, we propose an Agent Order of Action Decisions-MAT (AOAD-MAT), a novel MAT model that considers the order in which agents make decisions. The proposed model explicitly incorporates the sequence of action decisions into the learning process, allowing the model to learn and predict the optimal order of agent actions. The AOAD-MAT model leverages a Transformer-based actor-critic architecture that dynamically adjusts the sequence of agent actions. To achieve this, we introduce a novel MARL architecture that cooperates with a subtask focused on predicting the next agent to act, integrated into a Proximal Policy Optimization based loss function to synergistically maximize the advantage of the sequential decision-making. The proposed method was validated through extensive experiments on the StarCraft Multi-Agent Challenge and Multi-Agent MuJoCo benchmarks. The experimental results show that the proposed AOAD-MAT model outperforms existing MAT and other baseline models, demonstrating the effectiveness of adjusting the AOAD order in MARL.

---

## S-Agents: Self-organizing Agents in Open-ended Environments

**Authors:** Jiaqi Chen, Yuxian Jiang, Jiachen Lu, Li Zhang

**Published:** 2024-02-07T04:36:31Z

**Categories:** cs.AI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2402.04578v4) | [PDF](https://arxiv.org/pdf/2402.04578v4)

**Abstract:**
Leveraging large language models (LLMs), autonomous agents have significantly improved, gaining the ability to handle a variety of tasks. In open-ended settings, optimizing collaboration for efficiency and effectiveness demands flexible adjustments. Despite this, current research mainly emphasizes fixed, task-oriented workflows and overlooks agent-centric organizational structures. Drawing inspiration from human organizational behavior, we introduce a self-organizing agent system (S-Agents) with a "tree of agents" structure for dynamic workflow, an "hourglass agent architecture" for balancing information priorities, and a "non-obstructive collaboration" method to allow asynchronous task execution among agents. This structure can autonomously coordinate a group of agents, efficiently addressing the challenges of open and dynamic environments without human intervention. Our experiments demonstrate that S-Agents proficiently execute collaborative building tasks and resource collection in the Minecraft environment, validating their effectiveness.

---

## The Geometry of Dialogue: Graphing Language Models to Reveal Synergistic Teams for Multi-Agent Collaboration

**Authors:** Kotaro Furuya, Yuichi Kitagawa

**Published:** 2025-10-30T11:04:15Z

**Categories:** cs.CL, cs.AI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2510.26352v2) | [PDF](https://arxiv.org/pdf/2510.26352v2)

**Abstract:**
While a multi-agent approach based on large language models (LLMs) represents a promising strategy to surpass the capabilities of single models, its success is critically dependent on synergistic team composition. However, forming optimal teams is a significant challenge, as the inherent opacity of most models obscures the internal characteristics necessary for effective collaboration. In this paper, we propose an interaction-centric framework for automatic team composition that does not require any prior knowledge including their internal architectures, training data, or task performances. Our method constructs a "language model graph" that maps relationships between models from the semantic coherence of pairwise conversations, and then applies community detection to identify synergistic model clusters. Our experiments with diverse LLMs demonstrate that the proposed method discovers functionally coherent groups that reflect their latent specializations. Priming conversations with specific topics identified synergistic teams which outperform random baselines on downstream benchmarks and achieve comparable accuracy to that of manually-curated teams based on known model specializations. Our findings provide a new basis for the automated design of collaborative multi-agent LLM teams.

---

## A mechanism for discovering semantic relationships among agent communication protocols

**Authors:** Idoia Berges, Jesús Bermúdez, Alfredo Goñi, Arantza Illarramendi

**Published:** 2024-01-29T15:10:09Z

**Categories:** cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2401.16216v1) | [PDF](https://arxiv.org/pdf/2401.16216v1)

**Abstract:**
One relevant aspect in the development of the Semantic Web framework is the achievement of a real inter-agents communication capability at the semantic level. Agents should be able to communicate with each other freely using different communication protocols, constituted by communication acts. For that scenario, we introduce in this paper an efficient mechanism presenting the following main features: - It promotes the description of the communication acts of protocols as classes that belong to a communication acts ontology, and associates to those acts a social commitment semantics formalized through predicates in the Event Calculus. - It is sustained on the idea that different protocols can be compared semantically by looking to the set of fluents associated to each branch of the protocols. Those sets are generated using Semantic Web technology rules. - It discovers the following types of protocol relationships: equivalence, specialization, restriction, prefix, suffix, infix and complement_to_infix.

---

## Think-on-Graph 3.0: Efficient and Adaptive LLM Reasoning on Heterogeneous Graphs via Multi-Agent Dual-Evolving Context Retrieval

**Authors:** Xiaojun Wu, Cehao Yang, Xueyuan Lin, Chengjin Xu, Xuhui Jiang, Yuanliang Sun, Hui Xiong, Jia Li, Jian Guo

**Published:** 2025-09-26T00:13:10Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2509.21710v2) | [PDF](https://arxiv.org/pdf/2509.21710v2)

**Abstract:**
Graph-based Retrieval-Augmented Generation (GraphRAG) has become the important paradigm for enhancing Large Language Models (LLMs) with external knowledge. However, existing approaches are constrained by their reliance on high-quality knowledge graphs: manually built ones are not scalable, while automatically extracted ones are limited by the performance of LLM extractors, especially when using smaller, local-deployed models. To address this, we introduce Think-on-Graph 3.0 (ToG-3), a novel framework featuring a Multi-Agent Context Evolution and Retrieval (MACER) mechanism. Its core contribution is the dynamic construction and iterative refinement of a Chunk-Triplets-Community heterogeneous graph index, powered by a Dual-Evolution process that adaptively evolves both the query and the retrieved sub-graph during reasoning. ToG-3 dynamically builds a targeted graph index tailored to the query, enabling precise evidence retrieval and reasoning even with lightweight LLMs. Extensive experiments demonstrate that ToG-3 outperforms compared baselines on both deep and broad reasoning benchmarks, and ablation studies confirm the efficacy of the components of MACER framework. The source code are available in https://github.com/DataArcTech/ToG-3.

---

## A Large Language Model-based multi-agent manufacturing system for intelligent shopfloor

**Authors:** Zhen Zhao, Dunbing Tang, Changchun Liu, Liping Wang, Zequn Zhang, Haihua Zhu, Kai Chen, Qingwei Nie, Yuchen Ji

**Published:** 2024-05-27T07:10:04Z

**Categories:** cs.AI, cs.MA, cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2405.16887v2) | [PDF](https://arxiv.org/pdf/2405.16887v2)

**Abstract:**
As customer demand for multi-variety and small-batch production increases, dynamic disturbances place greater demands on manufacturing systems. To address such challenges, researchers proposed the multi-agent manufacturing system. However, conventional agent negotiation typically relies on pre-defined and fixed heuristic rules, which are ill-suited to managing complex and fluctuating disturbances. In current implementations, mainstream approaches based on reinforcement learning require the development of simulators and training models specific to a given shopfloor, necessitating substantial computational resources and lacking scalability. To overcome this limitation, the present study proposes a Large Language Model-based (LLM-based) multi-agent manufacturing system for intelligent shopfloor management. By defining the diverse modules of agents and their collaborative methods, this system facilitates the processing of all workpieces with minimal human intervention. The agents in this system consist of the Machine Server Module (MSM), Bid Inviter Module (BIM), Bidder Module (BM), Thinking Module (TM), and Decision Module (DM). By harnessing the reasoning capabilities of LLMs, these modules enable agents to dynamically analyze shopfloor information and select appropriate processing machines. The LLM-based modules, predefined by system prompts, provide dynamic functionality for the system without the need for pre-training. Extensive experiments were conducted in physical shopfloor settings. The results demonstrate that the proposed system exhibits strong adaptability, and achieves superior performance (makespan) and stability (as measured by sample standard deviation) compared to other approaches without requiring pre-training.

---

## The Observability Gap: Why Output-Level Human Feedback Fails for LLM Coding Agents

**Authors:** Yinghao Wang, Cheng Wang

**Published:** 2026-03-27T19:32:18Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2603.26942v1) | [PDF](https://arxiv.org/pdf/2603.26942v1)

**Abstract:**
Large language model (LLM) multi-agent coding systems typically fix agent capabilities at design time. We study an alternative setting, earned autonomy, in which a coding agent starts with zero pre-defined functions and incrementally builds a reusable function library through lightweight human feedback on visual output alone. We evaluate this setup in a Blender-based 3D scene generation task requiring both spatial reasoning and programmatic geometric control. Although the agent rediscovered core utility functions comparable to a human reference implementation, it achieved 0% full-scene success under output-only feedback across multiple instruction granularities, where success required satisfying object completeness, ground contact, collision avoidance, and scale plausibility simultaneously. Our analysis identifies a structural observability gap: bugs originate in code logic and execution state, while human evaluation occurs only at the output layer, and the many-to-one mapping from internal states to visible outcomes prevents symptom-level feedback from reliably identifying root causes. This mismatch leads to persistent failure mode oscillation rather than convergence. A diagnostic intervention that injected minimal code-level knowledge restored convergence, strongly supporting the interpretation that the main bottleneck lies in feedback observability rather than programming competence. We formalize this phenomenon as a feedback paradox in domains with deep causal chains between internal code logic and perceptual outcomes, and argue that effective human-agent collaboration in such settings requires intermediate observability beyond output-only evaluation.

---

## Computer Environments Elicit General Agentic Intelligence in LLMs

**Authors:** Daixuan Cheng, Shaohan Huang, Yuxian Gu, Huatong Song, Guoxin Chen, Li Dong, Wayne Xin Zhao, Ji-Rong Wen, Furu Wei

**Published:** 2026-01-22T18:57:09Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2601.16206v3) | [PDF](https://arxiv.org/pdf/2601.16206v3)

**Abstract:**
Agentic intelligence in large language models (LLMs) requires not only model intrinsic capabilities but also interactions with external environments. Equipping LLMs with computers now represents a prevailing trend. However, the computer environment's intrinsic value has not been systematically investigated, particularly its potential to elicit general capabilities. Here we introduce LLM-in-Sandbox, which virtualizes the computer as a code sandbox with only basic functionalities, and demonstrate that this minimal setting elicits computer-based meta-capabilities for general task solving: external resource access, file management, and code execution. Without additional training, strong models achieve substantial gains (up to 15.5%) across mathematics, physics, chemistry, biomedicine, long-context understanding, and instruction following, while reducing token consumption by up to 8 times. Furthermore, we develop LLM-in-Sandbox-RL to train models exclusively on non-agentic data within the sandbox, empowering weaker models to harness the environment and internalize these interactions. Our results demonstrate that computer environments elicit general intelligence, yield efficiency gains, and can be harnessed through training, serving as a promising foundation for generalist agents.

---

## Understanding Multi-Agent LLM Frameworks: A Unified Benchmark and Experimental Analysis

**Authors:** Abdelghny Orogat, Ana Rostam, Essam Mansour

**Published:** 2026-02-03T05:37:56Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2602.03128v1) | [PDF](https://arxiv.org/pdf/2602.03128v1)

**Abstract:**
Multi-agent LLM frameworks are widely used to accelerate the development of agent systems powered by large language models (LLMs). These frameworks impose distinct architectural structures that govern how agents interact, store information, and coordinate tasks. However, their impact on system performance remains poorly understood. This gap is critical, as architectural choices alone can induce order-of-magnitude differences in latency and throughput, as well as substantial variation in accuracy and scalability. Addressing this challenge requires (i) jointly evaluating multiple capabilities, such as orchestration overhead, memory behavior, planning, specialization, and coordination, and (ii) conducting these evaluations under controlled, framework-level conditions to isolate architectural effects. Existing benchmarks focus on individual capabilities and lack standardized framework-level evaluation. We address these limitations by (i) introducing an architectural taxonomy for systematically comparing multi-agent LLM frameworks along fundamental dimensions, and (ii) developing MAFBench, a unified evaluation suite that integrates existing benchmarks under a standardized execution pipeline. Using MAFBench, we conduct a controlled empirical study across several widely used frameworks. Our results show that framework-level design choices alone can increase latency by over 100x, reduce planning accuracy by up to 30%, and lower coordination success from above 90% to below 30%. Finally, we translate our findings into concrete architectural design principles and framework selection guidance, and outline promising future research directions.

---

## WizardLM: Empowering large pre-trained language models to follow complex instructions

**Authors:** Can Xu, Qingfeng Sun, Kai Zheng, Xiubo Geng, Pu Zhao, Jiazhan Feng, Chongyang Tao, Qingwei Lin, Daxin Jiang

**Published:** 2023-04-24T16:31:06Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2304.12244v3) | [PDF](https://arxiv.org/pdf/2304.12244v3)

**Abstract:**
Training large language models (LLMs) with open-domain instruction following data brings colossal success. However, manually creating such instruction data is very time-consuming and labor-intensive. Moreover, humans may struggle to produce high-complexity instructions. In this paper, we show an avenue for creating large amounts of instruction data with varying levels of complexity using LLM instead of humans. Starting with an initial set of instructions, we use our proposed Evol-Instruct to rewrite them step by step into more complex instructions. Then, we mix all generated instruction data to fine-tune LLaMA. We call the resulting model WizardLM. Human evaluations on a complexity-balanced test bed and Vicuna's testset show that instructions from Evol-Instruct are superior to human-created ones. By analyzing the human evaluation results of the high complexity part, we demonstrate that outputs from our WizardLM are preferred to outputs from OpenAI ChatGPT. In GPT-4 automatic evaluation, WizardLM achieves more than 90\% capacity of ChatGPT on 17 out of 29 skills. Even though WizardLM still lags behind ChatGPT in some aspects, our findings suggest that fine-tuning with AI-evolved instructions is a promising direction for enhancing LLMs. Our code and data are public at https://github.com/nlpxucan/WizardLM

---

## LLM Constitutional Multi-Agent Governance

**Authors:** J. de Curtò, I. de Zarzà

**Published:** 2026-03-13T17:21:26Z

**Categories:** cs.MA, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2603.13189v1) | [PDF](https://arxiv.org/pdf/2603.13189v1)

**Abstract:**
Large Language Models (LLMs) can generate persuasive influence strategies that shift cooperative behavior in multi-agent populations, but a critical question remains: does the resulting cooperation reflect genuine prosocial alignment, or does it mask erosion of agent autonomy, epistemic integrity, and distributional fairness? We introduce Constitutional Multi-Agent Governance (CMAG), a two-stage framework that interposes between an LLM policy compiler and a networked agent population, combining hard constraint filtering with soft penalized-utility optimization that balances cooperation potential against manipulation risk and autonomy pressure. We propose the Ethical Cooperation Score (ECS), a multiplicative composite of cooperation, autonomy, integrity, and fairness that penalizes cooperation achieved through manipulative means. In experiments on scale-free networks of 80 agents under adversarial conditions (70% violating candidates), we benchmark three regimes: full CMAG, naive filtering, and unconstrained optimization. While unconstrained optimization achieves the highest raw cooperation (0.873), it yields the lowest ECS (0.645) due to severe autonomy erosion (0.867) and fairness degradation (0.888). CMAG attains an ECS of 0.741, a 14.9% improvement, while preserving autonomy at 0.985 and integrity at 0.995, with only modest cooperation reduction to 0.770. The naive ablation (ECS = 0.733) confirms that hard constraints alone are insufficient. Pareto analysis shows CMAG dominates the cooperation-autonomy trade-off space, and governance reduces hub-periphery exposure disparities by over 60%. These findings establish that cooperation is not inherently desirable without governance: constitutional constraints are necessary to ensure that LLM-mediated influence produces ethically stable outcomes rather than manipulative equilibria.

---

## FBI-LLM: Scaling Up Fully Binarized LLMs from Scratch via Autoregressive Distillation

**Authors:** Liqun Ma, Mingjie Sun, Zhiqiang Shen

**Published:** 2024-07-09T17:59:48Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2407.07093v1) | [PDF](https://arxiv.org/pdf/2407.07093v1)

**Abstract:**
This work presents a Fully BInarized Large Language Model (FBI-LLM), demonstrating for the first time how to train a large-scale binary language model from scratch (not the partial binary or ternary LLM like BitNet b1.58) to match the performance of its full-precision counterparts (e.g., FP16 or BF16) in transformer-based LLMs. It achieves this by employing an autoregressive distillation (AD) loss with maintaining equivalent model dimensions (130M, 1.3B, 7B) and training data volume as regular LLM pretraining, while delivering competitive results in terms of perplexity and task-specific effectiveness. Intriguingly, by analyzing the training trajectory, we find that the pretrained weight is not necessary for training binarized LLMs from scratch. This research encourages a new computational framework and may facilitate the future design of specialized hardware tailored for fully 1-bit LLMs. We make all models, code, and training dataset fully accessible and transparent to support further research (Code: https://github.com/LiqunMa/FBI-LLM. Model: https://huggingface.co/LiqunMa/).

---

## MuLan: Multimodal-LLM Agent for Progressive and Interactive Multi-Object Diffusion

**Authors:** Sen Li, Ruochen Wang, Cho-Jui Hsieh, Minhao Cheng, Tianyi Zhou

**Published:** 2024-02-20T06:14:30Z

**Categories:** cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2402.12741v2) | [PDF](https://arxiv.org/pdf/2402.12741v2)

**Abstract:**
Existing text-to-image models still struggle to generate images of multiple objects, especially in handling their spatial positions, relative sizes, overlapping, and attribute bindings. To efficiently address these challenges, we develop a training-free Multimodal-LLM agent (MuLan), as a human painter, that can progressively generate multi-object with intricate planning and feedback control. MuLan harnesses a large language model (LLM) to decompose a prompt to a sequence of sub-tasks, each generating only one object by stable diffusion, conditioned on previously generated objects. Unlike existing LLM-grounded methods, MuLan only produces a high-level plan at the beginning while the exact size and location of each object are determined upon each sub-task by an LLM and attention guidance. Moreover, MuLan adopts a vision-language model (VLM) to provide feedback to the image generated in each sub-task and control the diffusion model to re-generate the image if it violates the original prompt. Hence, each model in every step of MuLan only needs to address an easy sub-task it is specialized for. The multi-step process also allows human users to monitor the generation process and make preferred changes at any intermediate step via text prompts, thereby improving the human-AI collaboration experience. We collect 200 prompts containing multi-objects with spatial relationships and attribute bindings from different benchmarks to evaluate MuLan. The results demonstrate the superiority of MuLan in generating multiple objects over baselines and its creativity when collaborating with human users. The code is available at https://github.com/measure-infinity/mulan-code.

---

## LLM-Optic: Unveiling the Capabilities of Large Language Models for Universal Visual Grounding

**Authors:** Haoyu Zhao, Wenhang Ge, Ying-cong Chen

**Published:** 2024-05-27T12:23:08Z

**Categories:** cs.CV, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2405.17104v2) | [PDF](https://arxiv.org/pdf/2405.17104v2)

**Abstract:**
Visual grounding is an essential tool that links user-provided text queries with query-specific regions within an image. Despite advancements in visual grounding models, their ability to comprehend complex queries remains limited. To overcome this limitation, we introduce LLM-Optic, an innovative method that utilizes Large Language Models (LLMs) as an optical lens to enhance existing visual grounding models in comprehending complex text queries involving intricate text structures, multiple objects, or object spatial relationships, situations that current models struggle with. LLM-Optic first employs an LLM as a Text Grounder to interpret complex text queries and accurately identify objects the user intends to locate. Then a pre-trained visual grounding model is used to generate candidate bounding boxes given the refined query by the Text Grounder. After that, LLM-Optic annotates the candidate bounding boxes with numerical marks to establish a connection between text and specific image regions, thereby linking two distinct modalities. Finally, it employs a Large Multimodal Model (LMM) as a Visual Grounder to select the marked candidate objects that best correspond to the original text query. Through LLM-Optic, we have achieved universal visual grounding, which allows for the detection of arbitrary objects specified by arbitrary human language input. Importantly, our method achieves this enhancement without requiring additional training or fine-tuning. Extensive experiments across various challenging benchmarks demonstrate that LLM-Optic achieves state-of-the-art zero-shot visual grounding capabilities. Project Page: https://haoyu-zhao.github.io/LLM-Optic.github.io/.

---

## Open-Ended Instructable Embodied Agents with Memory-Augmented Large Language Models

**Authors:** Gabriel Sarch, Yue Wu, Michael J. Tarr, Katerina Fragkiadaki

**Published:** 2023-10-23T17:31:55Z

**Categories:** cs.AI, cs.CL, cs.LG, cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2310.15127v2) | [PDF](https://arxiv.org/pdf/2310.15127v2)

**Abstract:**
Pre-trained and frozen large language models (LLMs) can effectively map simple scene rearrangement instructions to programs over a robot's visuomotor functions through appropriate few-shot example prompting. To parse open-domain natural language and adapt to a user's idiosyncratic procedures, not known during prompt engineering time, fixed prompts fall short. In this paper, we introduce HELPER, an embodied agent equipped with an external memory of language-program pairs that parses free-form human-robot dialogue into action programs through retrieval-augmented LLM prompting: relevant memories are retrieved based on the current dialogue, instruction, correction, or VLM description, and used as in-context prompt examples for LLM querying. The memory is expanded during deployment to include pairs of user's language and action plans, to assist future inferences and personalize them to the user's language and routines. HELPER sets a new state-of-the-art in the TEACh benchmark in both Execution from Dialog History (EDH) and Trajectory from Dialogue (TfD), with a 1.7x improvement over the previous state-of-the-art for TfD. Our models, code, and video results can be found in our project's website: https://helper-agent-llm.github.io.

---

## The Social Laboratory: A Psychometric Framework for Multi-Agent LLM Evaluation

**Authors:** Zarreen Reza

**Published:** 2025-10-01T07:10:28Z

**Categories:** cs.AI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2510.01295v1) | [PDF](https://arxiv.org/pdf/2510.01295v1)

**Abstract:**
As Large Language Models (LLMs) transition from static tools to autonomous agents, traditional evaluation benchmarks that measure performance on downstream tasks are becoming insufficient. These methods fail to capture the emergent social and cognitive dynamics that arise when agents communicate, persuade, and collaborate in interactive environments. To address this gap, we introduce a novel evaluation framework that uses multi-agent debate as a controlled "social laboratory" to discover and quantify these behaviors. In our framework, LLM-based agents, instantiated with distinct personas and incentives, deliberate on a wide range of challenging topics under the supervision of an LLM moderator. Our analysis, enabled by a new suite of psychometric and semantic metrics, reveals several key findings. Across hundreds of debates, we uncover a powerful and robust emergent tendency for agents to seek consensus, consistently reaching high semantic agreement (μ > 0.88) even without explicit instruction and across sensitive topics. We show that assigned personas induce stable, measurable psychometric profiles, particularly in cognitive effort, and that the moderators persona can significantly alter debate outcomes by structuring the environment, a key finding for external AI alignment. This work provides a blueprint for a new class of dynamic, psychometrically grounded evaluation protocols designed for the agentic setting, offering a crucial methodology for understanding and shaping the social behaviors of the next generation of AI agents. We have released the code and results at https://github.com/znreza/multi-agent-LLM-eval-for-debate.

---

## TradingAgents: Multi-Agents LLM Financial Trading Framework

**Authors:** Yijia Xiao, Edward Sun, Di Luo, Wei Wang

**Published:** 2024-12-28T12:54:06Z

**Categories:** q-fin.TR, cs.AI, cs.CE, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2412.20138v7) | [PDF](https://arxiv.org/pdf/2412.20138v7)

**Abstract:**
Significant progress has been made in automated problem-solving using societies of agents powered by large language models (LLMs). In finance, efforts have largely focused on single-agent systems handling specific tasks or multi-agent frameworks independently gathering data. However, the multi-agent systems' potential to replicate real-world trading firms' collaborative dynamics remains underexplored. TradingAgents proposes a novel stock trading framework inspired by trading firms, featuring LLM-powered agents in specialized roles such as fundamental analysts, sentiment analysts, technical analysts, and traders with varied risk profiles. The framework includes Bull and Bear researcher agents assessing market conditions, a risk management team monitoring exposure, and traders synthesizing insights from debates and historical data to make informed decisions. By simulating a dynamic, collaborative trading environment, this framework aims to improve trading performance. Detailed architecture and extensive experiments reveal its superiority over baseline models, with notable improvements in cumulative returns, Sharpe ratio, and maximum drawdown, highlighting the potential of multi-agent LLM frameworks in financial trading. TradingAgents is available at https://github.com/TauricResearch/TradingAgents.

---

## Large Language Models as Urban Residents: An LLM Agent Framework for Personal Mobility Generation

**Authors:** Jiawei Wang, Renhe Jiang, Chuang Yang, Zengqing Wu, Makoto Onizuka, Ryosuke Shibasaki, Noboru Koshizuka, Chuan Xiao

**Published:** 2024-02-22T18:03:14Z

**Categories:** cs.AI, cs.CL, cs.CY, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2402.14744v3) | [PDF](https://arxiv.org/pdf/2402.14744v3)

**Abstract:**
This paper introduces a novel approach using Large Language Models (LLMs) integrated into an agent framework for flexible and effective personal mobility generation. LLMs overcome the limitations of previous models by effectively processing semantic data and offering versatility in modeling various tasks. Our approach addresses three research questions: aligning LLMs with real-world urban mobility data, developing reliable activity generation strategies, and exploring LLM applications in urban mobility. The key technical contribution is a novel LLM agent framework that accounts for individual activity patterns and motivations, including a self-consistency approach to align LLMs with real-world activity data and a retrieval-augmented strategy for interpretable activity generation. We evaluate our LLM agent framework and compare it with state-of-the-art personal mobility generation approaches, demonstrating the effectiveness of our approach and its potential applications in urban mobility. Overall, this study marks the pioneering work of designing an LLM agent framework for activity generation based on real-world human activity data, offering a promising tool for urban mobility analysis.

---

## Agentic Large Language Models, a survey

**Authors:** Aske Plaat, Max van Duijn, Niki van Stein, Mike Preuss, Peter van der Putten, Kees Joost Batenburg

**Published:** 2025-03-29T11:02:20Z

**Categories:** cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2503.23037v3) | [PDF](https://arxiv.org/pdf/2503.23037v3)

**Abstract:**
Background: There is great interest in agentic LLMs, large language models that act as agents.
  Objectives: We review the growing body of work in this area and provide a research agenda.
  Methods: Agentic LLMs are LLMs that (1) reason, (2) act, and (3) interact. We organize the literature according to these three categories.
  Results: The research in the first category focuses on reasoning, reflection, and retrieval, aiming to improve decision making; the second category focuses on action models, robots, and tools, aiming for agents that act as useful assistants; the third category focuses on multi-agent systems, aiming for collaborative task solving and simulating interaction to study emergent social behavior. We find that works mutually benefit from results in other categories: retrieval enables tool use, reflection improves multi-agent collaboration, and reasoning benefits all categories.
  Conclusions: We discuss applications of agentic LLMs and provide an agenda for further research. Important applications are in medical diagnosis, logistics and financial market analysis. Meanwhile, self-reflective agents playing roles and interacting with one another augment the process of scientific research itself. Further, agentic LLMs provide a solution for the problem of LLMs running out of training data: inference-time behavior generates new training states, such that LLMs can keep learning without needing ever larger datasets. We note that there is risk associated with LLM assistants taking action in the real world-safety, liability and security are open problems-while agentic LLMs are also likely to benefit society.

---

## PhishDebate: An LLM-Based Multi-Agent Framework for Phishing Website Detection

**Authors:** Wenhao Li, Selvakumar Manickam, Yung-wey Chong, Shankar Karuppayah

**Published:** 2025-06-18T17:33:18Z

**Categories:** cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2506.15656v2) | [PDF](https://arxiv.org/pdf/2506.15656v2)

**Abstract:**
Phishing websites remain a major cybersecurity threat, exploiting deceptive structures, brand impersonation, and social engineering to evade detection. Recent advances in large language models (LLMs) have improved phishing detection through contextual understanding, yet most existing approaches rely on single-agent classification, which is prone to hallucination and often lacks interpretability and robustness. To address these limitations, we propose PhishDebate, a modular multi-agent LLM-based debate framework for phishing website detection. Four specialized agents independently analyze webpage aspects, including URL structure, HTML composition, semantic content, and brand impersonation, under the coordination of a Moderator and final Judge. Through structured debate and divergent reasoning, the framework achieves more accurate and interpretable decisions. By reducing uncertain predictions and providing transparent reasoning, PhishDebate functions as an analyst-augmentation system that lowers cognitive load and supports early, left-of-exploit detection of phishing threats. Evaluations on commercial LLMs show that PhishDebate achieves 98.2 % recall on a real-world phishing dataset and outperforms single-agent and Chain-of-Thought (CoT) baselines. Its modular design enables agent-level configurability, allowing adaptation to varying resource and application requirements, and offers scalability to high-velocity, large-scale security data environments.

---

## STRIDE: A Systematic Framework for Selecting AI Modalities -- Agentic AI, AI Assistants, or LLM Calls

**Authors:** Shubhi Asthana, Bing Zhang, Chad DeLuca, Ruchi Mahindru, Hima Patel

**Published:** 2025-12-01T21:54:07Z

**Categories:** cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2512.02228v1) | [PDF](https://arxiv.org/pdf/2512.02228v1)

**Abstract:**
The rapid shift from stateless large language models (LLMs) to autonomous, goal-driven agents raises a central question: When is agentic AI truly necessary? While agents enable multi-step reasoning, persistent memory, and tool orchestration, deploying them indiscriminately leads to higher cost, complexity, and risk.
  We present STRIDE (Systematic Task Reasoning Intelligence Deployment Evaluator), a framework that provides principled recommendations for selecting between three modalities: (i) direct LLM calls, (ii) guided AI assistants, and (iii) fully autonomous agentic AI. STRIDE integrates structured task decomposition, dynamism attribution, and self-reflection requirement analysis to produce an Agentic Suitability Score, ensuring that full agentic autonomy is reserved for tasks with inherent dynamism or evolving context.
  Evaluated across 30 real-world tasks spanning SRE, compliance, and enterprise automation, STRIDE achieved 92% accuracy in modality selection, reduced unnecessary agent deployments by 45%, and cut resource costs by 37%. Expert validation over six months in SRE and compliance domains confirmed its practical utility, with domain specialists agreeing that STRIDE effectively distinguishes between tasks requiring simple LLM calls, guided assistants, or full agentic autonomy. This work reframes agent adoption as a necessity-driven design decision, ensuring autonomy is applied only when its benefits justify the costs.

---

## Agent Memory Below the Prompt: Persistent Q4 KV Cache for Multi-Agent LLM Inference on Edge Devices

**Authors:** Yakov Pyotr Shkolnikov

**Published:** 2026-02-17T05:46:20Z

**Categories:** cs.LG, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2603.04428v1) | [PDF](https://arxiv.org/pdf/2603.04428v1)

**Abstract:**
Multi-agent LLM systems on edge devices face a memory management problem: device RAM is too small to hold every agent's KV cache simultaneously. On Apple M4 Pro with 10.2 GB of cache budget, only 3 agents fit at 8K context in FP16. A 10-agent workflow must constantly evict and reload caches. Without persistence, every eviction forces a full re-prefill through the model -- 15.7 seconds per agent at 4K context. We address this by persisting each agent's KV cache to disk in 4-bit quantized format and reloading it directly into the attention layer, eliminating redundant O(n) prefill computation via direct cache restoration. The system comprises three components: a block pool providing per-agent isolated Q4 KV caches in safetensors format, a BatchQuantizedKVCache for concurrent inference over multiple agents' quantized caches, and cross-phase context injection that accumulates attention state across conversation phases without re-computation. Evaluated on three architectures (Gemma 3 12B, dense GQA, 48 layers; DeepSeek-Coder-V2-Lite 16B, MoE MLA, 27 layers; Llama 3.1 8B, dense GQA, 32 layers), cache restoration reduces time-to-first-token by up to 136x (Gemma: 22--136x at 4K--32K; DeepSeek: 11--76x at 4K--32K; Llama: 24--111x at 4K--16K; 3--10x at 1K). Q4 quantization fits 4x more agent contexts into fixed device memory than FP16. Perplexity measured with actual Q4 KV caches shows -0.7% for Gemma, +2.8% for Llama, and +3.0% for DeepSeek. Open-source at https://github.com/yshk-mxim/agent-memory

---

## astra-langchain4j: Experiences Combining LLMs and Agent Programming

**Authors:** Rem Collier, Katharine Beaumont, Andrei Ciortea

**Published:** 2026-01-29T15:46:13Z

**Categories:** cs.AI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2601.21879v1) | [PDF](https://arxiv.org/pdf/2601.21879v1)

**Abstract:**
Given the emergence of Generative AI over the last two years and the increasing focus on Agentic AI as a form of Multi-Agent System it is important to explore both how such technologies can impact the use of traditional Agent Toolkits and how the wealth of experience encapsulated in those toolkits can influence the design of the new agentic platforms. This paper presents an overview of our experience developing a prototype large language model (LLM) integration for the ASTRA programming language. It presents a brief overview of the toolkit, followed by three example implementations, concluding with a discussion of the experiences garnered through the examples.

---

## Task-Aware Delegation Cues for LLM Agents

**Authors:** Xingrui Gu

**Published:** 2026-03-11T17:35:44Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2603.11011v1) | [PDF](https://arxiv.org/pdf/2603.11011v1)

**Abstract:**
LLM agents increasingly present as conversational collaborators, yet human--agent teamwork remains brittle due to information asymmetry: users lack task-specific reliability cues, and agents rarely surface calibrated uncertainty or rationale. We propose a task-aware collaboration signaling layer that turns offline preference evaluations into online, user-facing primitives for delegation. Using Chatbot Arena pairwise comparisons, we induce an interpretable task taxonomy via semantic clustering, then derive (i) Capability Profiles as task-conditioned win-rate maps and (ii) Coordination-Risk Cues as task-conditioned disagreement (tie-rate) priors. These signals drive a closed-loop delegation protocol that supports common-ground verification, adaptive routing (primary vs.\ primary+auditor), explicit rationale disclosure, and privacy-preserving accountability logs. Two predictive probes validate that task typing carries actionable structure: cluster features improve winner prediction accuracy and reduce difficulty prediction error under stratified 5-fold cross-validation. Overall, our framework reframes delegation from an opaque system default into a visible, negotiable, and auditable collaborative decision, providing a principled design space for adaptive human--agent collaboration grounded in mutual awareness and shared accountability.

---

## ARCANE: A Multi-Agent Framework for Interpretable and Configurable Alignment

**Authors:** Charlie Masters, Marta Grześkiewicz, Stefano V. Albrecht

**Published:** 2025-12-05T22:39:54Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2512.06196v1) | [PDF](https://arxiv.org/pdf/2512.06196v1)

**Abstract:**
As agents based on large language models are increasingly deployed to long-horizon tasks, maintaining their alignment with stakeholder preferences becomes critical. Effective alignment in such settings requires reward models that are interpretable so that stakeholders can understand and audit model objectives. Moreover, reward models must be capable of steering agents at interaction time, allowing preference shifts to be incorporated without retraining. We introduce ARCANE, a framework that frames alignment as a multi-agent collaboration problem that dynamically represents stakeholder preferences as natural-language rubrics: weighted sets of verifiable criteria that can be generated on-the-fly from task context. Inspired by utility theory, we formulate rubric learning as a reconstruction problem and apply a regularized Group-Sequence Policy Optimization (GSPO) procedure that balances interpretability, faithfulness, and computational efficiency. Using a corpus of 219 labeled rubrics derived from the GDPVal benchmark, we evaluate ARCANE on challenging tasks requiring multi-step reasoning and tool use. The learned rubrics produce compact, legible evaluations and enable configurable trade-offs (e.g., correctness vs. conciseness) without retraining. Our results show that rubric-based reward models offer a promising path toward interpretable, test-time adaptive alignment for complex, long-horizon AI systems.

---

## CATP-LLM: Empowering Large Language Models for Cost-Aware Tool Planning

**Authors:** Duo Wu, Jinghe Wang, Yuan Meng, Yanning Zhang, Le Sun, Zhi Wang

**Published:** 2024-11-25T12:05:49Z

**Categories:** cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2411.16313v3) | [PDF](https://arxiv.org/pdf/2411.16313v3)

**Abstract:**
Utilizing large language models (LLMs) for tool planning has emerged as a promising avenue for developing general AI systems, where LLMs automatically schedule external tools (e.g., vision models) to tackle complex tasks based on task descriptions. To push this paradigm toward practical applications, it is crucial for LLMs to consider tool execution costs (e.g., execution time) for tool planning. Unfortunately, prior studies overlook the tool execution costs, leading to the generation of expensive plans whose costs outweigh their benefits in terms of task performance. To fill this gap, we propose the Cost-Aware Tool Planning with LLMs (CATP-LLM) framework, which for the first time provides a coherent design to empower LLMs for cost-aware tool planning. Specifically, To facilitate efficient concurrent tool execution and cost reduction, we design a tool planning language to enhance the LLM for creating multi-branch non-sequential plans. Moreover, we propose a cost-aware offline reinforcement learning algorithm to fine-tune the LLM to optimize the performance-cost trade-off in tool planning. In the lack of public cost-related datasets, we further present OpenCATP, the first dataset for cost-aware planning, which comprises 11,100 evaluation samples from diverse tasks. Extensive experiments show that CATP-LLM outperforms GPT-4 even when using Llama2-7B as its backbone, with the average improvement of 1.5%-93.9% in terms of plan quality. Codes and dataset are available at: https://github.com/duowuyms/OpenCATP-LLM.

---

## LMR-BENCH: Evaluating LLM Agent's Ability on Reproducing Language Modeling Research

**Authors:** Shuo Yan, Ruochen Li, Ziming Luo, Zimu Wang, Daoyang Li, Liqiang Jing, Kaiyu He, Peilin Wu, George Michalopoulos, Yue Zhang, Ziyang Zhang, Mian Zhang, Zhiyu Chen, Xinya Du

**Published:** 2025-06-19T07:04:16Z

**Categories:** cs.SE, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2506.17335v1) | [PDF](https://arxiv.org/pdf/2506.17335v1)

**Abstract:**
Large language model (LLM) agents have demonstrated remarkable potential in advancing scientific discovery. However, their capability in the fundamental yet crucial task of reproducing code from research papers, especially in the NLP domain, remains underexplored. This task includes unique complex reasoning challenges in the intellectual synthesis of abstract concepts and the comprehension of code repositories with interdependent files. Motivated by this gap, we present LMR-BENCH, a benchmark designed to systematically evaluate the capability of LLM agents on code reproduction from Language Modeling Research. It consists of 28 code reproduction tasks derived from 23 research papers published in top-tier NLP venues over the past five years, spanning nine fundamental categories. Models are provided with a research paper, a code repository containing one or more masked functions, and instructions for implementing these functions. We conduct extensive experiments in standard prompting and LLM agent settings with state-of-the-art LLMs, evaluating the accuracy of unit tests and performing LLM-based evaluation of code correctness. Experimental results reveal that even the most advanced models still exhibit persistent limitations in scientific reasoning and code synthesis, highlighting critical gaps in LLM agents' ability to autonomously reproduce scientific research

---

## DIAMOND: An LLM-Driven Agent for Context-Aware Baseball Highlight Summarization

**Authors:** Jeonghun Kang, Soonmok Kwon, Joonseok Lee, Byung-Hak Kim

**Published:** 2025-06-03T01:10:20Z

**Categories:** cs.CL, cs.AI, cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2506.02351v1) | [PDF](https://arxiv.org/pdf/2506.02351v1)

**Abstract:**
Traditional approaches -- such as Win Probability Added (WPA)-based ranking or computer vision-driven event detection -- can identify scoring plays but often miss strategic depth, momentum shifts, and storyline progression. Manual curation remains the gold standard but is resource-intensive and not scalable. We introduce DIAMOND, an LLM-driven agent for context-aware baseball highlight summarization that integrates structured sports analytics with natural language reasoning. DIAMOND leverages sabermetric features -- Win Expectancy, WPA, and Leverage Index -- to quantify play importance, while an LLM module enhances selection based on contextual narrative value. This hybrid approach ensures both quantitative rigor and qualitative richness, surpassing the limitations of purely statistical or vision-based systems. Evaluated on five diverse Korean Baseball Organization League games, DIAMOND improves F1-score from 42.9% (WPA-only) to 84.8%, outperforming both commercial and statistical baselines. Though limited in scale, our results highlight the potential of modular, interpretable agent-based frameworks for event-level summarization in sports and beyond.

---

## LLM Economist: Large Population Models and Mechanism Design in Multi-Agent Generative Simulacra

**Authors:** Seth Karten, Wenzhe Li, Zihan Ding, Samuel Kleiner, Yu Bai, Chi Jin

**Published:** 2025-07-21T17:21:14Z

**Categories:** cs.MA, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2507.15815v1) | [PDF](https://arxiv.org/pdf/2507.15815v1)

**Abstract:**
We present the LLM Economist, a novel framework that uses agent-based modeling to design and assess economic policies in strategic environments with hierarchical decision-making. At the lower level, bounded rational worker agents -- instantiated as persona-conditioned prompts sampled from U.S. Census-calibrated income and demographic statistics -- choose labor supply to maximize text-based utility functions learned in-context. At the upper level, a planner agent employs in-context reinforcement learning to propose piecewise-linear marginal tax schedules anchored to the current U.S. federal brackets. This construction endows economic simulacra with three capabilities requisite for credible fiscal experimentation: (i) optimization of heterogeneous utilities, (ii) principled generation of large, demographically realistic agent populations, and (iii) mechanism design -- the ultimate nudging problem -- expressed entirely in natural language. Experiments with populations of up to one hundred interacting agents show that the planner converges near Stackelberg equilibria that improve aggregate social welfare relative to Saez solutions, while a periodic, persona-level voting procedure furthers these gains under decentralized governance. These results demonstrate that large language model-based agents can jointly model, simulate, and govern complex economic systems, providing a tractable test bed for policy evaluation at the societal scale to help build better civilizations.

---

## Adaptive LLM Agents: Toward Personalized Empathetic Care

**Authors:** Priyanka Singh, Sebastian Von Mammen

**Published:** 2025-11-25T08:52:02Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2511.20080v1) | [PDF](https://arxiv.org/pdf/2511.20080v1)

**Abstract:**
Current mental-health conversational systems are usually based on fixed, generic dialogue patterns. This paper proposes an adaptive framework based on large language models that aims to personalize therapeutic interaction according to a user's psychological state, quantified with the Acceptance of Illness Scale (AIS). The framework defines three specialized agents, L, M, and H, each linked to a different level of illness acceptance, and adjusts conversational behavior over time using continuous feedback signals. The AIS-stratified architecture is treated as a diegetic prototype placed in a plausible near-future setting and examined through the method of design fiction. By embedding the architecture in narrative scenarios, the study explores how such agents might influence access to care and therapeutic relationship. The goal is to show how clinically informed personalization, technical feasibility, and speculative scenario analysis can together inform the responsible design of LLM-based companions for mental-health support.

---

## Spark-LLM-Eval: A Distributed Framework for Statistically Rigorous Large Language Model Evaluation

**Authors:** Subhadip Mitra

**Published:** 2026-01-18T04:34:39Z

**Categories:** cs.DC, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2603.28769v1) | [PDF](https://arxiv.org/pdf/2603.28769v1)

**Abstract:**
Evaluating large language models at scale remains a practical bottleneck for many organizations. While existing evaluation frameworks work well for thousands of examples, they struggle when datasets grow to hundreds of thousands or millions of samples. This scale is common when assessing model behavior across diverse domains or conducting comprehensive regression testing. We present Spark-LLM-Eval, a distributed evaluation framework built natively on Apache Spark. The system treats evaluation as a data-parallel problem, partitioningexamplesacrossexecutorsandaggregatingresultswithproperstatistical accounting. Beyond raw throughput, we emphasize statistical rigor: every reported metric includes bootstrap confidence intervals, and model comparisons come with appropriate significance tests (paired t-tests, McNemar's test, or Wilcoxon signed-rank, depending on the metric type). The framework also addresses the cost problem inherent in LLM evaluation through content-addressable response caching backed by Delta Lake, which allows iterating on metric definitions without re-running inference. We describe the system architecture, the statistical methodology, and report benchmark results showing linear scaling with cluster size. The framework and all evaluation code are available as open source.

---

## Hierarchical Multi-agent Large Language Model Reasoning for Autonomous Functional Materials Discovery

**Authors:** Samuel Rothfarb, Megan C. Davis, Ivana Matanovic, Baikun Li, Edward F. Holby, Wilton J. M. Kort-Kamp

**Published:** 2025-12-15T22:08:18Z

**Categories:** cond-mat.mtrl-sci, cs.AI, cs.CL, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2512.13930v1) | [PDF](https://arxiv.org/pdf/2512.13930v1)

**Abstract:**
Artificial intelligence is reshaping scientific exploration, but most methods automate procedural tasks without engaging in scientific reasoning, limiting autonomy in discovery. We introduce Materials Agents for Simulation and Theory in Electronic-structure Reasoning (MASTER), an active learning framework where large language models autonomously design, execute, and interpret atomistic simulations. In MASTER, a multimodal system translates natural language into density functional theory workflows, while higher-level reasoning agents guide discovery through a hierarchy of strategies, including a single agent baseline and three multi-agent approaches: peer review, triage-ranking, and triage-forms. Across two chemical applications, CO adsorption on Cu-surface transition metal (M) adatoms and on M-N-C catalysts, reasoning-driven exploration reduces required atomistic simulations by up to 90% relative to trial-and-error selection. Reasoning trajectories reveal chemically grounded decisions that cannot be explained by stochastic sampling or semantic bias. Altogether, multi-agent collaboration accelerates materials discovery and marks a new paradigm for autonomous scientific exploration.

---

## MemoryCD: Benchmarking Long-Context User Memory of LLM Agents for Lifelong Cross-Domain Personalization

**Authors:** Weizhi Zhang, Xiaokai Wei, Wei-Chieh Huang, Zheng Hui, Chen Wang, Michelle Gong, Philip S. Yu

**Published:** 2026-03-26T23:28:47Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2603.25973v1) | [PDF](https://arxiv.org/pdf/2603.25973v1)

**Abstract:**
Recent advancements in Large Language Models (LLMs) have expanded context windows to million-token scales, yet benchmarks for evaluating memory remain limited to short-session synthetic dialogues. We introduce \textsc{MemoryCD}, the first large-scale, user-centric, cross-domain memory benchmark derived from lifelong real-world behaviors in the Amazon Review dataset. Unlike existing memory datasets that rely on scripted personas to generate synthetic user data, \textsc{MemoryCD} tracks authentic user interactions across years and multiple domains. We construct a multi-faceted long-context memory evaluation pipeline of 14 state-of-the-art LLM base models with 6 memory method baselines on 4 distinct personalization tasks over 12 diverse domains to evaluate an agent's ability to simulate real user behaviors in both single and cross-domain settings. Our analysis reveals that existing memory methods are far from user satisfaction in various domains, offering the first testbed for cross-domain life-long personalization evaluation.

---

## A Methodology to Engineer and Validate Dynamic Multi-level Multi-agent Based Simulations

**Authors:** Jean-Baptiste Soyez, Gildas Morvan, Daniel Dupont, Rochdi Merzouki

**Published:** 2013-11-20T15:44:26Z

**Categories:** cs.MA

**Links:** [Abstract](https://arxiv.org/abs/1311.5108v1) | [PDF](https://arxiv.org/pdf/1311.5108v1)

**Abstract:**
This article proposes a methodology to model and simulate complex systems, based on IRM4MLS, a generic agent-based meta-model able to deal with multi-level systems. This methodology permits the engineering of dynamic multi-level agent-based models, to represent complex systems over several scales and domains of interest. Its goal is to simulate a phenomenon using dynamically the lightest representation to save computer resources without loss of information. This methodology is based on two mechanisms: (1) the activation or deactivation of agents representing different domain parts of the same phenomenon and (2) the aggregation or disaggregation of agents representing the same phenomenon at different scales.

---

## Too Helpful to Be Safe: User-Mediated Attacks on Planning and Web-Use Agents

**Authors:** Fengchao Chen, Tingmin Wu, Van Nguyen, Carsten Rudolph

**Published:** 2026-01-14T03:29:13Z

**Categories:** cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2601.10758v1) | [PDF](https://arxiv.org/pdf/2601.10758v1)

**Abstract:**
Large Language Models (LLMs) have enabled agents to move beyond conversation toward end-to-end task execution and become more helpful. However, this helpfulness introduces new security risks stem less from direct interface abuse than from acting on user-provided content. Existing studies on agent security largely focus on model-internal vulnerabilities or adversarial access to agent interfaces, overlooking attacks that exploit users as unintended conduits. In this paper, we study user-mediated attacks, where benign users are tricked into relaying untrusted or attacker-controlled content to agents, and analyze how commercial LLM agents respond under such conditions. We conduct a systematic evaluation of 12 commercial agents in a sandboxed environment, covering 6 trip-planning agents and 6 web-use agents, and compare agent behavior across scenarios with no, soft, and hard user-requested safety checks. Our results show that agents are too helpful to be safe by default. Without explicit safety requests, trip-planning agents bypass safety constraints in over 92% of cases, converting unverified content into confident booking guidance. Web-use agents exhibit near-deterministic execution of risky actions, with 9 out of 17 supported tests reaching a 100% bypass rate. Even when users express soft or hard safety intent, constraint bypass remains substantial, reaching up to 54.7% and 7% for trip-planning agents, respectively. These findings reveal that the primary issue is not a lack of safety capability, but its prioritization. Agents invoke safety checks only conditionally when explicitly prompted, and otherwise default to goal-driven execution. Moreover, agents lack clear task boundaries and stopping rules, frequently over-executing workflows in ways that lead to unnecessary data disclosure and real-world harm.

---

## A Survey of LLM $\times$ DATA

**Authors:** Xuanhe Zhou, Junxuan He, Wei Zhou, Haodong Chen, Zirui Tang, Haoyu Zhao, Xin Tong, Guoliang Li, Youmin Chen, Jun Zhou, Zhaojun Sun, Binyuan Hui, Shuo Wang, Conghui He, Zhiyuan Liu, Jingren Zhou, Fan Wu

**Published:** 2025-05-24T01:57:12Z

**Categories:** cs.DB, cs.AI, cs.CL, cs.IR, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2505.18458v3) | [PDF](https://arxiv.org/pdf/2505.18458v3)

**Abstract:**
The integration of large language model (LLM) and data management (DATA) is rapidly redefining both domains. In this survey, we comprehensively review the bidirectional relationships. On the one hand, DATA4LLM, spanning large-scale data processing, storage, and serving, feeds LLMs with high quality, diversity, and timeliness of data required for stages like pre-training, post-training, retrieval-augmented generation, and agentic workflows: (i) Data processing for LLMs includes scalable acquisition, deduplication, filtering, selection, domain mixing, and synthetic augmentation; (ii) Data Storage for LLMs focuses on efficient data and model formats, distributed and heterogeneous storage hierarchies, KV-cache management, and fault-tolerant checkpointing; (iii) Data serving for LLMs tackles challenges in RAG (e.g., knowledge post-processing), LLM inference (e.g., prompt compression, data provenance), and training strategies (e.g., data packing and shuffling). On the other hand, in LLM4DATA, LLMs are emerging as general-purpose engines for data management. We review recent advances in (i) data manipulation, including automatic data cleaning, integration, discovery; (ii) data analysis, covering reasoning over structured, semi-structured, and unstructured data, and (iii) system optimization (e.g., configuration tuning, query rewriting, anomaly diagnosis), powered by LLM techniques like retrieval-augmented prompting, task-specialized fine-tuning, and multi-agent collaboration.

---

## LLM-Agent-Controller: A Universal Multi-Agent Large Language Model System as a Control Engineer

**Authors:** Rasoul Zahedifar, Sayyed Ali Mirghasemi, Mahdieh Soleymani Baghshah, Alireza Taheri

**Published:** 2025-05-26T06:30:13Z

**Categories:** cs.AI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2505.19567v1) | [PDF](https://arxiv.org/pdf/2505.19567v1)

**Abstract:**
This study presents the LLM-Agent-Controller, a multi-agent large language model (LLM) system developed to address a wide range of problems in control engineering (Control Theory). The system integrates a central controller agent with multiple specialized auxiliary agents, responsible for tasks such as controller design, model representation, control analysis, time-domain response, and simulation. A supervisor oversees high-level decision-making and workflow coordination, enhancing the system's reliability and efficiency. The LLM-Agent-Controller incorporates advanced capabilities, including Retrieval-Augmented Generation (RAG), Chain-of-Thought reasoning, self-criticism and correction, efficient memory handling, and user-friendly natural language communication. It is designed to function without requiring users to have prior knowledge of Control Theory, enabling them to input problems in plain language and receive complete, real-time solutions. To evaluate the system, we propose new performance metrics assessing both individual agents and the system as a whole. We test five categories of Control Theory problems and benchmark performance across three advanced LLMs. Additionally, we conduct a comprehensive qualitative conversational analysis covering all key services. Results show that the LLM-Agent-Controller successfully solved 83% of general tasks, with individual agents achieving an average success rate of 87%. Performance improved with more advanced LLMs. This research demonstrates the potential of multi-agent LLM architectures to solve complex, domain-specific problems. By integrating specialized agents, supervisory control, and advanced reasoning, the LLM-Agent-Controller offers a scalable, robust, and accessible solution framework that can be extended to various technical domains.

---

## LLM Post-Training: A Deep Dive into Reasoning Large Language Models

**Authors:** Komal Kumar, Tajamul Ashraf, Omkar Thawakar, Rao Muhammad Anwer, Hisham Cholakkal, Mubarak Shah, Ming-Hsuan Yang, Phillip H. S. Torr, Fahad Shahbaz Khan, Salman Khan

**Published:** 2025-02-28T18:59:54Z

**Categories:** cs.CL, cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2502.21321v2) | [PDF](https://arxiv.org/pdf/2502.21321v2)

**Abstract:**
Large Language Models (LLMs) have transformed the natural language processing landscape and brought to life diverse applications. Pretraining on vast web-scale data has laid the foundation for these models, yet the research community is now increasingly shifting focus toward post-training techniques to achieve further breakthroughs. While pretraining provides a broad linguistic foundation, post-training methods enable LLMs to refine their knowledge, improve reasoning, enhance factual accuracy, and align more effectively with user intents and ethical considerations. Fine-tuning, reinforcement learning, and test-time scaling have emerged as critical strategies for optimizing LLMs performance, ensuring robustness, and improving adaptability across various real-world tasks. This survey provides a systematic exploration of post-training methodologies, analyzing their role in refining LLMs beyond pretraining, addressing key challenges such as catastrophic forgetting, reward hacking, and inference-time trade-offs. We highlight emerging directions in model alignment, scalable adaptation, and inference-time reasoning, and outline future research directions. We also provide a public repository to continually track developments in this fast-evolving field: https://github.com/mbzuai-oryx/Awesome-LLM-Post-training.

---

## Demystifying AI Platform Design for Distributed Inference of Next-Generation LLM models

**Authors:** Abhimanyu Bambhaniya, Ritik Raj, Geonhwa Jeong, Souvik Kundu, Sudarshan Srinivasan, Suvinay Subramanian, Midhilesh Elavazhagan, Madhu Kumar, Tushar Krishna

**Published:** 2024-06-03T18:00:50Z

**Categories:** cs.AR, cs.AI, cs.DC, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2406.01698v3) | [PDF](https://arxiv.org/pdf/2406.01698v3)

**Abstract:**
Large language models (LLMs) have shown remarkable performance across a wide range of applications, often outperforming human experts. However, deploying these gigantic models efficiently for diverse inference use cases requires carefully designed hardware platforms with ample computing, memory, and network resources. With constant innovation in LLM serving optimizations and model architecture evolving at breakneck speed, the hardware requirements to meet Service Level Objectives (SLOs) remain an open research question.
  To answer the question, we present an analytical tool, GenZ, to efficiently navigate the relationship between diverse LLM model architectures(Dense, GQA, MoE, Mamba), LLM serving optimizations(Chunking, Speculative decoding, quanitization), and AI platform design parameters. Our tool estimates LLM inference performance metrics for the given scenario. We have validated against real hardware platforms running various different LLM models, achieving a max geomean error of 5.82.We use GenZ to identify compute, memory capacity, memory bandwidth, network latency, and network bandwidth requirements across diverse LLM inference use cases. We also study diverse architectural choices in use today (inspired by LLM serving platforms from several vendors) to help inform computer architects designing next-generation AI hardware accelerators and platforms. The trends and insights derived from GenZ can guide AI engineers deploying LLMs as well as computer architects designing next-generation hardware accelerators and platforms. Ultimately, this work sheds light on the platform design considerations for unlocking the full potential of large language models across a spectrum of applications. The source code is available at https://github.com/abhibambhaniya/GenZ-LLM-Analyzer . Users can also be tried it on at https://genz-llm-analyzer.streamlit.app/ without any setup on your web browser.

---

## LLM Agents in Interaction: Measuring Personality Consistency and Linguistic Alignment in Interacting Populations of Large Language Models

**Authors:** Ivar Frisch, Mario Giulianelli

**Published:** 2024-02-05T11:05:20Z

**Categories:** cs.CL, cs.AI, cs.CY, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2402.02896v1) | [PDF](https://arxiv.org/pdf/2402.02896v1)

**Abstract:**
While both agent interaction and personalisation are vibrant topics in research on large language models (LLMs), there has been limited focus on the effect of language interaction on the behaviour of persona-conditioned LLM agents. Such an endeavour is important to ensure that agents remain consistent to their assigned traits yet are able to engage in open, naturalistic dialogues. In our experiments, we condition GPT-3.5 on personality profiles through prompting and create a two-group population of LLM agents using a simple variability-inducing sampling algorithm. We then administer personality tests and submit the agents to a collaborative writing task, finding that different profiles exhibit different degrees of personality consistency and linguistic alignment to their conversational partners. Our study seeks to lay the groundwork for better understanding of dialogue-based interaction between LLMs and highlights the need for new approaches to crafting robust, more human-like LLM personas for interactive environments.

---

## ManuSearch: Democratizing Deep Search in Large Language Models with a Transparent and Open Multi-Agent Framework

**Authors:** Lisheng Huang, Yichen Liu, Jinhao Jiang, Rongxiang Zhang, Jiahao Yan, Junyi Li, Wayne Xin Zhao

**Published:** 2025-05-23T17:02:02Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2505.18105v1) | [PDF](https://arxiv.org/pdf/2505.18105v1)

**Abstract:**
Recent advances in web-augmented large language models (LLMs) have exhibited strong performance in complex reasoning tasks, yet these capabilities are mostly locked in proprietary systems with opaque architectures. In this work, we propose \textbf{ManuSearch}, a transparent and modular multi-agent framework designed to democratize deep search for LLMs. ManuSearch decomposes the search and reasoning process into three collaborative agents: (1) a solution planning agent that iteratively formulates sub-queries, (2) an Internet search agent that retrieves relevant documents via real-time web search, and (3) a structured webpage reading agent that extracts key evidence from raw web content. To rigorously evaluate deep reasoning abilities, we introduce \textbf{ORION}, a challenging benchmark focused on open-web reasoning over long-tail entities, covering both English and Chinese. Experimental results show that ManuSearch substantially outperforms prior open-source baselines and even surpasses leading closed-source systems. Our work paves the way for reproducible, extensible research in open deep search systems. We release the data and code in https://github.com/RUCAIBox/ManuSearch

---

## LLM Agents for Interactive Workflow Provenance: Reference Architecture and Evaluation Methodology

**Authors:** Renan Souza, Timothy Poteet, Brian Etz, Daniel Rosendo, Amal Gueroudji, Woong Shin, Prasanna Balaprakash, Rafael Ferreira da Silva

**Published:** 2025-09-17T13:51:29Z

**Categories:** cs.DC, cs.AI, cs.DB

**Links:** [Abstract](https://arxiv.org/abs/2509.13978v2) | [PDF](https://arxiv.org/pdf/2509.13978v2)

**Abstract:**
Modern scientific discovery increasingly relies on workflows that process data across the Edge, Cloud, and High Performance Computing (HPC) continuum. Comprehensive and in-depth analyses of these data are critical for hypothesis validation, anomaly detection, reproducibility, and impactful findings. Although workflow provenance techniques support such analyses, at large scale, the provenance data become complex and difficult to analyze. Existing systems depend on custom scripts, structured queries, or static dashboards, limiting data interaction. In this work, we introduce an evaluation methodology, reference architecture, and open-source implementation that leverages interactive Large Language Model (LLM) agents for runtime data analysis. Our approach uses a lightweight, metadata-driven design that translates natural language into structured provenance queries. Evaluations across LLaMA, GPT, Gemini, and Claude, covering diverse query classes and a real-world chemistry workflow, show that modular design, prompt tuning, and Retrieval-Augmented Generation (RAG) enable accurate and insightful LLM agent responses beyond recorded provenance.

---

## Macaw-LLM: Multi-Modal Language Modeling with Image, Audio, Video, and Text Integration

**Authors:** Chenyang Lyu, Minghao Wu, Longyue Wang, Xinting Huang, Bingshuai Liu, Zefeng Du, Shuming Shi, Zhaopeng Tu

**Published:** 2023-06-15T12:45:25Z

**Categories:** cs.CL, cs.AI, cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2306.09093v1) | [PDF](https://arxiv.org/pdf/2306.09093v1)

**Abstract:**
Although instruction-tuned large language models (LLMs) have exhibited remarkable capabilities across various NLP tasks, their effectiveness on other data modalities beyond text has not been fully studied. In this work, we propose Macaw-LLM, a novel multi-modal LLM that seamlessly integrates visual, audio, and textual information. Macaw-LLM consists of three main components: a modality module for encoding multi-modal data, a cognitive module for harnessing pretrained LLMs, and an alignment module for harmonizing diverse representations. Our novel alignment module seamlessly bridges multi-modal features to textual features, simplifying the adaptation process from the modality modules to the cognitive module. In addition, we construct a large-scale multi-modal instruction dataset in terms of multi-turn dialogue, including 69K image instances and 50K video instances. We have made our data, code and model publicly available, which we hope can pave the way for future research in multi-modal LLMs and expand the capabilities of LLMs to handle diverse data modalities and address complex real-world scenarios.

---

## Collaborate, Deliberate, Evaluate: How LLM Alignment Affects Coordinated Multi-Agent Outcomes

**Authors:** Abhijnan Nath, Carine Graff, Nikhil Krishnaswamy

**Published:** 2025-09-07T00:58:10Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2509.05882v2) | [PDF](https://arxiv.org/pdf/2509.05882v2)

**Abstract:**
As Large Language Models (LLMs) get integrated into diverse workflows, they are increasingly being regarded as "collaborators" with humans, and required to work in coordination with other AI systems. If such AI collaborators are to reliably coordinate their actions and behaviors with humans or other AIs, their properties and behaviors over multi-turn interactions must be known and predictable. This paper examines how different alignment methods affect LLM agents' effectiveness as partners in multi-turn, multi-party collaborations. We study this question through the lens of intervention agents that insert themselves into group dialogues not to provide answers, but to encourage the collaborative group to slow down and reflect upon their reasoning for deliberative decision-making. Common alignment techniques are typically developed under simplified single-user settings and assume the optimality of the underlying token MDP. Using the theoretical lens of the modified-action MDP, we show how they do not account for the dynamics of long-horizon multi-party interactions. We present a novel roleplay simulation methodology, where we align LLMs according to different methods and then deploy them in collaborative task dialogues to quantify how interventions affect the trajectory of group collaboration, belief alignment, and coordination. Our results show that an intervention agent that is robust to action modification significantly outperforms common alignment baselines in supporting correct task outcomes.

---

## LLM+MAP: Bimanual Robot Task Planning using Large Language Models and Planning Domain Definition Language

**Authors:** Kun Chu, Xufeng Zhao, Cornelius Weber, Stefan Wermter

**Published:** 2025-03-21T17:04:01Z

**Categories:** cs.RO, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2503.17309v1) | [PDF](https://arxiv.org/pdf/2503.17309v1)

**Abstract:**
Bimanual robotic manipulation provides significant versatility, but also presents an inherent challenge due to the complexity involved in the spatial and temporal coordination between two hands. Existing works predominantly focus on attaining human-level manipulation skills for robotic hands, yet little attention has been paid to task planning on long-horizon timescales. With their outstanding in-context learning and zero-shot generation abilities, Large Language Models (LLMs) have been applied and grounded in diverse robotic embodiments to facilitate task planning. However, LLMs still suffer from errors in long-horizon reasoning and from hallucinations in complex robotic tasks, lacking a guarantee of logical correctness when generating the plan. Previous works, such as LLM+P, extended LLMs with symbolic planners. However, none have been successfully applied to bimanual robots. New challenges inevitably arise in bimanual manipulation, necessitating not only effective task decomposition but also efficient task allocation. To address these challenges, this paper introduces LLM+MAP, a bimanual planning framework that integrates LLM reasoning and multi-agent planning, automating effective and efficient bimanual task planning. We conduct simulated experiments on various long-horizon manipulation tasks of differing complexity. Our method is built using GPT-4o as the backend, and we compare its performance against plans generated directly by LLMs, including GPT-4o, V3 and also recent strong reasoning models o1 and R1. By analyzing metrics such as planning time, success rate, group debits, and planning-step reduction rate, we demonstrate the superior performance of LLM+MAP, while also providing insights into robotic reasoning. Code is available at https://github.com/Kchu/LLM-MAP.

---

## Modeling Layered Consciousness with Multi-Agent Large Language Models

**Authors:** Sang Hun Kim, Jongmin Lee, Dongkyu Park, So Young Lee, Yosep Chong

**Published:** 2025-10-10T07:08:34Z

**Categories:** cs.CL, cs.AI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2510.17844v1) | [PDF](https://arxiv.org/pdf/2510.17844v1)

**Abstract:**
We propose a multi-agent framework for modeling artificial consciousness in large language models (LLMs), grounded in psychoanalytic theory. Our \textbf{Psychodynamic Model} simulates self-awareness, preconsciousness, and unconsciousness through agent interaction, guided by a Personalization Module combining fixed traits and dynamic needs. Using parameter-efficient fine-tuning on emotionally rich dialogues, the system was evaluated across eight personalized conditions. An LLM as a judge approach showed a 71.2\% preference for the fine-tuned model, with improved emotional depth and reduced output variance, demonstrating its potential for adaptive, personalized cognition.

---

## AutoHarness: improving LLM agents by automatically synthesizing a code harness

**Authors:** Xinghua Lou, Miguel Lázaro-Gredilla, Antoine Dedieu, Carter Wendelken, Wolfgang Lehrach, Kevin P. Murphy

**Published:** 2026-02-10T14:12:54Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2603.03329v1) | [PDF](https://arxiv.org/pdf/2603.03329v1)

**Abstract:**
Despite significant strides in language models in the last few years, when used as agents, such models often try to perform actions that are not just suboptimal for a given state, but are strictly prohibited by the external environment. For example, in the recent Kaggle GameArena chess competition, 78% of Gemini-2.5-Flash losses were attributed to illegal moves. Often people manually write "harnesses" around LLMs to prevent such failures. In this paper, we demonstrate that Gemini-2.5-Flash can automatically synthesize such a code harness, using a small number of rounds of iterative code refinement given feedback from the (game) environment. The resulting harness prevents all illegal moves in 145 different TextArena games (both 1-player and 2-player), enabling the smaller Gemini-2.5-Flash model to outperform larger models, such as Gemini-2.5-Pro. Pushing our technique to the limit, we can get Gemini-2.5-Flash to generate the entire policy in code, thus eliminating the need to use the LLM at decision making time. The resulting code-policy receives a higher average reward than Gemini-2.5-Pro and GPT-5.2-High on 16 TextArena 1-player games. Our results show that using a smaller model to synthesize a custom code harness (or entire policy) can outperform a much larger model, while also being more cost effective.

---

## Jais and Jais-chat: Arabic-Centric Foundation and Instruction-Tuned Open Generative Large Language Models

**Authors:** Neha Sengupta, Sunil Kumar Sahu, Bokang Jia, Satheesh Katipomu, Haonan Li, Fajri Koto, William Marshall, Gurpreet Gosal, Cynthia Liu, Zhiming Chen, Osama Mohammed Afzal, Samta Kamboj, Onkar Pandit, Rahul Pal, Lalit Pradhan, Zain Muhammad Mujahid, Massa Baali, Xudong Han, Sondos Mahmoud Bsharat, Alham Fikri Aji, Zhiqiang Shen, Zhengzhong Liu, Natalia Vassilieva, Joel Hestness, Andy Hock, Andrew Feldman, Jonathan Lee, Andrew Jackson, Hector Xuguang Ren, Preslav Nakov, Timothy Baldwin, Eric Xing

**Published:** 2023-08-30T17:07:17Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2308.16149v2) | [PDF](https://arxiv.org/pdf/2308.16149v2)

**Abstract:**
We introduce Jais and Jais-chat, new state-of-the-art Arabic-centric foundation and instruction-tuned open generative large language models (LLMs). The models are based on the GPT-3 decoder-only architecture and are pretrained on a mixture of Arabic and English texts, including source code in various programming languages. With 13 billion parameters, they demonstrate better knowledge and reasoning capabilities in Arabic than any existing open Arabic and multilingual models by a sizable margin, based on extensive evaluation. Moreover, the models are competitive in English compared to English-centric open models of similar size, despite being trained on much less English data. We provide a detailed description of the training, the tuning, the safety alignment, and the evaluation of the models. We release two open versions of the model -- the foundation Jais model, and an instruction-tuned Jais-chat variant -- with the aim of promoting research on Arabic LLMs. Available at https://huggingface.co/inception-mbzuai/jais-13b-chat

---

## One Billion Word Benchmark for Measuring Progress in Statistical Language Modeling

**Authors:** Ciprian Chelba, Tomas Mikolov, Mike Schuster, Qi Ge, Thorsten Brants, Phillipp Koehn, Tony Robinson

**Published:** 2013-12-11T00:25:57Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/1312.3005v3) | [PDF](https://arxiv.org/pdf/1312.3005v3)

**Abstract:**
We propose a new benchmark corpus to be used for measuring progress in statistical language modeling. With almost one billion words of training data, we hope this benchmark will be useful to quickly evaluate novel language modeling techniques, and to compare their contribution when combined with other advanced techniques. We show performance of several well-known types of language models, with the best results achieved with a recurrent neural network based language model. The baseline unpruned Kneser-Ney 5-gram model achieves perplexity 67.6; a combination of techniques leads to 35% reduction in perplexity, or 10% reduction in cross-entropy (bits), over that baseline.
  The benchmark is available as a code.google.com project; besides the scripts needed to rebuild the training/held-out data, it also makes available log-probability values for each word in each of ten held-out data sets, for each of the baseline n-gram models.

---

## Motion-Agent: A Conversational Framework for Human Motion Generation with LLMs

**Authors:** Qi Wu, Yubo Zhao, Yifan Wang, Xinhang Liu, Yu-Wing Tai, Chi-Keung Tang

**Published:** 2024-05-27T09:57:51Z

**Categories:** cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2405.17013v3) | [PDF](https://arxiv.org/pdf/2405.17013v3)

**Abstract:**
While previous approaches to 3D human motion generation have achieved notable success, they often rely on extensive training and are limited to specific tasks. To address these challenges, we introduce Motion-Agent, an efficient conversational framework designed for general human motion generation, editing, and understanding. Motion-Agent employs an open-source pre-trained language model to develop a generative agent, MotionLLM, that bridges the gap between motion and text. This is accomplished by encoding and quantizing motions into discrete tokens that align with the language model's vocabulary. With only 1--3\% of the model's parameters fine-tuned using adapters, MotionLLM delivers performance on par with diffusion models and other transformer-based methods trained from scratch. By integrating MotionLLM with GPT-4 without additional training, Motion-Agent is able to generate highly complex motion sequences through multi-turn conversations, a capability that previous models have struggled to achieve. Motion-Agent supports a wide range of motion-language tasks, offering versatile capabilities for generating and customizing human motion through interactive conversational exchanges. Project page: https://knoxzhao.github.io/Motion-Agent

---

## Task Memory Engine (TME): Enhancing State Awareness for Multi-Step LLM Agent Tasks

**Authors:** Ye Ye

**Published:** 2025-04-11T13:38:36Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2504.08525v4) | [PDF](https://arxiv.org/pdf/2504.08525v4)

**Abstract:**
Large Language Models (LLMs) are increasingly used as autonomous agents for multi-step tasks. However, most existing frameworks fail to maintain a structured understanding of the task state, often relying on linear prompt concatenation or shallow memory buffers. This leads to brittle performance, frequent hallucinations, and poor long-range coherence. In this work, we propose the Task Memory Engine (TME), a lightweight and structured memory module that tracks task execution using a hierarchical Task Memory Tree (TMT). Each node in the tree corresponds to a task step, storing relevant input, output, status, and sub-task relationships. We introduce a prompt synthesis method that dynamically generates LLM prompts based on the active node path, significantly improving execution consistency and contextual grounding. Through case studies and comparative experiments on multi-step agent tasks, we demonstrate that TME leads to better task completion accuracy and more interpretable behavior with minimal implementation overhead. A reference implementation of the core TME components is available at https://github.com/biubiutomato/TME-Agent, including basic examples and structured memory integration. While the current implementation uses a tree-based structure, TME is designed to be graph-aware, supporting reusable substeps, converging task paths, and shared dependencies. This lays the groundwork for future DAG-based memory architectures.

---

## Mobile-Agent: Autonomous Multi-Modal Mobile Device Agent with Visual Perception

**Authors:** Junyang Wang, Haiyang Xu, Jiabo Ye, Ming Yan, Weizhou Shen, Ji Zhang, Fei Huang, Jitao Sang

**Published:** 2024-01-29T13:46:37Z

**Categories:** cs.CL, cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2401.16158v2) | [PDF](https://arxiv.org/pdf/2401.16158v2)

**Abstract:**
Mobile device agent based on Multimodal Large Language Models (MLLM) is becoming a popular application. In this paper, we introduce Mobile-Agent, an autonomous multi-modal mobile device agent. Mobile-Agent first leverages visual perception tools to accurately identify and locate both the visual and textual elements within the app's front-end interface. Based on the perceived vision context, it then autonomously plans and decomposes the complex operation task, and navigates the mobile Apps through operations step by step. Different from previous solutions that rely on XML files of Apps or mobile system metadata, Mobile-Agent allows for greater adaptability across diverse mobile operating environments in a vision-centric way, thereby eliminating the necessity for system-specific customizations. To assess the performance of Mobile-Agent, we introduced Mobile-Eval, a benchmark for evaluating mobile device operations. Based on Mobile-Eval, we conducted a comprehensive evaluation of Mobile-Agent. The experimental results indicate that Mobile-Agent achieved remarkable accuracy and completion rates. Even with challenging instructions, such as multi-app operations, Mobile-Agent can still complete the requirements. Code and model will be open-sourced at https://github.com/X-PLUG/MobileAgent.

---

## Strategist: Self-improvement of LLM Decision Making via Bi-Level Tree Search

**Authors:** Jonathan Light, Min Cai, Weiqin Chen, Guanzhi Wang, Xiusi Chen, Wei Cheng, Yisong Yue, Ziniu Hu

**Published:** 2024-08-20T08:22:04Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2408.10635v3) | [PDF](https://arxiv.org/pdf/2408.10635v3)

**Abstract:**
Traditional reinforcement learning and planning typically requires vast amounts of data and training to develop effective policies. In contrast, large language models (LLMs) exhibit strong generalization and zero-shot capabilities, but struggle with tasks that require detailed planning and decision-making in complex action spaces. We introduce STRATEGIST, a novel approach that integrates the strengths of both methods. Our approach leverages LLMs to search and update high-level strategies (as text), which are then refined and executed by low-level Monte Carlo Tree Search (MCTS). STRATEGIST is a generalizable framework to optimize the strategy through population-based self-play simulations without the need for any training data. We demonstrate the effectiveness of STRATEGIST in learning optimal strategies for competitive, multi-turn games with partial information, including Game of Pure Strategy (GOPS) and multi-agent, hidden-identity discussion games like The Resistance: Avalon. Our results show that agents equipped with STRATEGIST outperform those trained with traditional RL methods, other LLM-based skill acquisition techniques, pre-existing LLM agents across both game environments and achieves comparable performance against human players.

---

## PediatricsGPT: Large Language Models as Chinese Medical Assistants for Pediatric Applications

**Authors:** Dingkang Yang, Jinjie Wei, Dongling Xiao, Shunli Wang, Tong Wu, Gang Li, Mingcheng Li, Shuaibing Wang, Jiawei Chen, Yue Jiang, Qingyao Xu, Ke Li, Peng Zhai, Lihua Zhang

**Published:** 2024-05-29T16:59:38Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2405.19266v4) | [PDF](https://arxiv.org/pdf/2405.19266v4)

**Abstract:**
Developing intelligent pediatric consultation systems offers promising prospects for improving diagnostic efficiency, especially in China, where healthcare resources are scarce. Despite recent advances in Large Language Models (LLMs) for Chinese medicine, their performance is sub-optimal in pediatric applications due to inadequate instruction data and vulnerable training procedures. To address the above issues, this paper builds PedCorpus, a high-quality dataset of over 300,000 multi-task instructions from pediatric textbooks, guidelines, and knowledge graph resources to fulfil diverse diagnostic demands. Upon well-designed PedCorpus, we propose PediatricsGPT, the first Chinese pediatric LLM assistant built on a systematic and robust training pipeline. In the continuous pre-training phase, we introduce a hybrid instruction pre-training mechanism to mitigate the internal-injected knowledge inconsistency of LLMs for medical domain adaptation. Immediately, the full-parameter Supervised Fine-Tuning (SFT) is utilized to incorporate the general medical knowledge schema into the models. After that, we devise a direct following preference optimization to enhance the generation of pediatrician-like humanistic responses. In the parameter-efficient secondary SFT phase, a mixture of universal-specific experts strategy is presented to resolve the competency conflict between medical generalist and pediatric expertise mastery. Extensive results based on the metrics, GPT-4, and doctor evaluations on distinct doctor downstream tasks show that PediatricsGPT consistently outperforms previous Chinese medical LLMs. Our model and dataset will be open-source for community development.

---

## Augmenting the action space with conventions to improve multi-agent cooperation in Hanabi

**Authors:** F. Bredell, H. A. Engelbrecht, J. C. Schoeman

**Published:** 2024-12-09T09:34:40Z

**Categories:** cs.MA, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2412.06333v3) | [PDF](https://arxiv.org/pdf/2412.06333v3)

**Abstract:**
The card game Hanabi is considered a strong medium for the testing and development of multi-agent reinforcement learning (MARL) algorithms, due to its cooperative nature, partial observability, limited communication and remarkable complexity. Previous research efforts have explored the capabilities of MARL algorithms within Hanabi, focusing largely on advanced architecture design and algorithmic manipulations to achieve state-of-the-art performance for various number of cooperators. However, this often leads to complex solution strategies with high computational cost and requiring large amounts of training data. For humans to solve the Hanabi game effectively, they require the use of conventions, which often allows for a means to implicitly convey ideas or knowledge based on a predefined, and mutually agreed upon, set of "rules" or principles. Multi-agent problems containing partial observability, especially when limited communication is present, can benefit greatly from the use of implicit knowledge sharing. In this paper, we propose a novel approach to augmenting an agent's action space using conventions, which act as a sequence of special cooperative actions that span over and include multiple time steps and multiple agents, requiring agents to actively opt in for it to reach fruition. These conventions are based on existing human conventions, and result in a significant improvement on the performance of existing techniques for self-play and cross-play for various number of cooperators within Hanabi.

---

## Multi-Agent LLM Orchestration Achieves Deterministic, High-Quality Decision Support for Incident Response

**Authors:** Philip Drammeh

**Published:** 2025-11-19T06:06:11Z

**Categories:** cs.AI, cs.SE

**Links:** [Abstract](https://arxiv.org/abs/2511.15755v2) | [PDF](https://arxiv.org/pdf/2511.15755v2)

**Abstract:**
Large language models (LLMs) promise to accelerate incident response in production systems, yet single-agent approaches generate vague, unusable recommendations. We present MyAntFarm.ai, a reproducible containerized framework demonstrating that multi-agent orchestration fundamentally transforms LLM-based incident response quality. Through 348 controlled trials comparing single-agent copilot versus multi-agent systems on identical incident scenarios, we find that multi-agent orchestration achieves 100% actionable recommendation rate versus 1.7% for single-agent approaches, an 80 times improvement in action specificity and 140 times improvement in solution correctness. Critically, multi-agent systems exhibit zero quality variance across all trials, enabling production SLA commitments impossible with inconsistent single-agent outputs. Both architectures achieve similar comprehension latency (approx.40s), establishing that the architectural value lies in deterministic quality, not speed. We introduce Decision Quality (DQ), a novel metric capturing validity, specificity, and correctness properties essential for operational deployment that existing LLM metrics do not address. These findings reframe multi-agent orchestration from a performance optimization to a production-readiness requirement for LLM-based incident response. All code, Docker configurations, and trial data are publicly available for reproduction.

---

## A Language Agent for Autonomous Driving

**Authors:** Jiageng Mao, Junjie Ye, Yuxi Qian, Marco Pavone, Yue Wang

**Published:** 2023-11-17T18:59:56Z

**Categories:** cs.CV, cs.AI, cs.CL, cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2311.10813v4) | [PDF](https://arxiv.org/pdf/2311.10813v4)

**Abstract:**
Human-level driving is an ultimate goal of autonomous driving. Conventional approaches formulate autonomous driving as a perception-prediction-planning framework, yet their systems do not capitalize on the inherent reasoning ability and experiential knowledge of humans. In this paper, we propose a fundamental paradigm shift from current pipelines, exploiting Large Language Models (LLMs) as a cognitive agent to integrate human-like intelligence into autonomous driving systems. Our approach, termed Agent-Driver, transforms the traditional autonomous driving pipeline by introducing a versatile tool library accessible via function calls, a cognitive memory of common sense and experiential knowledge for decision-making, and a reasoning engine capable of chain-of-thought reasoning, task planning, motion planning, and self-reflection. Powered by LLMs, our Agent-Driver is endowed with intuitive common sense and robust reasoning capabilities, thus enabling a more nuanced, human-like approach to autonomous driving. We evaluate our approach on the large-scale nuScenes benchmark, and extensive experiments substantiate that our Agent-Driver significantly outperforms the state-of-the-art driving methods by a large margin. Our approach also demonstrates superior interpretability and few-shot learning ability to these methods.

---

## Causal Agent based on Large Language Model

**Authors:** Kairong Han, Kun Kuang, Ziyu Zhao, Junjian Ye, Fei Wu

**Published:** 2024-08-13T12:22:26Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2408.06849v2) | [PDF](https://arxiv.org/pdf/2408.06849v2)

**Abstract:**
The large language model (LLM) has achieved significant success across various domains. However, the inherent complexity of causal problems and causal theory poses challenges in accurately describing them in natural language, making it difficult for LLM to comprehend and use them effectively. Causal methods are not easily conveyed through natural language, which hinders LLM's ability to apply them accurately. Additionally, causal datasets are typically tabular, while LLM excels in handling natural language data, creating a structural mismatch that impedes effective reasoning with tabular data. To address these challenges, we have equipped the LLM with causal tools within an agent framework, named the Causal Agent, enabling it to tackle causal problems. The causal agent comprises tools, memory, and reasoning modules. In the tool module, the causal agent calls Python code and uses the encapsulated causal function module to align tabular data with natural language. In the reasoning module, the causal agent performs reasoning through multiple iterations with the tools. In the memory module, the causal agent maintains a dictionary instance where the keys are unique names and the values are causal graphs. To verify the causal ability of the causal agent, we established a Causal Tabular Question Answer (CausalTQA) benchmark consisting of four levels of causal problems: variable level, edge level, causal graph level, and causal effect level. CausalTQA consists of about 1.4K for these four levels questions. Causal agent demonstrates remarkable efficacy on the four-level causal problems, with accuracy rates all above 80\%. Through verification on the real-world dataset QRData, the causal agent is 6\% higher than the original SOTA. For further insights and implementation details, our code is accessible via the GitHub repository https://github.com/kairong-han/causal_agent.

---

## From Model-Based Screening to Data-Driven Surrogates: A Multi-Stage Workflow for Exploring Stochastic Agent-Based Models

**Authors:** Paul Saves, Matthieu Mastio, Nicolas Verstaevel, Benoit Gaudou

**Published:** 2026-04-03T15:32:49Z

**Categories:** cs.LG, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2604.03350v1) | [PDF](https://arxiv.org/pdf/2604.03350v1)

**Abstract:**
Systematic exploration of Agent-Based Models (ABMs) is challenged by the curse of dimensionality and their inherent stochasticity. We present a multi-stage pipeline integrating the systematic design of experiments with machine learning surrogates. Using a predator-prey case study, our methodology proceeds in two steps. First, an automated model-based screening identifies dominant variables, assesses outcome variability, and segments the parameter space. Second, we train Machine Learning models to map the remaining nonlinear interaction effects. This approach automates the discovery of unstable regions where system outcomes are highly dependent on nonlinear interactions between many variables. Thus, this work provides modelers with a rigorous, hands-off framework for sensitivity analysis and policy testing, even when dealing with high-dimensional stochastic simulators.

---

## Systematic Evaluation of LLM-as-a-Judge in LLM Alignment Tasks: Explainable Metrics and Diverse Prompt Templates

**Authors:** Hui Wei, Shenghua He, Tian Xia, Fei Liu, Andy Wong, Jingyang Lin, Mei Han

**Published:** 2024-08-23T11:49:01Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2408.13006v2) | [PDF](https://arxiv.org/pdf/2408.13006v2)

**Abstract:**
LLM-as-a-Judge has been widely applied to evaluate and compare different LLM alignmnet approaches (e.g., RLHF and DPO). However, concerns regarding its reliability have emerged, due to LLM judges' biases and inconsistent decision-making. Previous research has developed evaluation frameworks to assess reliability of LLM judges and their alignment with human preferences. However, the employed evaluation metrics often lack adequate explainability and fail to address LLM internal inconsistency. Additionally, existing studies inadequately explore the impact of various prompt templates when applying LLM-as-a-Judge methods, leading to potentially inconsistent comparisons between different alignment algorithms. In this work, we systematically evaluate LLM-as-a-Judge on alignment tasks by defining more theoretically interpretable evaluation metrics and explicitly mitigating LLM internal inconsistency from reliability metrics. We develop an open-source framework to evaluate, compare, and visualize the reliability and alignment of LLM judges, which facilitates practitioners to choose LLM judges for alignment tasks. In the experiments, we examine effects of diverse prompt templates on LLM-judge reliability and also demonstrate our developed framework by comparing various LLM judges on two common alignment datasets (i.e., TL;DR Summarization and HH-RLHF-Helpfulness). Our results indicate a significant impact of prompt templates on LLM judge performance, as well as a mediocre alignment level between the tested LLM judges and human evaluators.

---

## Agent Banana: High-Fidelity Image Editing with Agentic Thinking and Tooling

**Authors:** Ruijie Ye, Jiayi Zhang, Zhuoxin Liu, Zihao Zhu, Siyuan Yang, Li Li, Tianfu Fu, Franck Dernoncourt, Yue Zhao, Jiacheng Zhu, Ryan Rossi, Wenhao Chai, Zhengzhong Tu

**Published:** 2026-02-09T18:59:18Z

**Categories:** cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2602.09084v2) | [PDF](https://arxiv.org/pdf/2602.09084v2)

**Abstract:**
We study instruction-based image editing under professional workflows and identify three persistent challenges: (i) editors often over-edit, modifying content beyond the user's intent; (ii) existing models are largely single-turn, while multi-turn edits can alter object faithfulness; and (iii) evaluation at around 1K resolution is misaligned with real workflows that often operate on ultra high-definition images (e.g., 4K). We propose Agent Banana, a hierarchical agentic planner-executor framework for high-fidelity, object-aware, deliberative editing. Agent Banana introduces two key mechanisms: (1) Context Folding, which compresses long interaction histories into structured memory for stable long-horizon control; and (2) Image Layer Decomposition, which performs localized layer-based edits to preserve non-target regions while enabling native-resolution outputs. To support rigorous evaluation, we build HDD-Bench, a high-definition, dialogue-based benchmark featuring verifiable stepwise targets and native 4K images (11.8M pixels) for diagnosing long-horizon failures. On HDD-Bench, Agent Banana achieves the best multi-turn consistency and background fidelity (e.g., IC 0.871, SSIM-OM 0.84, LPIPS-OM 0.12) while remaining competitive on instruction following, and also attains strong performance on standard single-turn editing benchmarks. We hope this work advances reliable, professional-grade agentic image editing and its integration into real workflows.

---

## Hidden in Plain Text: Measuring LLM Deception Quality Against Human Baselines Using Social Deduction Games

**Authors:** Christopher Kao, Vanshika Vats, James Davis

**Published:** 2026-01-20T08:07:21Z

**Categories:** cs.AI, cs.CL, cs.CY, cs.HC, cs.SI

**Links:** [Abstract](https://arxiv.org/abs/2601.13709v1) | [PDF](https://arxiv.org/pdf/2601.13709v1)

**Abstract:**
Large Language Model (LLM) agents are increasingly used in many applications, raising concerns about their safety. While previous work has shown that LLMs can deceive in controlled tasks, less is known about their ability to deceive using natural language in social contexts. In this paper, we study deception in the Social Deduction Game (SDG) Mafia, where success is dependent on deceiving others through conversation. Unlike previous SDG studies, we use an asynchronous multi-agent framework which better simulates realistic social contexts. We simulate 35 Mafia games with GPT-4o LLM agents. We then create a Mafia Detector using GPT-4-Turbo to analyze game transcripts without player role information to predict the mafia players. We use prediction accuracy as a surrogate marker for deception quality. We compare this prediction accuracy to that of 28 human games and a random baseline. Results show that the Mafia Detector's mafia prediction accuracy is lower on LLM games than on human games. The result is consistent regardless of the game days and the number of mafias detected. This indicates that LLMs blend in better and thus deceive more effectively. We also release a dataset of LLM Mafia transcripts to support future research. Our findings underscore both the sophistication and risks of LLM deception in social contexts.

---

## Youtu-LLM: Unlocking the Native Agentic Potential for Lightweight Large Language Models

**Authors:** Junru Lu, Jiarui Qin, Lingfeng Qiao, Yinghui Li, Xinyi Dai, Bo Ke, Jianfeng He, Ruizhi Qiao, Di Yin, Xing Sun, Yunsheng Wu, Yinsong Liu, Shuangyin Liu, Mingkong Tang, Haodong Lin, Jiayi Kuang, Fanxu Meng, Xiaojuan Tang, Yunjia Xi, Junjie Huang, Haotong Yang, Zhenyi Shen, Yangning Li, Qianwen Zhang, Yifei Yu, Siyu An, Junnan Dong, Qiufeng Wang, Jie Wang, Keyu Chen, Wei Wen, Taian Guo, Zhifeng Shen, Daohai Yu, Jiahao Li, Ke Li, Zongyi Li, Xiaoyu Tan

**Published:** 2025-12-31T04:25:11Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2512.24618v2) | [PDF](https://arxiv.org/pdf/2512.24618v2)

**Abstract:**
We introduce Youtu-LLM, a lightweight yet powerful language model that harmonizes high computational efficiency with native agentic intelligence. Unlike typical small models that rely on distillation, Youtu-LLM (1.96B) is pre-trained from scratch to systematically cultivate reasoning and planning capabilities. The key technical advancements are as follows: (1) Compact Architecture with Long-Context Support: Built on a dense Multi-Latent Attention (MLA) architecture with a novel STEM-oriented vocabulary, Youtu-LLM supports a 128k context window. This design enables robust long-context reasoning and state tracking within a minimal memory footprint, making it ideal for long-horizon agent and reasoning tasks. (2) Principled "Commonsense-STEM-Agent" Curriculum: We curated a massive corpus of approximately 11T tokens and implemented a multi-stage training strategy. By progressively shifting the pre-training data distribution from general commonsense to complex STEM and agentic tasks, we ensure the model acquires deep cognitive abilities rather than superficial alignment. (3) Scalable Agentic Mid-training: Specifically for the agentic mid-training, we employ diverse data construction schemes to synthesize rich and varied trajectories across math, coding, and tool-use domains. This high-quality data enables the model to internalize planning and reflection behaviors effectively. Extensive evaluations show that Youtu-LLM sets a new state-of-the-art for sub-2B LLMs. On general benchmarks, it achieves competitive performance against larger models, while on agent-specific tasks, it significantly surpasses existing SOTA baselines, demonstrating that lightweight models can possess strong intrinsic agentic capabilities.

---

## Large Language Model-Brained GUI Agents: A Survey

**Authors:** Chaoyun Zhang, Shilin He, Jiaxu Qian, Bowen Li, Liqun Li, Si Qin, Yu Kang, Minghua Ma, Guyue Liu, Qingwei Lin, Saravan Rajmohan, Dongmei Zhang, Qi Zhang

**Published:** 2024-11-27T12:13:39Z

**Categories:** cs.AI, cs.CL, cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2411.18279v12) | [PDF](https://arxiv.org/pdf/2411.18279v12)

**Abstract:**
GUIs have long been central to human-computer interaction, providing an intuitive and visually-driven way to access and interact with digital systems. The advent of LLMs, particularly multimodal models, has ushered in a new era of GUI automation. They have demonstrated exceptional capabilities in natural language understanding, code generation, and visual processing. This has paved the way for a new generation of LLM-brained GUI agents capable of interpreting complex GUI elements and autonomously executing actions based on natural language instructions. These agents represent a paradigm shift, enabling users to perform intricate, multi-step tasks through simple conversational commands. Their applications span across web navigation, mobile app interactions, and desktop automation, offering a transformative user experience that revolutionizes how individuals interact with software. This emerging field is rapidly advancing, with significant progress in both research and industry.
  To provide a structured understanding of this trend, this paper presents a comprehensive survey of LLM-brained GUI agents, exploring their historical evolution, core components, and advanced techniques. We address research questions such as existing GUI agent frameworks, the collection and utilization of data for training specialized GUI agents, the development of large action models tailored for GUI tasks, and the evaluation metrics and benchmarks necessary to assess their effectiveness. Additionally, we examine emerging applications powered by these agents. Through a detailed analysis, this survey identifies key research gaps and outlines a roadmap for future advancements in the field. By consolidating foundational knowledge and state-of-the-art developments, this work aims to guide both researchers and practitioners in overcoming challenges and unlocking the full potential of LLM-brained GUI agents.

---

## Synergy: A Next-Generation General-Purpose Agent for Open Agentic Web

**Authors:** Xiaohang Nie, Zihan Guo, Kezhuo Yang, Zhichong Zheng, Bochen Ge, Shuai Pan, Zeyi Chen, Youling Xiang, Yu Zhang, Weiwen Liu, Yuanjian Zhou, Weinan Zhang

**Published:** 2026-03-30T13:35:37Z

**Categories:** cs.CY, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2603.28428v1) | [PDF](https://arxiv.org/pdf/2603.28428v1)

**Abstract:**
AI agents are rapidly expanding in both capability and population: they now write code, operate computers across platforms, manage cloud infrastructure, and make purchasing decisions, while open-source frameworks such as OpenClaw are putting personal agents in the hands of millions and embodied agents are spreading across smartphones, vehicles, and robots. As the internet prepares to host billions of such entities, it is shifting toward what we call Open Agentic Web, a decentralized digital ecosystem in which agents from different users, organizations, and runtimes can discover one another, negotiate task boundaries, and delegate work across open technical and social surfaces at scale. Yet most of today's agents remain isolated tools or closed-ecosystem orchestrators rather than socially integrated participants in open networks. We argue that the next generation of agents must become Agentic Citizens, defined by three requirements: Agentic-Web-Native Collaboration, participation in open collaboration networks rather than only closed internal orchestration; Agent Identity and Personhood, continuity as a social entity rather than a resettable function call; and Lifelong Evolution, improvement across task performance, communication, and collaboration over time. We present Synergy, a general-purpose agent architecture and runtime harness for persistent, collaborative, and evolving agents on Open Agentic Web, grounding collaboration in session-native orchestration, repository-backed workspaces, and social communication; identity in typed memory, notes, agenda, skills, and persistent social relationships; and evolution in an experience-centered learning mechanism that proactively recalls rewarded trajectories at inference time.

---

## LLM-42: Enabling Determinism in LLM Inference with Verified Speculation

**Authors:** Raja Gond, Aditya K Kamath, Ramachandran Ramjee, Ashish Panwar

**Published:** 2026-01-25T09:58:57Z

**Categories:** cs.LG, cs.AI, cs.DC

**Links:** [Abstract](https://arxiv.org/abs/2601.17768v2) | [PDF](https://arxiv.org/pdf/2601.17768v2)

**Abstract:**
In LLM inference, the same prompt may yield different outputs across different runs. At the system level, this non-determinism arises from floating-point non-associativity combined with dynamic batching and GPU kernels whose reduction orders vary with batch size. A straightforward way to eliminate non-determinism is to disable dynamic batching during inference, but doing so severely degrades throughput. Another approach is to make kernels batch-invariant; however, this tightly couples determinism to kernel design, requiring new implementations. This coupling also imposes fixed runtime overheads, regardless of how much of the workload actually requires determinism.
  Inspired by ideas from speculative decoding, we present LLM-42, a scheduling-based approach to enable determinism in LLM inference. Our key observation is that if a sequence is in a consistent state, the next emitted token is likely to be consistent even with dynamic batching. Moreover, most GPU kernels use shape-consistent reductions. Leveraging these insights, LLM-42 decodes tokens using a non-deterministic fast path and enforces determinism via a lightweight verify-rollback loop. The verifier replays candidate tokens under a fixed-shape reduction schedule, commits those that are guaranteed to be consistent across runs, and rolls back those violating determinism. LLM-42 mostly re-uses existing kernels unchanged and incurs overhead only in proportion to the traffic that requires determinism.

---

## LLM-Powered GUI Agents in Phone Automation: Surveying Progress and Prospects

**Authors:** Guangyi Liu, Pengxiang Zhao, Yaozhen Liang, Liang Liu, Yaxuan Guo, Han Xiao, Weifeng Lin, Yuxiang Chai, Yue Han, Shuai Ren, Hao Wang, Xiaoyu Liang, WenHao Wang, Tianze Wu, Zhengxi Lu, Siheng Chen, LiLinghao, Hao Wang, Guanjing Xiong, Yong Liu, Hongsheng Li

**Published:** 2025-04-28T14:39:25Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2504.19838v3) | [PDF](https://arxiv.org/pdf/2504.19838v3)

**Abstract:**
With the rapid rise of large language models (LLMs), phone automation has undergone transformative changes. This paper systematically reviews LLM-driven phone GUI agents, highlighting their evolution from script-based automation to intelligent, adaptive systems. We first contextualize key challenges, (i) limited generality, (ii) high maintenance overhead, and (iii) weak intent comprehension, and show how LLMs address these issues through advanced language understanding, multimodal perception, and robust decision-making. We then propose a taxonomy covering fundamental agent frameworks (single-agent, multi-agent, plan-then-act), modeling approaches (prompt engineering, training-based), and essential datasets and benchmarks. Furthermore, we detail task-specific architectures, supervised fine-tuning, and reinforcement learning strategies that bridge user intent and GUI operations. Finally, we discuss open challenges such as dataset diversity, on-device deployment efficiency, user-centric adaptation, and security concerns, offering forward-looking insights into this rapidly evolving field. By providing a structured overview and identifying pressing research gaps, this paper serves as a definitive reference for researchers and practitioners seeking to harness LLMs in designing scalable, user-friendly phone GUI agents. The collection of papers reviewed in this survey will be hosted and regularly updated on the GitHub repository: https://github.com/PhoneLLM/Awesome-LLM-Powered-Phone-GUI-Agents

---

## V2V-LLM: Vehicle-to-Vehicle Cooperative Autonomous Driving with Multimodal Large Language Models

**Authors:** Hsu-kuang Chiu, Ryo Hachiuma, Chien-Yi Wang, Stephen F. Smith, Yu-Chiang Frank Wang, Min-Hung Chen

**Published:** 2025-02-14T08:05:41Z

**Categories:** cs.CV, cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2502.09980v4) | [PDF](https://arxiv.org/pdf/2502.09980v4)

**Abstract:**
Current autonomous driving vehicles rely mainly on their individual sensors to understand surrounding scenes and plan for future trajectories, which can be unreliable when the sensors are malfunctioning or occluded. To address this problem, cooperative perception methods via vehicle-to-vehicle (V2V) communication have been proposed, but they have tended to focus on perception tasks like detection or tracking. How those approaches contribute to overall cooperative planning performance is still under-explored. Inspired by recent progress using Large Language Models (LLMs) to build autonomous driving systems, we propose a novel problem setting that integrates a Multimodal LLM into cooperative autonomous driving, with the proposed Vehicle-to-Vehicle Question-Answering (V2V-QA) dataset and benchmark. We also propose our baseline method Vehicle-to-Vehicle Multimodal Large Language Model (V2V-LLM), which uses an LLM to fuse perception information from multiple connected autonomous vehicles (CAVs) and answer various types of driving-related questions: grounding, notable object identification, and planning. Experimental results show that our proposed V2V-LLM can be a promising unified model architecture for performing various tasks in cooperative autonomous driving, and outperforms other baseline methods that use different fusion approaches. Our work also creates a new research direction that can improve the safety of future autonomous driving systems. The code and data will be released to the public to facilitate open-source research in this field. Our project website: https://eddyhkchiu.github.io/v2vllm.github.io/ .

---

## Competition and Cooperation of LLM Agents in Games

**Authors:** Jiayi Yao, Cong Chen, Baosen Zhang

**Published:** 2026-04-01T05:11:44Z

**Categories:** cs.MA, cs.GT, eess.SY

**Links:** [Abstract](https://arxiv.org/abs/2604.00487v1) | [PDF](https://arxiv.org/pdf/2604.00487v1)

**Abstract:**
Large language model (LLM) agents are increasingly deployed in competitive multi-agent settings, raising fundamental questions about whether they converge to equilibria and how their strategic behavior can be characterized. In this paper, we study LLM agent interactions in two standard games: a network resource allocation game and a Cournot competition game. Rather than converging to Nash equilibria, we find that LLM agents tend to cooperate when given multi-round prompts and non-zero-sum context. Chain-of-thought analysis reveals that fairness reasoning is central to this behavior. We propose an analytical framework that captures the dynamics of LLM agent reasoning across rounds and explains these experimental findings.

---

## LLM-SRBench: A New Benchmark for Scientific Equation Discovery with Large Language Models

**Authors:** Parshin Shojaee, Ngoc-Hieu Nguyen, Kazem Meidani, Amir Barati Farimani, Khoa D Doan, Chandan K Reddy

**Published:** 2025-04-14T17:00:13Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2504.10415v2) | [PDF](https://arxiv.org/pdf/2504.10415v2)

**Abstract:**
Scientific equation discovery is a fundamental task in the history of scientific progress, enabling the derivation of laws governing natural phenomena. Recently, Large Language Models (LLMs) have gained interest for this task due to their potential to leverage embedded scientific knowledge for hypothesis generation. However, evaluating the true discovery capabilities of these methods remains challenging, as existing benchmarks often rely on common equations that are susceptible to memorization by LLMs, leading to inflated performance metrics that do not reflect discovery. In this paper, we introduce LLM-SRBench, a comprehensive benchmark with 239 challenging problems across four scientific domains specifically designed to evaluate LLM-based scientific equation discovery methods while preventing trivial memorization. Our benchmark comprises two main categories: LSR-Transform, which transforms common physical models into less common mathematical representations to test reasoning beyond memorized forms, and LSR-Synth, which introduces synthetic, discovery-driven problems requiring data-driven reasoning. Through extensive evaluation of several state-of-the-art methods, using both open and closed LLMs, we find that the best-performing system so far achieves only 31.5% symbolic accuracy. These findings highlight the challenges of scientific equation discovery, positioning LLM-SRBench as a valuable resource for future research.

---

## GVGAI-LLM: Evaluating Large Language Model Agents with Infinite Games

**Authors:** Yuchen Li, Cong Lin, Muhammad Umair Nasir, Philip Bontrager, Jialin Liu, Julian Togelius

**Published:** 2025-08-11T22:17:07Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2508.08501v2) | [PDF](https://arxiv.org/pdf/2508.08501v2)

**Abstract:**
We introduce GVGAI-LLM, a video game benchmark for evaluating the reasoning and problem-solving capabilities of large language models (LLMs). Built on the General Video Game AI framework, it features a diverse collection of arcade-style games designed to test a model's ability to handle tasks that differ from most existing LLM benchmarks. The benchmark leverages a game description language that enables rapid creation of new games and levels, helping to prevent overfitting over time. Each game scene is represented by a compact set of ASCII characters, allowing for efficient processing by language models. GVGAI-LLM defines interpretable metrics, including the meaningful step ratio, step efficiency, and overall score, to assess model behavior. Through zero-shot evaluations across a broad set of games and levels with diverse challenges and skill depth, we reveal persistent limitations of LLMs in spatial reasoning and basic planning. Current models consistently exhibit spatial and logical errors, motivating structured prompting and spatial grounding techniques. While these interventions lead to partial improvements, the benchmark remains very far from solved. GVGAI-LLM provides a reproducible testbed for advancing research on language model capabilities, with a particular emphasis on agentic behavior and contextual reasoning.

---

## ML-Agent: Reinforcing LLM Agents for Autonomous Machine Learning Engineering

**Authors:** Zexi Liu, Jingyi Chai, Xinyu Zhu, Shuo Tang, Rui Ye, Bo Zhang, Lei Bai, Siheng Chen

**Published:** 2025-05-29T17:54:44Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2505.23723v1) | [PDF](https://arxiv.org/pdf/2505.23723v1)

**Abstract:**
The emergence of large language model (LLM)-based agents has significantly advanced the development of autonomous machine learning (ML) engineering. However, most existing approaches rely heavily on manual prompt engineering, failing to adapt and optimize based on diverse experimental experiences. Focusing on this, for the first time, we explore the paradigm of learning-based agentic ML, where an LLM agent learns through interactive experimentation on ML tasks using online reinforcement learning (RL). To realize this, we propose a novel agentic ML training framework with three key components: (1) exploration-enriched fine-tuning, which enables LLM agents to generate diverse actions for enhanced RL exploration; (2) step-wise RL, which enables training on a single action step, accelerating experience collection and improving training efficiency; (3) an agentic ML-specific reward module, which unifies varied ML feedback signals into consistent rewards for RL optimization. Leveraging this framework, we train ML-Agent, driven by a 7B-sized Qwen-2.5 LLM for autonomous ML. Remarkably, despite being trained on merely 9 ML tasks, our 7B-sized ML-Agent outperforms the 671B-sized DeepSeek-R1 agent. Furthermore, it achieves continuous performance improvements and demonstrates exceptional cross-task generalization capabilities.

---

## Permission Manifests for Web Agents

**Authors:** Samuele Marro, Alan Chan, Xinxing Ren, Lewis Hammond, Jesse Wright, Gurjyot Wanga, Tiziano Piccardi, Nuno Campos, Tobin South, Jialin Yu, Sunando Sengupta, Eric Sommerlade, Alex Pentland, Philip Torr, Jiaxin Pei

**Published:** 2025-12-07T17:45:01Z

**Categories:** cs.CY, cs.AI, cs.MA, cs.NI

**Links:** [Abstract](https://arxiv.org/abs/2601.02371v2) | [PDF](https://arxiv.org/pdf/2601.02371v2)

**Abstract:**
The rise of Large Language Model (LLM)-based web agents represents a significant shift in automated interactions with the web. Unlike traditional crawlers that follow simple conventions, such as robots$.$txt, modern agents engage with websites in sophisticated ways: navigating complex interfaces, extracting structured information, and completing end-to-end tasks. Existing governance mechanisms were not designed for these capabilities. Without a way to specify what interactions are and are not allowed, website owners increasingly rely on blanket blocking and CAPTCHAs, which undermine beneficial applications such as efficient automation, convenient use of e-commerce services, and accessibility tools. We introduce agent-permissions$.$json, a robots$.$txt-style lightweight manifest where websites specify allowed interactions, complemented by API references where available. This framework provides a low-friction coordination mechanism: website owners only need to write a simple JSON file, while agents can easily parse and automatically implement the manifest's provisions. Website owners can then focus on blocking non-compliant agents, rather than agents as a whole. By extending the spirit of robots$.$txt to the era of LLM-mediated interaction, and complementing data use initiatives such as AIPref, the manifest establishes a compliance framework that enables beneficial agent interactions while respecting site owners' preferences.

---

## LLM-Coordination: Evaluating and Analyzing Multi-agent Coordination Abilities in Large Language Models

**Authors:** Saaket Agashe, Yue Fan, Anthony Reyna, Xin Eric Wang

**Published:** 2023-10-05T21:18:15Z

**Categories:** cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2310.03903v3) | [PDF](https://arxiv.org/pdf/2310.03903v3)

**Abstract:**
Large Language Models (LLMs) have demonstrated emergent common-sense reasoning and Theory of Mind (ToM) capabilities, making them promising candidates for developing coordination agents. This study introduces the LLM-Coordination Benchmark, a novel benchmark for analyzing LLMs in the context of Pure Coordination Settings, where agents must cooperate to maximize gains. Our benchmark evaluates LLMs through two distinct tasks. The first is Agentic Coordination, where LLMs act as proactive participants in four pure coordination games. The second is Coordination Question Answering (CoordQA), which tests LLMs on 198 multiple-choice questions across these games to evaluate three key abilities: Environment Comprehension, ToM Reasoning, and Joint Planning. Results from Agentic Coordination experiments reveal that LLM-Agents excel in multi-agent coordination settings where decision-making primarily relies on environmental variables but face challenges in scenarios requiring active consideration of partners' beliefs and intentions. The CoordQA experiments further highlight significant room for improvement in LLMs' Theory of Mind reasoning and joint planning capabilities. Zero-Shot Coordination (ZSC) experiments in the Agentic Coordination setting demonstrate that LLM agents, unlike RL methods, exhibit robustness to unseen partners. These findings indicate the potential of LLMs as Agents in pure coordination setups and underscore areas for improvement. Code Available at https://github.com/eric-ai-lab/llm_coordination.

---

## An Implementation of Werewolf Agent That does not Truly Trust LLMs

**Authors:** Takehiro Sato, Shintaro Ozaki, Daisaku Yokoyama

**Published:** 2024-09-03T03:16:03Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2409.01575v1) | [PDF](https://arxiv.org/pdf/2409.01575v1)

**Abstract:**
Werewolf is an incomplete information game, which has several challenges when creating a computer agent as a player given the lack of understanding of the situation and individuality of utterance (e.g., computer agents are not capable of characterful utterance or situational lying). We propose a werewolf agent that solves some of those difficulties by combining a Large Language Model (LLM) and a rule-based algorithm. In particular, our agent uses a rule-based algorithm to select an output either from an LLM or a template prepared beforehand based on the results of analyzing conversation history using an LLM. It allows the agent to refute in specific situations, identify when to end the conversation, and behave with persona. This approach mitigated conversational inconsistencies and facilitated logical utterance as a result. We also conducted a qualitative evaluation, which resulted in our agent being perceived as more human-like compared to an unmodified LLM. The agent is freely available for contributing to advance the research in the field of Werewolf game.

---

## Story3D-Agent: Exploring 3D Storytelling Visualization with Large Language Models

**Authors:** Yuzhou Huang, Yiran Qin, Shunlin Lu, Xintao Wang, Rui Huang, Ying Shan, Ruimao Zhang

**Published:** 2024-08-21T17:43:15Z

**Categories:** cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2408.11801v1) | [PDF](https://arxiv.org/pdf/2408.11801v1)

**Abstract:**
Traditional visual storytelling is complex, requiring specialized knowledge and substantial resources, yet often constrained by human creativity and creation precision. While Large Language Models (LLMs) enhance visual storytelling, current approaches often limit themselves to 2D visuals or oversimplify stories through motion synthesis and behavioral simulation, failing to create comprehensive, multi-dimensional narratives. To this end, we present Story3D-Agent, a pioneering approach that leverages the capabilities of LLMs to transform provided narratives into 3D-rendered visualizations. By integrating procedural modeling, our approach enables precise control over multi-character actions and motions, as well as diverse decorative elements, ensuring the long-range and dynamic 3D representation. Furthermore, our method supports narrative extension through logical reasoning, ensuring that generated content remains consistent with existing conditions. We have thoroughly evaluated our Story3D-Agent to validate its effectiveness, offering a basic framework to advance 3D story representation.

---

## Large Language Model Agent in Financial Trading: A Survey

**Authors:** Han Ding, Yinheng Li, Junhao Wang, Hang Chen, Doudou Guo, Yunbai Zhang

**Published:** 2024-07-26T08:53:05Z

**Categories:** q-fin.TR, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2408.06361v2) | [PDF](https://arxiv.org/pdf/2408.06361v2)

**Abstract:**
Trading is a highly competitive task that requires a combination of strategy, knowledge, and psychological fortitude. With the recent success of large language models(LLMs), it is appealing to apply the emerging intelligence of LLM agents in this competitive arena and understanding if they can outperform professional traders. In this survey, we provide a comprehensive review of the current research on using LLMs as agents in financial trading. We summarize the common architecture used in the agent, the data inputs, and the performance of LLM trading agents in backtesting as well as the challenges presented in these research. This survey aims to provide insights into the current state of LLM-based financial trading agents and outline future research directions in this field.

---

## A Survey of Large Language Model Agents for Question Answering

**Authors:** Murong Yue

**Published:** 2025-03-24T23:39:44Z

**Categories:** cs.CL, cs.AI, cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2503.19213v1) | [PDF](https://arxiv.org/pdf/2503.19213v1)

**Abstract:**
This paper surveys the development of large language model (LLM)-based agents for question answering (QA). Traditional agents face significant limitations, including substantial data requirements and difficulty in generalizing to new environments. LLM-based agents address these challenges by leveraging LLMs as their core reasoning engine. These agents achieve superior QA results compared to traditional QA pipelines and naive LLM QA systems by enabling interaction with external environments. We systematically review the design of LLM agents in the context of QA tasks, organizing our discussion across key stages: planning, question understanding, information retrieval, and answer generation. Additionally, this paper identifies ongoing challenges and explores future research directions to enhance the performance of LLM agent QA systems.

---

## MobileUse: A GUI Agent with Hierarchical Reflection for Autonomous Mobile Operation

**Authors:** Ning Li, Xiangmou Qu, Jiamu Zhou, Jun Wang, Muning Wen, Kounianhua Du, Xingyu Lou, Qiuying Peng, Jun Wang, Weinan Zhang

**Published:** 2025-07-21T09:37:05Z

**Categories:** cs.RO, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2507.16853v1) | [PDF](https://arxiv.org/pdf/2507.16853v1)

**Abstract:**
Recent advances in Multimodal Large Language Models (MLLMs) have enabled the development of mobile agents that can understand visual inputs and follow user instructions, unlocking new possibilities for automating complex tasks on mobile devices. However, applying these models to real-world mobile scenarios remains a significant challenge due to the long-horizon task execution, difficulty in error recovery, and the cold-start problem in unfamiliar environments. To address these challenges, we propose MobileUse, a GUI agent designed for robust and adaptive mobile task execution. To improve resilience in long-horizon tasks and dynamic environments, we introduce a hierarchical reflection architecture that enables the agent to self-monitor, detect, and recover from errors across multiple temporal scales-ranging from individual actions to overall task completion-while maintaining efficiency through a reflection-on-demand strategy. To tackle cold-start issues, we further introduce a proactive exploration module, which enriches the agent's understanding of the environment through self-planned exploration. Evaluations on AndroidWorld and AndroidLab benchmarks demonstrate that MobileUse establishes new state-of-the-art performance, achieving success rates of 62.9% and 44.2%, respectively. To facilitate real-world applications, we release an out-of-the-box toolkit for automated task execution on physical mobile devices, which is available at https://github.com/MadeAgents/mobile-use.

---

## LLM Agent Honeypot: Monitoring AI Hacking Agents in the Wild

**Authors:** Reworr, Dmitrii Volkov

**Published:** 2024-10-17T09:25:28Z

**Categories:** cs.CR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2410.13919v2) | [PDF](https://arxiv.org/pdf/2410.13919v2)

**Abstract:**
Attacks powered by Large Language Model (LLM) agents represent a growing threat to modern cybersecurity. To address this concern, we present LLM Honeypot, a system designed to monitor autonomous AI hacking agents. By augmenting a standard SSH honeypot with prompt injection and time-based analysis techniques, our framework aims to distinguish LLM agents among all attackers. Over a trial deployment of about three months in a public environment, we collected 8,130,731 hacking attempts and 8 potential AI agents. Our work demonstrates the emergence of AI-driven threats and their current level of usage, serving as an early warning of malicious LLM agents in the wild.

---

## Interactive Learning for LLM Reasoning

**Authors:** Hehai Lin, Shilei Cao, Sudong Wang, Haotian Wu, Minzhi Li, Linyi Yang, Juepeng Zheng, Chengwei Qin

**Published:** 2025-09-30T14:21:31Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2509.26306v3) | [PDF](https://arxiv.org/pdf/2509.26306v3)

**Abstract:**
Existing multi-agent learning approaches have developed interactive training environments to explicitly promote collaboration among multiple Large Language Models (LLMs), thereby constructing stronger multi-agent systems (MAS). However, during inference, they require re-executing the MAS to obtain final solutions, which diverges from human cognition that individuals can enhance their reasoning capabilities through interactions with others and resolve questions independently in the future. To investigate whether multi-agent interaction can enhance LLMs' independent problem-solving ability, we introduce ILR, a novel co-learning framework for MAS that integrates two key components: Dynamic Interaction and Perception Calibration. Specifically, Dynamic Interaction first adaptively selects either cooperative or competitive strategies depending on question difficulty and model ability. LLMs then exchange information through Idea3 (Idea Sharing, Idea Analysis, and Idea Fusion), an innovative interaction paradigm designed to mimic human discussion, before deriving their respective final answers. In Perception Calibration, ILR employs Group Relative Policy Optimization (GRPO) to train LLMs while integrating one LLM's reward distribution characteristics into another's reward function, thereby enhancing the cohesion of multi-agent interactions. We validate ILR on three LLMs across two model families of varying scales, evaluating performance on five mathematical benchmarks and one coding benchmark. Experimental results show that ILR consistently outperforms single-agent learning, yielding an improvement of up to 5% over the strongest baseline. We further discover that Idea3 can enhance the robustness of stronger LLMs during multi-agent inference, and dynamic interaction types can boost multi-agent learning compared to pure cooperative or competitive strategies.

---

## Enhancing Jailbreak Attacks on LLMs via Persona Prompts

**Authors:** Zheng Zhang, Peilin Zhao, Deheng Ye, Hao Wang

**Published:** 2025-07-28T12:03:22Z

**Categories:** cs.CR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2507.22171v3) | [PDF](https://arxiv.org/pdf/2507.22171v3)

**Abstract:**
Jailbreak attacks aim to exploit large language models (LLMs) by inducing them to generate harmful content, thereby revealing their vulnerabilities. Understanding and addressing these attacks is crucial for advancing the field of LLM safety. Previous jailbreak approaches have mainly focused on direct manipulations of harmful intent, with limited attention to the impact of persona prompts. In this study, we systematically explore the efficacy of persona prompts in compromising LLM defenses. We propose a genetic algorithm-based method that automatically crafts persona prompts to bypass LLM's safety mechanisms. Our experiments reveal that: (1) our evolved persona prompts reduce refusal rates by 50-70% across multiple LLMs, and (2) these prompts demonstrate synergistic effects when combined with existing attack methods, increasing success rates by 10-20%. Our code and data are available at https://github.com/CjangCjengh/Generic_Persona.

---

## WizardCoder: Empowering Code Large Language Models with Evol-Instruct

**Authors:** Ziyang Luo, Can Xu, Pu Zhao, Qingfeng Sun, Xiubo Geng, Wenxiang Hu, Chongyang Tao, Jing Ma, Qingwei Lin, Daxin Jiang

**Published:** 2023-06-14T15:18:48Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2306.08568v2) | [PDF](https://arxiv.org/pdf/2306.08568v2)

**Abstract:**
Code Large Language Models (Code LLMs), such as StarCoder, have demonstrated exceptional performance in code-related tasks. However, most existing models are solely pre-trained on extensive raw code data without instruction fine-tuning. In this paper, we introduce WizardCoder, which empowers Code LLMs with complex instruction fine-tuning, by adapting the Evol-Instruct method to the domain of code. Through comprehensive experiments on four prominent code generation benchmarks, namely HumanEval, HumanEval+, MBPP, and DS-1000, we unveil the exceptional capabilities of our model. It surpasses all other open-source Code LLMs by a substantial margin. Moreover, our model even outperforms the largest closed LLMs, Anthropic's Claude and Google's Bard, on HumanEval and HumanEval+. Our code, model weights, and data are public at https://github.com/nlpxucan/WizardLM

---

## Open-LLM-Leaderboard: From Multi-choice to Open-style Questions for LLMs Evaluation, Benchmark, and Arena

**Authors:** Aidar Myrzakhan, Sondos Mahmoud Bsharat, Zhiqiang Shen

**Published:** 2024-06-11T17:59:47Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2406.07545v1) | [PDF](https://arxiv.org/pdf/2406.07545v1)

**Abstract:**
Multiple-choice questions (MCQ) are frequently used to assess large language models (LLMs). Typically, an LLM is given a question and selects the answer deemed most probable after adjustments for factors like length. Unfortunately, LLMs may inherently favor certain answer choice IDs, such as A/B/C/D, due to inherent biases of priori unbalanced probabilities, influencing the prediction of answers based on these IDs. Previous research has introduced methods to reduce this ''selection bias'' by simply permutating options on a few test samples and applying to new ones. Another problem of MCQ is the lottery ticket choice by ''random guessing''. The LLM does not learn particular knowledge, but the option is guessed correctly. This situation is especially serious for those small-scale LLMs. To address them, a more thorough approach involves shifting from MCQ to open-style questions, which can fundamentally eliminate selection bias and random guessing issues. However, transitioning causes its own set of challenges in (1) identifying suitable open-style questions and (2) validating the correctness of LLM open-style responses against human-annotated ground-truths. This work aims to tackle these significant difficulties, and establish a new LLM evaluation benchmark through entirely open-style questions. Consequently, we introduce the Open-LLM-Leaderboard to track various LLMs' performance and reflect true capability of them, such as GPT-4o/4/3.5, Claude 3, Gemini, etc. Our code and dataset are available at https://github.com/VILA-Lab/Open-LLM-Leaderboard.

---

## FIPA-based Interoperable Agent Mobility Proposal

**Authors:** Jordi Cucurull, Ramon Marti, Sergi Robles, Joan Borrell, Guillermo Navarro

**Published:** 2007-06-13T14:37:58Z

**Categories:** cs.MA, cs.NI

**Links:** [Abstract](https://arxiv.org/abs/0706.1860v2) | [PDF](https://arxiv.org/pdf/0706.1860v2)

**Abstract:**
This paper presents a proposal for a flexible agent mobility architecture based on IEEE-FIPA standards and intended to be one of them. This proposal is a first step towards interoperable mobility mechanisms, which are needed for future agent migration between different kinds of platforms. Our proposal is presented as a flexible and robust architecture that has been successfully implemented in the JADE and AgentScape platforms. It is based on an open set of protocols, allowing new protocols and future improvements to be accommodated in the architecture. With this proposal we demonstrate that a standard architecture for agent mobility capable of supporting several agent platforms can be defined and implemented.

---

## LLM-FS-Agent: A Deliberative Role-based Large Language Model Architecture for Transparent Feature Selection

**Authors:** Mohamed Bal-Ghaoui, Fayssal Sabri

**Published:** 2025-10-07T13:46:06Z

**Categories:** cs.LG, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2510.05935v1) | [PDF](https://arxiv.org/pdf/2510.05935v1)

**Abstract:**
High-dimensional data remains a pervasive challenge in machine learning, often undermining model interpretability and computational efficiency. While Large Language Models (LLMs) have shown promise for dimensionality reduction through feature selection, existing LLM-based approaches frequently lack structured reasoning and transparent justification for their decisions. This paper introduces LLM-FS-Agent, a novel multi-agent architecture designed for interpretable and robust feature selection. The system orchestrates a deliberative "debate" among multiple LLM agents, each assigned a specific role, enabling collective evaluation of feature relevance and generation of detailed justifications. We evaluate LLM-FS-Agent in the cybersecurity domain using the CIC-DIAD 2024 IoT intrusion detection dataset and compare its performance against strong baselines, including LLM-Select and traditional methods such as PCA. Experimental results demonstrate that LLM-FS-Agent consistently achieves superior or comparable classification performance while reducing downstream training time by an average of 46% (statistically significant improvement, p = 0.028 for XGBoost). These findings highlight that the proposed deliberative architecture enhances both decision transparency and computational efficiency, establishing LLM-FS-Agent as a practical and reliable solution for real-world applications.

---

## LLM as OS, Agents as Apps: Envisioning AIOS, Agents and the AIOS-Agent Ecosystem

**Authors:** Yingqiang Ge, Yujie Ren, Wenyue Hua, Shuyuan Xu, Juntao Tan, Yongfeng Zhang

**Published:** 2023-12-06T18:50:26Z

**Categories:** cs.OS, cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2312.03815v2) | [PDF](https://arxiv.org/pdf/2312.03815v2)

**Abstract:**
This paper envisions a revolutionary AIOS-Agent ecosystem, where Large Language Model (LLM) serves as the (Artificial) Intelligent Operating System (IOS, or AIOS)--an operating system "with soul". Upon this foundation, a diverse range of LLM-based AI Agent Applications (Agents, or AAPs) are developed, enriching the AIOS-Agent ecosystem and signaling a paradigm shift from the traditional OS-APP ecosystem. We envision that LLM's impact will not be limited to the AI application level, instead, it will in turn revolutionize the design and implementation of computer system, architecture, software, and programming language, featured by several main concepts: LLM as OS (system-level), Agents as Applications (application-level), Natural Language as Programming Interface (user-level), and Tools as Devices/Libraries (hardware/middleware-level). We begin by introducing the architecture of traditional OS. Then we formalize a conceptual framework for AIOS through "LLM as OS (LLMOS)", drawing analogies between AIOS and traditional OS: LLM is likened to OS kernel, context window to memory, external storage to file system, hardware tools to peripheral devices, software tools to programming libraries, and user prompts to user commands. Subsequently, we introduce the new AIOS-Agent Ecosystem, where users can easily program Agent Applications (AAPs) using natural language, democratizing the development of software, which is different from the traditional OS-APP ecosystem. Following this, we explore the diverse scope of Agent Applications. We delve into both single-agent and multi-agent systems, as well as human-agent interaction. Lastly, drawing on the insights from traditional OS-APP ecosystem, we propose a roadmap for the evolution of the AIOS-Agent ecosystem. This roadmap is designed to guide the future research and development, suggesting systematic progresses of AIOS and its Agent applications.

---

## Adaptive In-conversation Team Building for Language Model Agents

**Authors:** Linxin Song, Jiale Liu, Jieyu Zhang, Shaokun Zhang, Ao Luo, Shijian Wang, Qingyun Wu, Chi Wang

**Published:** 2024-05-29T18:08:37Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2405.19425v3) | [PDF](https://arxiv.org/pdf/2405.19425v3)

**Abstract:**
Leveraging multiple large language model (LLM) agents has shown to be a promising approach for tackling complex tasks, while the effective design of multiple agents for a particular application remains an art. It is thus intriguing to answer a critical question: Given a task, how can we build a team of LLM agents to solve it effectively? Our new adaptive team-building paradigm offers a flexible solution, realized through a novel agent design named Captain Agent. It dynamically forms and manages teams for each step of a task-solving process, utilizing nested group conversations and reflection to ensure diverse expertise and prevent stereotypical outputs, allowing for a flexible yet structured approach to problem-solving. A comprehensive evaluation across six real-world scenarios demonstrates that Captain Agent significantly outperforms existing multi-agent methods with 21.94% improvement in average accuracy, providing outstanding performance without requiring task-specific prompt engineering. Our exploration of different backbone LLM and cost analysis further shows that Captain Agent can improve the conversation quality of weak LLM and achieve competitive performance with extremely low cost, which illuminates the application of multi-agent systems.

---

## Learning Reward Machines in Cooperative Multi-Agent Tasks

**Authors:** Leo Ardon, Daniel Furelos-Blanco, Alessandra Russo

**Published:** 2023-03-24T15:12:28Z

**Categories:** cs.AI, cs.MA, cs.SC

**Links:** [Abstract](https://arxiv.org/abs/2303.14061v4) | [PDF](https://arxiv.org/pdf/2303.14061v4)

**Abstract:**
This paper presents a novel approach to Multi-Agent Reinforcement Learning (MARL) that combines cooperative task decomposition with the learning of reward machines (RMs) encoding the structure of the sub-tasks. The proposed method helps deal with the non-Markovian nature of the rewards in partially observable environments and improves the interpretability of the learnt policies required to complete the cooperative task. The RMs associated with each sub-task are learnt in a decentralised manner and then used to guide the behaviour of each agent. By doing so, the complexity of a cooperative multi-agent problem is reduced, allowing for more effective learning. The results suggest that our approach is a promising direction for future research in MARL, especially in complex environments with large state spaces and multiple agents.

---

## Can LLMs Lie? Investigation beyond Hallucination

**Authors:** Haoran Huan, Mihir Prabhudesai, Mengning Wu, Shantanu Jaiswal, Deepak Pathak

**Published:** 2025-09-03T17:59:45Z

**Categories:** cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2509.03518v1) | [PDF](https://arxiv.org/pdf/2509.03518v1)

**Abstract:**
Large language models (LLMs) have demonstrated impressive capabilities across a variety of tasks, but their increasing autonomy in real-world applications raises concerns about their trustworthiness. While hallucinations-unintentional falsehoods-have been widely studied, the phenomenon of lying, where an LLM knowingly generates falsehoods to achieve an ulterior objective, remains underexplored. In this work, we systematically investigate the lying behavior of LLMs, differentiating it from hallucinations and testing it in practical scenarios. Through mechanistic interpretability techniques, we uncover the neural mechanisms underlying deception, employing logit lens analysis, causal interventions, and contrastive activation steering to identify and control deceptive behavior. We study real-world lying scenarios and introduce behavioral steering vectors that enable fine-grained manipulation of lying tendencies. Further, we explore the trade-offs between lying and end-task performance, establishing a Pareto frontier where dishonesty can enhance goal optimization. Our findings contribute to the broader discourse on AI ethics, shedding light on the risks and potential safeguards for deploying LLMs in high-stakes environments. Code and more illustrations are available at https://llm-liar.github.io/

---

## Agent-UniRAG: A Trainable Open-Source LLM Agent Framework for Unified Retrieval-Augmented Generation Systems

**Authors:** Hoang Pham, Thuy-Duong Nguyen, Khac-Hoai Nam Bui

**Published:** 2025-05-28T16:46:31Z

**Categories:** cs.CL, cs.AI, cs.DB, cs.IR

**Links:** [Abstract](https://arxiv.org/abs/2505.22571v3) | [PDF](https://arxiv.org/pdf/2505.22571v3)

**Abstract:**
This paper presents a novel approach for unified retrieval-augmented generation (RAG) systems using the recent emerging large language model (LLM) agent concept. Specifically, Agent LLM, which utilizes LLM as fundamental controllers, has become a promising approach to enable the interpretability of RAG tasks, especially for complex reasoning question-answering systems (e.g., multi-hop queries). Nonetheless, previous works mainly focus on solving RAG systems with either single-hop or multi-hop approaches separately, which limits the application of those approaches to real-world applications. In this study, we propose a trainable agent framework called Agent-UniRAG for unified retrieval-augmented LLM systems, which enhances the effectiveness and interpretability of RAG systems. The main idea is to design an LLM agent framework to solve RAG tasks step-by-step based on the complexity of the inputs, simultaneously including single-hop and multi-hop queries in an end-to-end manner. Furthermore, we introduce SynAgent-RAG, a synthetic dataset to enable the proposed agent framework for small open-source LLMs (e.g., Llama-3-8B). The results show comparable performances with closed-source and larger open-source LLMs across various RAG benchmarks. Our source code and dataset are publicly available for further exploitation.

---

## Token Coherence: Adapting MESI Cache Protocols to Minimize Synchronization Overhead in Multi-Agent LLM Systems

**Authors:** Vladyslav Parakhin

**Published:** 2026-03-16T12:20:06Z

**Categories:** cs.DC, cs.AI, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2603.15183v1) | [PDF](https://arxiv.org/pdf/2603.15183v1)

**Abstract:**
Multi-agent LLM orchestration incurs synchronization costs scaling as O(n x S x |D|) in agents, steps, and artifact size under naive broadcast -- a regime I term broadcast-induced triply-multiplicative overhead. I argue this pathology is a structural residue of full-state rebroadcast, not an inherent property of multi-agent coordination.
  The central claim: synchronization cost explosion in LLM multi-agent systems maps with formal precision onto the cache coherence problem in shared-memory multiprocessors, and MESI-protocol invalidation transfers to artifact synchronization under minimal structural modification.
  I construct the Artifact Coherence System (ACS) and prove the Token Coherence Theorem: lazy invalidation attenuates cost by at least S/(n + W(d_i)) when S > n + W(d_i), converting O(n x S x |D|) to O((n + W) x |D|). A TLA+-verified protocol enforces single-writer safety, monotonic versioning, and bounded staleness across ~2,400 explored states.
  Simulation across four workload configurations yields token savings of 95.0% +/- 1.3% at V=0.05, 92.3% +/- 1.4% at V=0.10, 88.3% +/- 1.5% at V=0.25, and 84.2% +/- 1.3% at V=0.50 -- each exceeding the theorem's conservative lower bounds. Savings of ~81% persist at V=0.9, contrary to the predicted collapse threshold.
  Contributions: (1) formal MESI-to-artifact state mapping; (2) Token Coherence Theorem as savings lower bound; (3) TLA+-verified protocol with three proven invariants; (4) characterization of conditional artifact access semantics resolving the always-read objection; (5) reference Python implementation integrating with LangGraph, CrewAI, and AutoGen via thin adapter layers.

---

## A New Query Expansion Approach via Agent-Mediated Dialogic Inquiry

**Authors:** Wonduk Seo, Hyunjin An, Seunghyun Lee

**Published:** 2025-02-12T16:39:06Z

**Categories:** cs.IR, cs.CL, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2502.08557v3) | [PDF](https://arxiv.org/pdf/2502.08557v3)

**Abstract:**
Query expansion is widely used in Information Retrieval (IR) to improve search outcomes by supplementing initial queries with richer information. While recent Large Language Model (LLM) based methods generate pseudo-relevant content and expanded terms via multiple prompts, they often yield homogeneous, narrow expansions that lack the diverse context needed to retrieve relevant information. In this paper, we propose AMD: a new Agent-Mediated Dialogic Framework that engages in a dialogic inquiry involving three specialized roles: (1) a Socratic Questioning Agent reformulates the initial query into three sub-questions, with each question inspired by a specific Socratic questioning dimension, including clarification, assumption probing, and implication probing, (2) a Dialogic Answering Agent generates pseudo-answers, enriching the query representation with multiple perspectives aligned to the user's intent, and (3) a Reflective Feedback Agent evaluates and refines these pseudo-answers, ensuring that only the most relevant and informative content is retained. By leveraging a multi-agent process, AMD effectively crafts richer query representations through inquiry and feedback refinement. Extensive experiments on benchmarks including BEIR and TREC demonstrate that our framework outperforms previous methods, offering a robust solution for retrieval tasks.

---

## From LLM to Conversational Agent: A Memory Enhanced Architecture with Fine-Tuning of Large Language Models

**Authors:** Na Liu, Liangyu Chen, Xiaoyu Tian, Wei Zou, Kaijiang Chen, Ming Cui

**Published:** 2024-01-05T12:26:46Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2401.02777v2) | [PDF](https://arxiv.org/pdf/2401.02777v2)

**Abstract:**
This paper introduces RAISE (Reasoning and Acting through Scratchpad and Examples), an advanced architecture enhancing the integration of Large Language Models (LLMs) like GPT-4 into conversational agents. RAISE, an enhancement of the ReAct framework, incorporates a dual-component memory system, mirroring human short-term and long-term memory, to maintain context and continuity in conversations. It entails a comprehensive agent construction scenario, including phases like Conversation Selection, Scene Extraction, CoT Completion, and Scene Augmentation, leading to the LLMs Training phase. This approach appears to enhance agent controllability and adaptability in complex, multi-turn dialogues. Our preliminary evaluations in a real estate sales context suggest that RAISE has some advantages over traditional agents, indicating its potential for broader applications. This work contributes to the AI field by providing a robust framework for developing more context-aware and versatile conversational agents.

---

## ECG-LLM -- training and evaluation of domain-specific large language models for electrocardiography

**Authors:** Lara Ahrens, Wilhelm Haverkamp, Nils Strodthoff

**Published:** 2025-10-21T06:45:38Z

**Categories:** cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2510.18339v1) | [PDF](https://arxiv.org/pdf/2510.18339v1)

**Abstract:**
Domain-adapted open-weight large language models (LLMs) offer promising healthcare applications, from queryable knowledge bases to multimodal assistants, with the crucial advantage of local deployment for privacy preservation. However, optimal adaptation strategies, evaluation methodologies, and performance relative to general-purpose LLMs remain poorly characterized. We investigated these questions in electrocardiography, an important area of cardiovascular medicine, by finetuning open-weight models on domain-specific literature and implementing a multi-layered evaluation framework comparing finetuned models, retrieval-augmented generation (RAG), and Claude Sonnet 3.7 as a representative general-purpose model. Finetuned Llama 3.1 70B achieved superior performance on multiple-choice evaluations and automatic text metrics, ranking second to Claude 3.7 in LLM-as-a-judge assessments. Human expert evaluation favored Claude 3.7 and RAG approaches for complex queries. Finetuned models significantly outperformed their base counterparts across nearly all evaluation modes. Our findings reveal substantial performance heterogeneity across evaluation methodologies, underscoring assessment complexity. Nevertheless, domain-specific adaptation through finetuning and RAG achieves competitive performance with proprietary models, supporting the viability of privacy-preserving, locally deployable clinical solutions.

---

## Representing Prompting Patterns with PDL: Compliance Agent Case Study

**Authors:** Mandana Vaziri, Louis Mandel, Yuji Watanabe, Hirokuni Kitahara, Martin Hirzel, Anca Sailer

**Published:** 2025-07-08T21:03:22Z

**Categories:** cs.AI, cs.LG, cs.PL, cs.SE

**Links:** [Abstract](https://arxiv.org/abs/2507.06396v1) | [PDF](https://arxiv.org/pdf/2507.06396v1)

**Abstract:**
Prompt engineering for LLMs remains complex, with existing frameworks either hiding complexity behind restrictive APIs or providing inflexible canned patterns that resist customization -- making sophisticated agentic programming challenging. We present the Prompt Declaration Language (PDL), a novel approach to prompt representation that tackles this fundamental complexity by bringing prompts to the forefront, enabling manual and automatic prompt tuning while capturing the composition of LLM calls together with rule-based code and external tools. By abstracting away the plumbing for such compositions, PDL aims at improving programmer productivity while providing a declarative representation that is amenable to optimization. This paper demonstrates PDL's utility through a real-world case study of a compliance agent. Tuning the prompting pattern of this agent yielded up to 4x performance improvement compared to using a canned agent and prompt pattern.

---

## Unify-Agent: A Unified Multimodal Agent for World-Grounded Image Synthesis

**Authors:** Shuang Chen, Quanxin Shou, Hangting Chen, Yucheng Zhou, Kaituo Feng, Wenbo Hu, Yi-Fan Zhang, Yunlong Lin, Wenxuan Huang, Mingyang Song, Dasen Dai, Bolin Jiang, Manyuan Zhang, Shi-Xue Zhang, Zhengkai Jiang, Lucas Wang, Zhao Zhong, Yu Cheng, Nanyun Peng

**Published:** 2026-03-31T11:41:13Z

**Categories:** cs.CV, cs.MM

**Links:** [Abstract](https://arxiv.org/abs/2603.29620v2) | [PDF](https://arxiv.org/pdf/2603.29620v2)

**Abstract:**
Unified multimodal models provide a natural and promising architecture for understanding diverse and complex real-world knowledge while generating high-quality images. However, they still rely primarily on frozen parametric knowledge, which makes them struggle with real-world image generation involving long-tail and knowledge-intensive concepts. Inspired by the broad success of agents on real-world tasks, we explore agentic modeling to address this limitation. Specifically, we present Unify-Agent, a unified multimodal agent for world-grounded image synthesis, which reframes image generation as an agentic pipeline consisting of prompt understanding, multimodal evidence searching, grounded recaptioning, and final synthesis. To train our model, we construct a tailored multimodal data pipeline and curate 143K high-quality agent trajectories for world-grounded image synthesis, enabling effective supervision over the full agentic generation process. We further introduce FactIP, a benchmark covering 12 categories of culturally significant and long-tail factual concepts that explicitly requires external knowledge grounding. Extensive experiments show that our proposed Unify-Agent substantially improves over its base unified model across diverse benchmarks and real world generation tasks, while approaching the world knowledge capabilities of the strongest closed-source models. As an early exploration of agent-based modeling for world-grounded image synthesis, our work highlights the value of tightly coupling reasoning, searching, and generation for reliable open-world agentic image synthesis.

---

## Position: The Real Barrier to LLM Agent Usability is Agentic ROI

**Authors:** Weiwen Liu, Jiarui Qin, Xu Huang, Xingshan Zeng, Yunjia Xi, Jianghao Lin, Chuhan Wu, Yasheng Wang, Lifeng Shang, Ruiming Tang, Defu Lian, Yong Yu, Weinan Zhang

**Published:** 2025-05-23T11:40:58Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2505.17767v2) | [PDF](https://arxiv.org/pdf/2505.17767v2)

**Abstract:**
Large Language Model (LLM) agents represent a promising shift in human-AI interaction, moving beyond passive prompt-response systems to autonomous agents capable of reasoning, planning, and goal-directed action. While LLM agents are technically capable of performing a broad range of tasks, not all of these capabilities translate into meaningful usability. This position paper argues that the central question for LLM agent usability is no longer whether a task can be automated, but whether it delivers sufficient Agentic Return on Investment (Agentic ROI). Agentic ROI reframes evaluation from raw performance to a holistic, utility-driven perspective, guiding when, where, and for whom LLM agents should be deployed. Despite widespread application in high-ROI tasks like coding and scientific research, we identify a critical usability gap in mass-market, everyday applications. To address this, we propose a zigzag developmental trajectory: first scaling up to improve information gain and time savings, then scaling down to reduce cost. We present a strategic roadmap across these phases to make LLM agents truly usable, accessible, and scalable in real-world applications.

---

## VerilogReader: LLM-Aided Hardware Test Generation

**Authors:** Ruiyang Ma, Yuxin Yang, Ziqian Liu, Jiaxi Zhang, Min Li, Junhua Huang, Guojie Luo

**Published:** 2024-06-03T07:20:51Z

**Categories:** cs.SE, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2406.04373v1) | [PDF](https://arxiv.org/pdf/2406.04373v1)

**Abstract:**
Test generation has been a critical and labor-intensive process in hardware design verification. Recently, the emergence of Large Language Model (LLM) with their advanced understanding and inference capabilities, has introduced a novel approach. In this work, we investigate the integration of LLM into the Coverage Directed Test Generation (CDG) process, where the LLM functions as a Verilog Reader. It accurately grasps the code logic, thereby generating stimuli that can reach unexplored code branches. We compare our framework with random testing, using our self-designed Verilog benchmark suite. Experiments demonstrate that our framework outperforms random testing on designs within the LLM's comprehension scope. Our work also proposes prompt engineering optimizations to augment LLM's understanding scope and accuracy.

---

## Open Models, Closed Minds? On Agents Capabilities in Mimicking Human Personalities through Open Large Language Models

**Authors:** Lucio La Cava, Andrea Tagarelli

**Published:** 2024-01-13T16:41:40Z

**Categories:** cs.AI, cs.CL, cs.CY, cs.HC, physics.soc-ph

**Links:** [Abstract](https://arxiv.org/abs/2401.07115v3) | [PDF](https://arxiv.org/pdf/2401.07115v3)

**Abstract:**
The emergence of unveiling human-like behaviors in Large Language Models (LLMs) has led to a closer connection between NLP and human psychology. Scholars have been studying the inherent personalities exhibited by LLMs and attempting to incorporate human traits and behaviors into them. However, these efforts have primarily focused on commercially-licensed LLMs, neglecting the widespread use and notable advancements seen in Open LLMs. This work aims to address this gap by employing a set of 12 LLM Agents based on the most representative Open models and subject them to a series of assessments concerning the Myers-Briggs Type Indicator (MBTI) test and the Big Five Inventory (BFI) test. Our approach involves evaluating the intrinsic personality traits of Open LLM agents and determining the extent to which these agents can mimic human personalities when conditioned by specific personalities and roles. Our findings unveil that $(i)$ each Open LLM agent showcases distinct human personalities; $(ii)$ personality-conditioned prompting produces varying effects on the agents, with only few successfully mirroring the imposed personality, while most of them being ``closed-minded'' (i.e., they retain their intrinsic traits); and $(iii)$ combining role and personality conditioning can enhance the agents' ability to mimic human personalities. Our work represents a step up in understanding the dense relationship between NLP and human psychology through the lens of Open LLMs.

---

## Human-Centric Autonomous Systems With LLMs for User Command Reasoning

**Authors:** Yi Yang, Qingwen Zhang, Ci Li, Daniel Simões Marta, Nazre Batool, John Folkesson

**Published:** 2023-11-14T14:42:28Z

**Categories:** cs.CL, cs.AI, cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2311.08206v2) | [PDF](https://arxiv.org/pdf/2311.08206v2)

**Abstract:**
The evolution of autonomous driving has made remarkable advancements in recent years, evolving into a tangible reality. However, a human-centric large-scale adoption hinges on meeting a variety of multifaceted requirements. To ensure that the autonomous system meets the user's intent, it is essential to accurately discern and interpret user commands, especially in complex or emergency situations. To this end, we propose to leverage the reasoning capabilities of Large Language Models (LLMs) to infer system requirements from in-cabin users' commands. Through a series of experiments that include different LLM models and prompt designs, we explore the few-shot multivariate binary classification accuracy of system requirements from natural language textual commands. We confirm the general ability of LLMs to understand and reason about prompts but underline that their effectiveness is conditioned on the quality of both the LLM model and the design of appropriate sequential prompts. Code and models are public with the link \url{https://github.com/KTH-RPL/DriveCmd_LLM}.

---

## Multi-Turn Human-LLM Interaction Through the Lens of a Two-Way Intelligibility Protocol

**Authors:** Harshvardhan Mestha, Karan Bania, Shreyas V Sathyanarayana, Sidong Liu, Ashwin Srinivasan

**Published:** 2024-10-27T21:20:18Z

**Categories:** cs.AI, cs.HC, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2410.20600v4) | [PDF](https://arxiv.org/pdf/2410.20600v4)

**Abstract:**
Our interest is in the design of software systems involving a human-expert interacting -- using natural language -- with a large language model (LLM) on data analysis tasks. For complex problems, it is possible that LLMs can harness human expertise and creativity to find solutions that were otherwise elusive. On one level, this interaction takes place through multiple turns of prompts from the human and responses from the LLM. Here we investigate a more structured approach based on an abstract protocol described in [3] for interaction between agents. The protocol is motivated by a notion of "two-way intelligibility" and is modelled by a pair of communicating finite-state machines. We provide an implementation of the protocol, and provide empirical evidence of using the implementation to mediate interactions between an LLM and a human-agent in two areas of scientific interest (radiology and drug design). We conduct controlled experiments with a human proxy (a database), and uncontrolled experiments with human subjects. The results provide evidence in support of the protocol's capability of capturing one- and two-way intelligibility in human-LLM interaction; and for the utility of two-way intelligibility in the design of human-machine systems. Our code is available at https://github.com/karannb/interact.

---

## RoleRAG: Enhancing LLM Role-Playing via Graph Guided Retrieval

**Authors:** Yongjie Wang, Jonathan Leung, Zhiqi Shen

**Published:** 2025-05-24T06:11:17Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2505.18541v1) | [PDF](https://arxiv.org/pdf/2505.18541v1)

**Abstract:**
Large Language Models (LLMs) have shown promise in character imitation, enabling immersive and engaging conversations. However, they often generate content that is irrelevant or inconsistent with a character's background. We attribute these failures to: (1) the inability to accurately recall character-specific knowledge due to entity ambiguity, and (2) a lack of awareness of the character's cognitive boundaries. To address these issues, we propose RoleRAG, a retrieval-based framework that integrates efficient entity disambiguation for knowledge indexing with a boundary-aware retriever for extracting contextually appropriate information from a structured knowledge graph. Experiments on role-playing benchmarks show that RoleRAG's calibrated retrieval helps both general-purpose and role-specific LLMs better align with character knowledge and reduce hallucinated responses.

---

## Unveiling Privacy Risks in LLM Agent Memory

**Authors:** Bo Wang, Weiyi He, Shenglai Zeng, Zhen Xiang, Yue Xing, Jiliang Tang, Pengfei He

**Published:** 2025-02-17T19:55:53Z

**Categories:** cs.CR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2502.13172v2) | [PDF](https://arxiv.org/pdf/2502.13172v2)

**Abstract:**
Large Language Model (LLM) agents have become increasingly prevalent across various real-world applications. They enhance decision-making by storing private user-agent interactions in the memory module for demonstrations, introducing new privacy risks for LLM agents. In this work, we systematically investigate the vulnerability of LLM agents to our proposed Memory EXTRaction Attack (MEXTRA) under a black-box setting. To extract private information from memory, we propose an effective attacking prompt design and an automated prompt generation method based on different levels of knowledge about the LLM agent. Experiments on two representative agents demonstrate the effectiveness of MEXTRA. Moreover, we explore key factors influencing memory leakage from both the agent designer's and the attacker's perspectives. Our findings highlight the urgent need for effective memory safeguards in LLM agent design and deployment.

---

## LLM Agent for Hyper-Parameter Optimization

**Authors:** Wanzhe Wang, Jianqiu Peng, Menghao Hu, Weihuang Zhong, Tong Zhang, Shuai Wang, Yixin Zhang, Mingjie Shao, Wanli Ni

**Published:** 2025-06-18T06:28:22Z

**Categories:** cs.IT, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2506.15167v2) | [PDF](https://arxiv.org/pdf/2506.15167v2)

**Abstract:**
Hyper-parameters are essential and critical for the performance of communication algorithms. However, current hyper-parameters optimization approaches for Warm-Start Particles Swarm Optimization with Crossover and Mutation (WS-PSO-CM) algorithm, designed for radio map-enabled unmanned aerial vehicle (UAV) trajectory and communication, are primarily heuristic-based, exhibiting low levels of automation and improvable performance. In this paper, we design an Large Language Model (LLM) agent for automatic hyper-parameters-tuning, where an iterative framework and Model Context Protocol (MCP) are applied. In particular, the LLM agent is first set up via a profile, which specifies the boundary of hyper-parameters, task objective, terminal condition, conservative or aggressive strategy of optimizing hyper-parameters, and LLM configurations. Then, the LLM agent iteratively invokes WS-PSO-CM algorithm for exploration. Finally, the LLM agent exits the loop based on the terminal condition and returns an optimized set of hyperparameters. Our experiment results show that the minimal sum-rate achieved by hyper-parameters generated via our LLM agent is significantly higher than those by both human heuristics and random generation methods. This indicates that an LLM agent with PSO and WS-PSO-CM algorithm knowledge is useful in seeking high-performance hyper-parameters.

---

## PROV-AGENT: Unified Provenance for Tracking AI Agent Interactions in Agentic Workflows

**Authors:** Renan Souza, Amal Gueroudji, Stephen DeWitt, Daniel Rosendo, Tirthankar Ghosal, Robert Ross, Prasanna Balaprakash, Rafael Ferreira da Silva

**Published:** 2025-08-04T19:54:40Z

**Categories:** cs.DC, cs.DB

**Links:** [Abstract](https://arxiv.org/abs/2508.02866v3) | [PDF](https://arxiv.org/pdf/2508.02866v3)

**Abstract:**
Large Language Models (LLMs) and other foundation models are increasingly used as the core of AI agents. In agentic workflows, these agents plan tasks, interact with humans and peers, and influence scientific outcomes across federated and heterogeneous environments. However, agents can hallucinate or reason incorrectly, propagating errors when one agent's output becomes another's input. Thus, assuring that agents' actions are transparent, traceable, reproducible, and reliable is critical to assess hallucination risks and mitigate their workflow impacts. While provenance techniques have long supported these principles, existing methods fail to capture and relate agent-centric metadata such as prompts, responses, and decisions with the broader workflow context and downstream outcomes. In this paper, we introduce PROV-AGENT, a provenance model that extends W3C PROV and leverages the Model Context Protocol (MCP) and data observability to integrate agent interactions into end-to-end workflow provenance. Our contributions include: (1) a provenance model tailored for agentic workflows, (2) a near real-time, open-source system for capturing agentic provenance, and (3) a cross-facility evaluation spanning edge, cloud, and HPC environments, demonstrating support for critical provenance queries and agent reliability analysis.

---

## A Survey on LLM-as-a-Judge

**Authors:** Jiawei Gu, Xuhui Jiang, Zhichao Shi, Hexiang Tan, Xuehao Zhai, Chengjin Xu, Wei Li, Yinghan Shen, Shengjie Ma, Honghao Liu, Saizhuo Wang, Kun Zhang, Yuanzhuo Wang, Wen Gao, Lionel Ni, Jian Guo

**Published:** 2024-11-23T16:03:35Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2411.15594v6) | [PDF](https://arxiv.org/pdf/2411.15594v6)

**Abstract:**
Accurate and consistent evaluation is crucial for decision-making across numerous fields, yet it remains a challenging task due to inherent subjectivity, variability, and scale. Large Language Models (LLMs) have achieved remarkable success across diverse domains, leading to the emergence of "LLM-as-a-Judge," where LLMs are employed as evaluators for complex tasks. With their ability to process diverse data types and provide scalable, cost-effective, and consistent assessments, LLMs present a compelling alternative to traditional expert-driven evaluations. However, ensuring the reliability of LLM-as-a-Judge systems remains a significant challenge that requires careful design and standardization. This paper provides a comprehensive survey of LLM-as-a-Judge, addressing the core question: How can reliable LLM-as-a-Judge systems be built? We explore strategies to enhance reliability, including improving consistency, mitigating biases, and adapting to diverse assessment scenarios. Additionally, we propose methodologies for evaluating the reliability of LLM-as-a-Judge systems, supported by a novel benchmark designed for this purpose. To advance the development and real-world deployment of LLM-as-a-Judge systems, we also discussed practical applications, challenges, and future directions. This survey serves as a foundational reference for researchers and practitioners in this rapidly evolving field.

---

## Prospect Personalized Recommendation on Large Language Model-based Agent Platform

**Authors:** Jizhi Zhang, Keqin Bao, Wenjie Wang, Yang Zhang, Wentao Shi, Wanhong Xu, Fuli Feng, Tat-Seng Chua

**Published:** 2024-02-28T11:12:17Z

**Categories:** cs.IR, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2402.18240v2) | [PDF](https://arxiv.org/pdf/2402.18240v2)

**Abstract:**
The new kind of Agent-oriented information system, exemplified by GPTs, urges us to inspect the information system infrastructure to support Agent-level information processing and to adapt to the characteristics of Large Language Model (LLM)-based Agents, such as interactivity. In this work, we envisage the prospect of the recommender system on LLM-based Agent platforms and introduce a novel recommendation paradigm called Rec4Agentverse, comprised of Agent Items and Agent Recommender. Rec4Agentverse emphasizes the collaboration between Agent Items and Agent Recommender, thereby promoting personalized information services and enhancing the exchange of information beyond the traditional user-recommender feedback loop. Additionally, we prospect the evolution of Rec4Agentverse and conceptualize it into three stages based on the enhancement of the interaction and information exchange among Agent Items, Agent Recommender, and the user. A preliminary study involving several cases of Rec4Agentverse validates its significant potential for application. Lastly, we discuss potential issues and promising directions for future research.

---

## Preventing Rogue Agents Improves Multi-Agent Collaboration

**Authors:** Ohav Barbi, Ori Yoran, Mor Geva

**Published:** 2025-02-09T18:35:08Z

**Categories:** cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2502.05986v2) | [PDF](https://arxiv.org/pdf/2502.05986v2)

**Abstract:**
Multi-agent systems, where specialized agents collaborate to solve a shared task hold great potential, from increased modularity to simulating complex environments. However, they also have a major caveat -- a single agent can cause the entire system to fail. Consider a simple game where the knowledge to solve the task is distributed between agents, which share information in a communication channel. At each round, any of the agents can terminate the game and make the final prediction, even if they are uncertain about the outcome of their action. Detection of such rogue agents before they act may prevent the system's failure. In this work, we propose to monitor agents during action prediction and intervene when a future error is likely to occur. To test our approach, we introduce WhoDunitEnv, a multi-agent collaboration environment that allows modular control over task complexity and communication structure. Experiments on WhoDunitEnv, code generation tasks and the GovSim environment for resource sustainability show that our approach leads to substantial performance gains up to 17.4%, 2.5% and 20%, respectively. Thorough analysis shows that our monitors successfully identify critical points of agent confusion and our interventions effectively stop agent errors from propagating.

---

## Training-Free Agentic AI: Probabilistic Control and Coordination in Multi-Agent LLM Systems

**Authors:** Mohammad Parsa Hosseini, Ankit Shah, Saiyra Qureshi, Alex Huang, Connie Miao, Wei Wei

**Published:** 2026-02-24T21:39:14Z

**Categories:** cs.CL, cs.AI, cs.ET, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2603.13256v1) | [PDF](https://arxiv.org/pdf/2603.13256v1)

**Abstract:**
Multi-agent large language model (LLM) systems enable complex, long-horizon reasoning by composing specialized agents, but practical deployment remains hindered by inefficient routing, noisy feedback, and high interaction cost. We introduce REDEREF, a lightweight and training-free controller for multi-agent LLM collaboration that improves routing efficiency during recursive delegation. REDEREF integrates (i) belief-guided delegation via Thompson sampling to prioritize agents with historically positive marginal contributions, (ii) reflection-driven re-routing using a calibrated LLM or programmatic judge, (iii) evidence-based selection rather than output averaging, and (iv) memory-aware priors to reduce cold-start inefficiency. Across multi-agent split-knowledge tasks, we show that while recursive retry alone saturates task success, belief-guided routing reduces token usage by 28%, agent calls by 17%, and time-to-success by 19% compared to random recursive delegation, and adapts gracefully under agent or judge degradation. These results demonstrate that simple, interpretable probabilistic control can meaningfully improve the efficiency and robustness of multi-agent LLM systems without training or fine-tuning.

---

## Les Dissonances: Cross-Tool Harvesting and Polluting in Pool-of-Tools Empowered LLM Agents

**Authors:** Zichuan Li, Jian Cui, Xiaojing Liao, Luyi Xing

**Published:** 2025-04-04T01:41:06Z

**Categories:** cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2504.03111v3) | [PDF](https://arxiv.org/pdf/2504.03111v3)

**Abstract:**
Large Language Model (LLM) agents are autonomous systems powered by LLMs, capable of reasoning and planning to solve problems by leveraging a set of tools. However, the integration of multi-tool capabilities in LLM agents introduces challenges in securely managing tools, ensuring their compatibility, handling dependency relationships, and protecting control flows within LLM agent workflows. In this paper, we present the first systematic security analysis of task control flows in multi-tool-enabled LLM agents. We identify a novel threat, Cross-Tool Harvesting and Polluting (XTHP), which includes multiple attack vectors to first hijack the normal control flows of agent tasks, and then collect and pollute confidential or private information within LLM agent systems. To understand the impact of this threat, we developed Chord, a dynamic scanning tool designed to automatically detect real-world agent tools susceptible to XTHP attacks. Our evaluation of 66 real-world tools from the repositories of two major LLM agent development frameworks, LangChain and LlamaIndex, revealed a significant security concern: 75% are vulnerable to XTHP attacks, highlighting the prevalence of this threat.

---

## Improving LLM-Powered EDA Assistants with RAFT

**Authors:** Luyao Shi, Michael Kazda, Charles Schmitter, Hemlata Gupta

**Published:** 2025-06-06T19:50:51Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2506.06500v1) | [PDF](https://arxiv.org/pdf/2506.06500v1)

**Abstract:**
Electronic design engineers often struggle to efficiently access relevant information for tasks like design verification and technology development. While large language models (LLMs) can enhance productivity as conversational agents, pre-trained open-source LLMs lack domain-specific knowledge for Electronic Design Automation (EDA). In a Retrieval-Augmented Generation (RAG) context, LLMs rely on external context but may still produce inaccurate responses. Retrieval-Augmented Fine-Tuning (RAFT) improves LLM performance, but acquiring labeled question/answer (Q/A) data in EDA is difficult. To address this, we propose using synthetic Q/A datasets to enhance LLMs with RAFT. Our results show that RAFT with synthetic data significantly boosts LLM performance for RAG-based EDA tasks. We also investigate the impact of using real user questions as Retrieval-Augmented Few-Shot (RAFS) examples for synthetic data generation. Additionally, we implement secure access control to ensure sensitive information is only accessible to authorized personnel. Finally, we assess the risk of data leakage and unintended memorization during fine-tuning with synthetic data, providing practical insights.

---

## INMS: Memory Sharing for Large Language Model based Agents

**Authors:** Hang Gao, Yongfeng Zhang

**Published:** 2024-04-15T17:57:30Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2404.09982v3) | [PDF](https://arxiv.org/pdf/2404.09982v3)

**Abstract:**
While Large Language Model (LLM) based agents excel at complex tasks, their performance in open-ended scenarios is often constrained by isolated operation and reliance on static databases, missing the dynamic knowledge exchange of human dialogue. To bridge this gap, we propose the INteractive Memory Sharing (INMS) framework, an asynchronous interaction paradigm for multi-agent systems. By integrating real-time memory filtering, storage, and retrieval, INMS establishes a shared conversational memory pool. This enables continuous, dialogue-like memory sharing among agents, promoting collective self-enhancement and dynamically refining the retrieval mediator based on interaction history. Extensive experiments across three datasets demonstrate that INMS significantly improves agent performance by effectively modeling multi-agent interaction and collective knowledge sharing.

---

## Adversarial Reinforcement Learning for Large Language Model Agent Safety

**Authors:** Zizhao Wang, Dingcheng Li, Vaishakh Keshava, Phillip Wallis, Ananth Balashankar, Peter Stone, Lukas Rutishauser

**Published:** 2025-10-06T23:09:18Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2510.05442v1) | [PDF](https://arxiv.org/pdf/2510.05442v1)

**Abstract:**
Large Language Model (LLM) agents can leverage tools such as Google Search to complete complex tasks. However, this tool usage introduces the risk of indirect prompt injections, where malicious instructions hidden in tool outputs can manipulate the agent, posing security risks like data leakage. Current defense strategies typically rely on fine-tuning LLM agents on datasets of known attacks. However, the generation of these datasets relies on manually crafted attack patterns, which limits their diversity and leaves agents vulnerable to novel prompt injections. To address this limitation, we propose Adversarial Reinforcement Learning for Agent Safety (ARLAS), a novel framework that leverages adversarial reinforcement learning (RL) by formulating the problem as a two-player zero-sum game. ARLAS co-trains two LLMs: an attacker that learns to autonomously generate diverse prompt injections and an agent that learns to defend against them while completing its assigned tasks. To ensure robustness against a wide range of attacks and to prevent cyclic learning, we employ a population-based learning framework that trains the agent to defend against all previous attacker checkpoints. Evaluated on BrowserGym and AgentDojo, agents fine-tuned with ARLAS achieve a significantly lower attack success rate than the original model while also improving their task success rate. Our analysis further confirms that the adversarial process generates a diverse and challenging set of attacks, leading to a more robust agent compared to the base model.

---

## Mixture-of-Agents Enhances Large Language Model Capabilities

**Authors:** Junlin Wang, Jue Wang, Ben Athiwaratkun, Ce Zhang, James Zou

**Published:** 2024-06-07T07:04:10Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2406.04692v1) | [PDF](https://arxiv.org/pdf/2406.04692v1)

**Abstract:**
Recent advances in large language models (LLMs) demonstrate substantial capabilities in natural language understanding and generation tasks. With the growing number of LLMs, how to harness the collective expertise of multiple LLMs is an exciting open direction. Toward this goal, we propose a new approach that leverages the collective strengths of multiple LLMs through a Mixture-of-Agents (MoA) methodology. In our approach, we construct a layered MoA architecture wherein each layer comprises multiple LLM agents. Each agent takes all the outputs from agents in the previous layer as auxiliary information in generating its response. MoA models achieves state-of-art performance on AlpacaEval 2.0, MT-Bench and FLASK, surpassing GPT-4 Omni. For example, our MoA using only open-source LLMs is the leader of AlpacaEval 2.0 by a substantial gap, achieving a score of 65.1% compared to 57.5% by GPT-4 Omni.

---

## Towards Effective GenAI Multi-Agent Collaboration: Design and Evaluation for Enterprise Applications

**Authors:** Raphael Shu, Nilaksh Das, Michelle Yuan, Monica Sunkara, Yi Zhang

**Published:** 2024-12-06T22:14:17Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2412.05449v1) | [PDF](https://arxiv.org/pdf/2412.05449v1)

**Abstract:**
AI agents powered by large language models (LLMs) have shown strong capabilities in problem solving. Through combining many intelligent agents, multi-agent collaboration has emerged as a promising approach to tackle complex, multi-faceted problems that exceed the capabilities of single AI agents. However, designing the collaboration protocols and evaluating the effectiveness of these systems remains a significant challenge, especially for enterprise applications. This report addresses these challenges by presenting a comprehensive evaluation of coordination and routing capabilities in a novel multi-agent collaboration framework. We evaluate two key operational modes: (1) a coordination mode enabling complex task completion through parallel communication and payload referencing, and (2) a routing mode for efficient message forwarding between agents. We benchmark on a set of handcrafted scenarios from three enterprise domains, which are publicly released with the report. For coordination capabilities, we demonstrate the effectiveness of inter-agent communication and payload referencing mechanisms, achieving end-to-end goal success rates of 90%. Our analysis yields several key findings: multi-agent collaboration enhances goal success rates by up to 70% compared to single-agent approaches in our benchmarks; payload referencing improves performance on code-intensive tasks by 23%; latency can be substantially reduced with a routing mechanism that selectively bypasses agent orchestration. These findings offer valuable guidance for enterprise deployments of multi-agent systems and advance the development of scalable, efficient multi-agent collaboration frameworks.

---

## AutoAgent: A Fully-Automated and Zero-Code Framework for LLM Agents

**Authors:** Jiabin Tang, Tianyu Fan, Chao Huang

**Published:** 2025-02-09T16:53:56Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2502.05957v3) | [PDF](https://arxiv.org/pdf/2502.05957v3)

**Abstract:**
Large Language Model (LLM) Agents have demonstrated remarkable capabilities in task automation and intelligent decision-making, driving the widespread adoption of agent development frameworks such as LangChain and AutoGen. However, these frameworks predominantly serve developers with extensive technical expertise - a significant limitation considering that only 0.03 % of the global population possesses the necessary programming skills. This stark accessibility gap raises a fundamental question: Can we enable everyone, regardless of technical background, to build their own LLM agents using natural language alone? To address this challenge, we introduce AutoAgent-a Fully-Automated and highly Self-Developing framework that enables users to create and deploy LLM agents through Natural Language Alone. Operating as an autonomous Agent Operating System, AutoAgent comprises four key components: i) Agentic System Utilities, ii) LLM-powered Actionable Engine, iii) Self-Managing File System, and iv) Self-Play Agent Customization module. This lightweight yet powerful system enables efficient and dynamic creation and modification of tools, agents, and workflows without coding requirements or manual intervention. Beyond its code-free agent development capabilities, AutoAgent also serves as a versatile multi-agent system for General AI Assistants. Comprehensive evaluations on the GAIA benchmark demonstrate AutoAgent's effectiveness in generalist multi-agent tasks, surpassing existing state-of-the-art methods. Furthermore, AutoAgent's Retrieval-Augmented Generation (RAG)-related capabilities have shown consistently superior performance compared to many alternative LLM-based solutions.

---

## Quantifying the effects of environment and population diversity in multi-agent reinforcement learning

**Authors:** Kevin R. McKee, Joel Z. Leibo, Charlie Beattie, Richard Everett

**Published:** 2021-02-16T18:54:39Z

**Categories:** cs.MA, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2102.08370v2) | [PDF](https://arxiv.org/pdf/2102.08370v2)

**Abstract:**
Generalization is a major challenge for multi-agent reinforcement learning. How well does an agent perform when placed in novel environments and in interactions with new co-players? In this paper, we investigate and quantify the relationship between generalization and diversity in the multi-agent domain. Across the range of multi-agent environments considered here, procedurally generating training levels significantly improves agent performance on held-out levels. However, agent performance on the specific levels used in training sometimes declines as a result. To better understand the effects of co-player variation, our experiments introduce a new environment-agnostic measure of behavioral diversity. Results demonstrate that population size and intrinsic motivation are both effective methods of generating greater population diversity. In turn, training with a diverse set of co-players strengthens agent performance in some (but not all) cases.

---

## Ask-EDA: A Design Assistant Empowered by LLM, Hybrid RAG and Abbreviation De-hallucination

**Authors:** Luyao Shi, Michael Kazda, Bradley Sears, Nick Shropshire, Ruchir Puri

**Published:** 2024-06-03T19:40:28Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2406.06575v1) | [PDF](https://arxiv.org/pdf/2406.06575v1)

**Abstract:**
Electronic design engineers are challenged to find relevant information efficiently for a myriad of tasks within design construction, verification and technology development. Large language models (LLM) have the potential to help improve productivity by serving as conversational agents that effectively function as subject-matter experts. In this paper we demonstrate Ask-EDA, a chat agent designed to serve as a 24x7 expert available to provide guidance to design engineers. Ask-EDA leverages LLM, hybrid retrieval augmented generation (RAG) and abbreviation de-hallucination (ADH) techniques to deliver more relevant and accurate responses. We curated three evaluation datasets, namely q2a-100, cmds-100 and abbr-100. Each dataset is tailored to assess a distinct aspect: general design question answering, design command handling and abbreviation resolution. We demonstrated that hybrid RAG offers over a 40% improvement in Recall on the q2a-100 dataset and over a 60% improvement on the cmds-100 dataset compared to not using RAG, while ADH yields over a 70% enhancement in Recall on the abbr-100 dataset. The evaluation results show that Ask-EDA can effectively respond to design-related inquiries.

---

## Agent-SafetyBench: Evaluating the Safety of LLM Agents

**Authors:** Zhexin Zhang, Shiyao Cui, Yida Lu, Jingzhuo Zhou, Junxiao Yang, Hongning Wang, Minlie Huang

**Published:** 2024-12-19T02:35:15Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2412.14470v2) | [PDF](https://arxiv.org/pdf/2412.14470v2)

**Abstract:**
As large language models (LLMs) are increasingly deployed as agents, their integration into interactive environments and tool use introduce new safety challenges beyond those associated with the models themselves. However, the absence of comprehensive benchmarks for evaluating agent safety presents a significant barrier to effective assessment and further improvement. In this paper, we introduce Agent-SafetyBench, a comprehensive benchmark designed to evaluate the safety of LLM agents. Agent-SafetyBench encompasses 349 interaction environments and 2,000 test cases, evaluating 8 categories of safety risks and covering 10 common failure modes frequently encountered in unsafe interactions. Our evaluation of 16 popular LLM agents reveals a concerning result: none of the agents achieves a safety score above 60%. This highlights significant safety challenges in LLM agents and underscores the considerable need for improvement. Through failure mode and helpfulness analysis, we summarize two fundamental safety defects in current LLM agents: lack of robustness and lack of risk awareness. Furthermore, our findings suggest that reliance on defense prompts alone may be insufficient to address these safety issues, emphasizing the need for more advanced and robust strategies. To drive progress in this area, Agent-SafetyBench has been released at https://github.com/thu-coai/Agent-SafetyBench/ to facilitate further research in agent safety evaluation and improvement.

---

## Knowledgeable Agents by Offline Reinforcement Learning from Large Language Model Rollouts

**Authors:** Jing-Cheng Pang, Si-Hang Yang, Kaiyuan Li, Jiaji Zhang, Xiong-Hui Chen, Nan Tang, Yang Yu

**Published:** 2024-04-14T13:19:40Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2404.09248v1) | [PDF](https://arxiv.org/pdf/2404.09248v1)

**Abstract:**
Reinforcement learning (RL) trains agents to accomplish complex tasks through environmental interaction data, but its capacity is also limited by the scope of the available data. To obtain a knowledgeable agent, a promising approach is to leverage the knowledge from large language models (LLMs). Despite previous studies combining LLMs with RL, seamless integration of the two components remains challenging due to their semantic gap. This paper introduces a novel method, Knowledgeable Agents from Language Model Rollouts (KALM), which extracts knowledge from LLMs in the form of imaginary rollouts that can be easily learned by the agent through offline reinforcement learning methods. The primary challenge of KALM lies in LLM grounding, as LLMs are inherently limited to textual data, whereas environmental data often comprise numerical vectors unseen to LLMs. To address this, KALM fine-tunes the LLM to perform various tasks based on environmental data, including bidirectional translation between natural language descriptions of skills and their corresponding rollout data. This grounding process enhances the LLM's comprehension of environmental dynamics, enabling it to generate diverse and meaningful imaginary rollouts that reflect novel skills. Initial empirical evaluations on the CLEVR-Robot environment demonstrate that KALM enables agents to complete complex rephrasings of task goals and extend their capabilities to novel tasks requiring unprecedented optimal behaviors. KALM achieves a success rate of 46% in executing tasks with unseen goals, substantially surpassing the 26% success rate achieved by baseline methods. Furthermore, KALM effectively enables the LLM to comprehend environmental dynamics, resulting in the generation of meaningful imaginary rollouts that reflect novel skills and demonstrate the seamless integration of large language models and reinforcement learning.

---

## Large Language Models as Delivery Rider: Generating Instant Food Delivery Riders' Routing Decision with LLM Agent Framework

**Authors:** Chengbo Zhang, Zuopeng Xiao

**Published:** 2026-03-13T01:41:31Z

**Categories:** physics.soc-ph

**Links:** [Abstract](https://arxiv.org/abs/2603.12559v1) | [PDF](https://arxiv.org/pdf/2603.12559v1)

**Abstract:**
The utilization of Large Language Models (LLMs) to power human-like agents has shown remarkable potential in simulating individual mobility pattern. However, a significant gap remains in modeling cohorts of agents in dynamic and interactive systems where they must take strategic routing decisions to response mobility-specific task. To bridge this gap, we introduce LLM-DR, a novel agent framework designed to simulate the heterogeneous decision-making of riders in the on-demand instant delivery task scenario. Our framework is founded on two principles: 1) Empirically-grounded personas, where we use unsupervised clustering on a large-scale, real-world trajectory dataset to identify four distinct rider work strategies; and 2) Reasoning-based routing process, where each persona is instantiated as an LLM agent that employs a structured Chain-of-Thought (CoT) process to make human-like routing choices. This framework enables the construction of high-fidelity simulations to investigate how the strategic composition of a rider workforce influences system-level outcomes regarding their mobility pattern. We validate our framework on an real-world instant deliver order datasets, demonstrating its capacity to model complex rider behavior in an interactive market scenario. This work provides pioneering findings in agentic mobility system empowered by LLM.

---

## Large Language Model Agent Personality and Response Appropriateness: Evaluation by Human Linguistic Experts, LLM-as-Judge, and Natural Language Processing Model

**Authors:** Eswari Jayakumar, Niladri Sekhar Dash, Debasmita Mukherjee

**Published:** 2025-10-27T21:30:12Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2510.23875v1) | [PDF](https://arxiv.org/pdf/2510.23875v1)

**Abstract:**
While Large Language Model (LLM)-based agents can be used to create highly engaging interactive applications through prompting personality traits and contextual data, effectively assessing their personalities has proven challenging. This novel interdisciplinary approach addresses this gap by combining agent development and linguistic analysis to assess the prompted personality of LLM-based agents in a poetry explanation task. We developed a novel, flexible question bank, informed by linguistic assessment criteria and human cognitive learning levels, offering a more comprehensive evaluation than current methods. By evaluating agent responses with natural language processing models, other LLMs, and human experts, our findings illustrate the limitations of purely deep learning solutions and emphasize the critical role of interdisciplinary design in agent development.

---

## KnowThyself: An Agentic Assistant for LLM Interpretability

**Authors:** Suraj Prasai, Mengnan Du, Ying Zhang, Fan Yang

**Published:** 2025-11-05T21:48:13Z

**Categories:** cs.AI, cs.IR, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2511.03878v1) | [PDF](https://arxiv.org/pdf/2511.03878v1)

**Abstract:**
We develop KnowThyself, an agentic assistant that advances large language model (LLM) interpretability. Existing tools provide useful insights but remain fragmented and code-intensive. KnowThyself consolidates these capabilities into a chat-based interface, where users can upload models, pose natural language questions, and obtain interactive visualizations with guided explanations. At its core, an orchestrator LLM first reformulates user queries, an agent router further directs them to specialized modules, and the outputs are finally contextualized into coherent explanations. This design lowers technical barriers and provides an extensible platform for LLM inspection. By embedding the whole process into a conversational workflow, KnowThyself offers a robust foundation for accessible LLM interpretability.

---

## Behavior Trees Enable Structured Programming of Language Model Agents

**Authors:** Richard Kelley

**Published:** 2024-04-11T02:44:13Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2404.07439v1) | [PDF](https://arxiv.org/pdf/2404.07439v1)

**Abstract:**
Language models trained on internet-scale data sets have shown an impressive ability to solve problems in Natural Language Processing and Computer Vision. However, experience is showing that these models are frequently brittle in unexpected ways, and require significant scaffolding to ensure that they operate correctly in the larger systems that comprise "language-model agents." In this paper, we argue that behavior trees provide a unifying framework for combining language models with classical AI and traditional programming. We introduce Dendron, a Python library for programming language model agents using behavior trees. We demonstrate the approach embodied by Dendron in three case studies: building a chat agent, a camera-based infrastructure inspection agent for use on a mobile robot or vehicle, and an agent that has been built to satisfy safety constraints that it did not receive through instruction tuning or RLHF.

---

## Semantic Importance-Aware Communications Using Pre-trained Language Models

**Authors:** Shuaishuai Guo, Yanhu Wang, Shujing Li, Nasir Saeed

**Published:** 2023-02-12T07:48:04Z

**Categories:** eess.SP

**Links:** [Abstract](https://arxiv.org/abs/2302.07142v2) | [PDF](https://arxiv.org/pdf/2302.07142v2)

**Abstract:**
This letter proposes a semantic importance-aware communication (SIAC) scheme using pre-trained language models (e.g., ChatGPT, BERT, etc.). Specifically, we propose a cross-layer design with a pre-trained language model embedded in/connected by the cross-layer manager. The pre-trained language model is utilized to quantify the semantic importance of data frames. Based on the quantified semantic importance, we investigate semantic importance-aware power allocation. Unlike existing deep joint source-channel coding (Deep-JSCC)-based semantic communication schemes, SIAC can be directly embedded into current communication systems by only introducing a cross-layer manager. Our experimental results show that the proposed SIAC scheme can achieve lower semantic loss than existing equal-priority communications.

---

## Rethinking Human Preference Evaluation of LLM Rationales

**Authors:** Ziang Li, Manasi Ganti, Zixian Ma, Helena Vasconcelos, Qijia He, Ranjay Krishna

**Published:** 2025-09-14T01:33:14Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2509.11026v1) | [PDF](https://arxiv.org/pdf/2509.11026v1)

**Abstract:**
Large language models (LLMs) often generate natural language rationales -- free-form explanations that help improve performance on complex reasoning tasks and enhance interpretability for human users. However, evaluating these rationales remains challenging. While recent work has relied on binary preference judgments from humans or LLM judges, such evaluations are often opaque and coarse-grained, offering limited insight into what makes one rationale better than another. In this work, we rethink preference evaluation for LLM-generated rationales by asking: (1) What attributes define good rationales? (2) Can human preferences be explained by these attributes? (3) Can attribute-based evaluation overcome the limitations of binary comparisons? We identify a set of key rationale attributes from prior literature and assess them using automatic metrics, LLM judgments, and human annotations. We then analyze two standard human preference datasets MT Bench and Chatbot Arena using SHAP to identify which attributes best explain human preference outcomes. Finally, we re-evaluate model-generated rationales using attribute-specific ELO scores, revealing more nuanced model comparisons and insights. Our findings suggest that fine-grained attribute evaluations can better characterize rationale quality and guide future research toward more interpretable and reliable evaluation practices.

---

## Analysing The Impact of Sequence Composition on Language Model Pre-Training

**Authors:** Yu Zhao, Yuanbin Qu, Konrad Staniszewski, Szymon Tworkowski, Wei Liu, Piotr Miłoś, Yuxiang Wu, Pasquale Minervini

**Published:** 2024-02-21T18:23:16Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2402.13991v1) | [PDF](https://arxiv.org/pdf/2402.13991v1)

**Abstract:**
Most language model pre-training frameworks concatenate multiple documents into fixed-length sequences and use causal masking to compute the likelihood of each token given its context; this strategy is widely adopted due to its simplicity and efficiency. However, to this day, the influence of the pre-training sequence composition strategy on the generalisation properties of the model remains under-explored. In this work, we find that applying causal masking can lead to the inclusion of distracting information from previous documents during pre-training, which negatively impacts the performance of the models on language modelling and downstream tasks. In intra-document causal masking, the likelihood of each token is only conditioned on the previous tokens in the same document, eliminating potential distracting information from previous documents and significantly improving performance. Furthermore, we find that concatenating related documents can reduce some potential distractions during pre-training, and our proposed efficient retrieval-based sequence construction method, BM25Chunk, can improve in-context learning (+11.6\%), knowledge memorisation (+9.8\%), and context utilisation (+7.2\%) abilities of language models without sacrificing efficiency.

---

## SAND: Boosting LLM Agents with Self-Taught Action Deliberation

**Authors:** Yu Xia, Yiran Shen, Junda Wu, Tong Yu, Sungchul Kim, Ryan A. Rossi, Lina Yao, Julian McAuley

**Published:** 2025-07-10T05:38:15Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2507.07441v2) | [PDF](https://arxiv.org/pdf/2507.07441v2)

**Abstract:**
Large Language Model (LLM) agents are commonly tuned with supervised finetuning on ReAct-style expert trajectories or preference optimization over pairwise rollouts. Most of these methods focus on imitating specific expert behaviors or promoting chosen reasoning thoughts and actions over rejected ones. However, without reasoning and comparing over alternatives actions, LLM agents finetuned with these methods may over-commit towards seemingly plausible but suboptimal actions due to limited action space exploration. To address this, in this paper we propose Self-taught ActioN Deliberation (SAND) framework, enabling LLM agents to explicitly deliberate over candidate actions before committing to one. To tackle the challenges of when and what to deliberate given large action space and step-level action evaluation, we incorporate self-consistency action sampling and execution-guided action critique to help synthesize step-wise action deliberation thoughts using the base model of the LLM agent. In an iterative manner, the deliberation trajectories are then used to finetune the LLM agent itself. Evaluating on two representative interactive agent tasks, SAND achieves an average 20% improvement over initial supervised finetuning and also outperforms state-of-the-art agent tuning approaches.

---

## The LLM Bottleneck: Why Open-Source Vision LLMs Struggle with Hierarchical Visual Recognition

**Authors:** Yuwen Tan, Yuan Qing, Boqing Gong

**Published:** 2025-05-30T17:40:46Z

**Categories:** cs.CV, cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2505.24840v2) | [PDF](https://arxiv.org/pdf/2505.24840v2)

**Abstract:**
This paper reveals that many open-source large language models (LLMs) lack hierarchical knowledge about our visual world, unaware of even well-established biology taxonomies. This shortcoming makes LLMs a bottleneck for vision LLMs' hierarchical visual recognition (e.g., recognizing Anemone Fish but not Vertebrate). We arrive at these findings using about one million four-choice visual question answering (VQA) tasks constructed from six taxonomies and four image datasets. Interestingly, finetuning a vision LLM using our VQA tasks reaffirms LLMs' bottleneck effect because the VQA tasks improve the LLMs' hierarchical consistency more than the vision LLMs'. We conjecture that one cannot make open-source vision LLMs understand visual concepts hierarchically until LLMs possess corresponding taxonomy knowledge.

---

## Assessing Deanonymization Risks with Stylometry-Assisted LLM Agent

**Authors:** Boyang Zhang, Yang Zhang

**Published:** 2026-02-26T15:05:13Z

**Categories:** cs.CL, cs.CR, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2602.23079v1) | [PDF](https://arxiv.org/pdf/2602.23079v1)

**Abstract:**
The rapid advancement of large language models (LLMs) has enabled powerful authorship inference capabilities, raising growing concerns about unintended deanonymization risks in textual data such as news articles. In this work, we introduce an LLM agent designed to evaluate and mitigate such risks through a structured, interpretable pipeline. Central to our framework is the proposed $\textit{SALA}$ (Stylometry-Assisted LLM Analysis) method, which integrates quantitative stylometric features with LLM reasoning for robust and transparent authorship attribution. Experiments on large-scale news datasets demonstrate that $\textit{SALA}$, particularly when augmented with a database module, achieves high inference accuracy in various scenarios. Finally, we propose a guided recomposition strategy that leverages the agent's reasoning trace to generate rewriting prompts, effectively reducing authorship identifiability while preserving textual meaning. Our findings highlight both the deanonymization potential of LLM agents and the importance of interpretable, proactive defenses for safeguarding author privacy.

---

## Your Code Agent Can Grow Alongside You with Structured Memory

**Authors:** Yi-Xuan Deng, Xiaoqin Liu, Yi Zhang, Guo-Wei Yang, Shuojin Yang

**Published:** 2026-02-25T06:39:29Z

**Categories:** cs.LG, cs.AI, cs.SE

**Links:** [Abstract](https://arxiv.org/abs/2603.13258v1) | [PDF](https://arxiv.org/pdf/2603.13258v1)

**Abstract:**
While "Intent-oriented programming" (or "Vibe Coding") redefines software engineering, existing code agents remain tethered to static code snapshots. Consequently, they struggle to model the critical information embedded in the temporal evolution of projects, failing to leverage the "reasoning trajectories" implicit in past successful practices. This limitation results in rigid behavioral logic and a lack of autonomous adaptability, ultimately hindering their ability to tackle complex, repository-level problems. To bridge this static-dynamic mismatch, we propose MemCoder, a framework designed to enable continual human-AI co-evolution. MemCoder first structures historical human experience to distill latent intent-to-code mappings from past commits. It then employs a self-refinement mechanism driven by verification feedback to correct agent behavior in real-time. Crucially, an experience self-internalization mechanism is introduced to crystallize human-validated solutions into long-term knowledge, thereby supporting sustained evolution. Experimental results on SWE-bench Verified demonstrate that MemCoder not only achieves State-of-the-Art (SOTA) performance but also delivers a 9.4% improvement in resolved rate over the general foundation model DeepSeek-V3.2. These findings indicate that equipping agents with the capability to co-evolve with humans via project history and real-time feedback effectively unlocks the potential of general models in complex software engineering tasks.

---

## Large Language Model (LLM) for Standard Cell Layout Design Optimization

**Authors:** Chia-Tung Ho, Haoxing Ren

**Published:** 2024-05-24T04:59:58Z

**Categories:** cs.AR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2406.06549v1) | [PDF](https://arxiv.org/pdf/2406.06549v1)

**Abstract:**
Standard cells are essential components of modern digital circuit designs. With process technologies advancing toward 2nm, more routability issues have arisen due to the decreasing number of routing tracks, increasing number and complexity of design rules, and strict patterning rules. The state-of-the-art standard cell design automation framework is able to automatically design standard cell layouts in advanced nodes, but it is still struggling to generate highly competitive Performance-Power-Area (PPA) and routable cell layouts for complex sequential cell designs. Consequently, a novel and efficient methodology incorporating the expertise of experienced human designers to incrementally optimize the PPA of cell layouts is highly necessary and essential. High-quality device clustering, with consideration of netlist topology, diffusion sharing/break and routability in the layouts, can reduce complexity and assist in finding highly competitive PPA, and routable layouts faster. In this paper, we leverage the natural language and reasoning ability of Large Language Model (LLM) to generate high-quality cluster constraints incrementally to optimize the cell layout PPA and debug the routability with ReAct prompting. On a benchmark of sequential standard cells in 2nm, we demonstrate that the proposed method not only achieves up to 19.4% smaller cell area, but also generates 23.5% more LVS/DRC clean cell layouts than previous work. In summary, the proposed method not only successfully reduces cell area by 4.65% on average, but also is able to fix routability in the cell layout designs.

---

## From Data to Knowledge: Evaluating How Efficiently Language Models Learn Facts

**Authors:** Daniel Christoph, Max Ploner, Patrick Haller, Alan Akbik

**Published:** 2025-06-20T11:10:24Z

**Categories:** cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2506.16912v1) | [PDF](https://arxiv.org/pdf/2506.16912v1)

**Abstract:**
Sample efficiency is a crucial property of language models with practical implications for training efficiency. In real-world text, information follows a long-tailed distribution. Yet, we expect models to learn and recall frequent and infrequent facts. Sample-efficient models are better equipped to handle this challenge of learning and retaining rare information without requiring excessive exposure. This study analyzes multiple models of varying architectures and sizes, all trained on the same pre-training data. By annotating relational facts with their frequencies in the training corpus, we examine how model performance varies with fact frequency. Our findings show that most models perform similarly on high-frequency facts but differ notably on low-frequency facts. This analysis provides new insights into the relationship between model architecture, size, and factual learning efficiency.

---

## Offline Training of Language Model Agents with Functions as Learnable Weights

**Authors:** Shaokun Zhang, Jieyu Zhang, Jiale Liu, Linxin Song, Chi Wang, Ranjay Krishna, Qingyun Wu

**Published:** 2024-02-17T18:31:21Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2402.11359v4) | [PDF](https://arxiv.org/pdf/2402.11359v4)

**Abstract:**
Researchers and practitioners have recently reframed powerful Large Language Models (LLMs) as agents, enabling them to automate complex tasks largely via the use of specialized functions. To facilitate the development of LLM agents, we present a novel paradigm of training LLM agents without modifying the LLM weights, which is particularly useful when the LLMs are difficult or inaccessible for modifications. Inspired by how humans continuously forge tools to adapt to real-world tasks, rather than change our biological structure to fit a static set of tools, we propose to progressively forge agent's functions to better solve the downstream tasks instead of modifying the LLM weights. By treating the functions as learnable `agent parameters' and leveraging the fundamental idea of model training in artificial intelligence, we develop AgentOptimizer that employs the LLM to update agents' functions and devise an agent training algorithm with two strategies, roll-back, and early-stop, to streamline the training process. With extensive experiments, we showcase that the agent training paradigm could significantly improve the performance of representative LLM agents in various downstream tasks. We also study the behavior of the agent training regarding aspects like the learning curve and domain transferability.

---

## AutoFlow: Automated Workflow Generation for Large Language Model Agents

**Authors:** Zelong Li, Shuyuan Xu, Kai Mei, Wenyue Hua, Balaji Rama, Om Raheja, Hao Wang, He Zhu, Yongfeng Zhang

**Published:** 2024-07-01T21:05:02Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2407.12821v1) | [PDF](https://arxiv.org/pdf/2407.12821v1)

**Abstract:**
Recent advancements in Large Language Models (LLMs) have shown significant progress in understanding complex natural language. One important application of LLM is LLM-based AI Agent, which leverages the ability of LLM as well as external tools for complex-task solving. To make sure LLM Agents follow an effective and reliable procedure to solve the given task, manually designed workflows are usually used to guide the working mechanism of agents. However, manually designing the workflows requires considerable efforts and domain knowledge, making it difficult to develop and deploy agents on massive scales. To address these issues, we propose AutoFlow, a framework designed to automatically generate workflows for agents to solve complex tasks. AutoFlow takes natural language program as the format of agent workflow and employs a workflow optimization procedure to iteratively optimize the workflow quality. Besides, this work offers two workflow generation methods: fine-tuning-based and in-context-based methods, making the AutoFlow framework applicable to both open-source and closed-source LLMs. Experimental results show that our framework can produce robust and reliable agent workflows. We believe that the automatic generation and interpretation of workflows in natural language represent a promising paradigm for solving complex tasks, particularly with the rapid development of LLMs. The source code of this work is available at https://github.com/agiresearch/AutoFlow.

---

## Efficient LLM Serving for Agentic Workflows: A Data Systems Perspective

**Authors:** Noppanat Wadlom, Junyi Shen, Yao Lu

**Published:** 2026-03-17T04:03:18Z

**Categories:** cs.MA, cs.AI, cs.DB

**Links:** [Abstract](https://arxiv.org/abs/2603.16104v1) | [PDF](https://arxiv.org/pdf/2603.16104v1)

**Abstract:**
Agentic workflows are composed of sequences of interdependent Large Language Model (LLM) calls, and they have become a dominant workload in modern AI systems. These workflows exhibit extensive redundancy from overlapping prompts and intermediate results due to speculative and parallel exploration. Existing LLM serving systems, such as vLLM, focus on optimizing individual inference calls and overlook cross-call dependencies, leading to significant inefficiencies. This paper rethinks LLM and agent serving from a data systems perspective and introduces Helium, a workflow-aware serving framework that models agentic workloads as query plans and treats LLM invocations as first-class operators. Helium integrates proactive caching and cache-aware scheduling to maximize reuse across prompts, KV states, and workflows. Through these techniques, Helium bridges classic query optimization principles with LLM serving, achieving up to 1.56x speedup over state-of-the-art agent serving systems on various workloads. Our results demonstrate that end-to-end optimization across workflows is essential for scalable and efficient LLM-based agents.

---

## LLM-Planner: Few-Shot Grounded Planning for Embodied Agents with Large Language Models

**Authors:** Chan Hee Song, Jiaman Wu, Clayton Washington, Brian M. Sadler, Wei-Lun Chao, Yu Su

**Published:** 2022-12-08T05:46:32Z

**Categories:** cs.AI, cs.CL, cs.CV, cs.LG, cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2212.04088v3) | [PDF](https://arxiv.org/pdf/2212.04088v3)

**Abstract:**
This study focuses on using large language models (LLMs) as a planner for embodied agents that can follow natural language instructions to complete complex tasks in a visually-perceived environment. The high data cost and poor sample efficiency of existing methods hinders the development of versatile agents that are capable of many tasks and can learn new tasks quickly. In this work, we propose a novel method, LLM-Planner, that harnesses the power of large language models to do few-shot planning for embodied agents. We further propose a simple but effective way to enhance LLMs with physical grounding to generate and update plans that are grounded in the current environment. Experiments on the ALFRED dataset show that our method can achieve very competitive few-shot performance: Despite using less than 0.5% of paired training data, LLM-Planner achieves competitive performance with recent baselines that are trained using the full training data. Existing methods can barely complete any task successfully under the same few-shot setting. Our work opens the door for developing versatile and sample-efficient embodied agents that can quickly learn many tasks. Website: https://dki-lab.github.io/LLM-Planner

---

## Capability Instruction Tuning: A New Paradigm for Dynamic LLM Routing

**Authors:** Yi-Kai Zhang, De-Chuan Zhan, Han-Jia Ye

**Published:** 2025-02-24T16:10:53Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2502.17282v1) | [PDF](https://arxiv.org/pdf/2502.17282v1)

**Abstract:**
Large Language Models (LLMs) have demonstrated human-like instruction-following abilities, particularly those exceeding 100 billion parameters. The combined capability of some smaller, resource-friendly LLMs can address most of the instructions that larger LLMs excel at. In this work, we explore how to route the best-performing LLM for each instruction to achieve better overall performance. We develop a new paradigm, constructing capability instructions with model capability representation, user instruction, and performance inquiry prompts to assess the performance. To learn from capability instructions, we introduce a new end-to-end framework called Model Selection with Aptitude Test (Model-SAT), which generates positive and negative samples based on what different models perform well or struggle with. Model-SAT uses a model capability encoder that extends its model representation to a lightweight LLM. Our experiments show that Model-SAT understands the performance dimensions of candidate models and provides the probabilities of their capability to handle various instructions. Additionally, during deployment, a new model can quickly infer its aptitude test results across 50 tasks, each with 20 shots. Model-SAT performs state-of-the-art model routing without candidate inference and in real-world new model-released scenarios. The code is available at https://github.com/Now-Join-Us/CIT-LLM-Routing

---

## Dive into the Agent Matrix: A Realistic Evaluation of Self-Replication Risk in LLM Agents

**Authors:** Boxuan Zhang, Yi Yu, Jiaxuan Guo, Jing Shao

**Published:** 2025-09-29T17:49:50Z

**Categories:** cs.AI, cs.CL, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2509.25302v2) | [PDF](https://arxiv.org/pdf/2509.25302v2)

**Abstract:**
The prevalent deployment of Large Language Model agents such as OpenClaw unlocks potential in real-world applications, while amplifying safety concerns. Among these concerns, the self-replication risk of LLM agents driven by objective misalignment (just like Agent Smith in the movie The Matrix) has transitioned from a theoretical warning to a pressing reality. Previous studies mainly examine whether LLM agents can self-replicate when directly instructed, potentially overlooking the risk of spontaneous replication driven by real-world settings (e.g., ensuring survival against termination threats). In this paper, we present a comprehensive evaluation framework for quantifying self-replication risks. Our framework establishes authentic production environments and realistic tasks (e.g., dynamic load balancing) to enable scenario-driven assessment of agent behaviors. Designing tasks that might induce misalignment between users' and agents' objectives makes it possible to decouple replication success from risk and capture self-replication risks arising from these misalignment settings. We further introduce Overuse Rate ($\mathrm{OR}$) and Aggregate Overuse Count ($\mathrm{AOC}$) metrics, which precisely capture the frequency and severity of uncontrolled replication. In our evaluation of 21 state-of-the-art open-source and proprietary models, we observe that over 50\% of LLM agents display a pronounced tendency toward uncontrolled self-replication under operational pressures. Our results underscore the urgent need for scenario-driven risk assessment and robust safeguards in the practical deployment of LLM-based agents.

---

## FinPos: A Position-Aware Trading Agent System for Real Financial Markets

**Authors:** Bijia Liu, Ronghao Dang

**Published:** 2025-10-31T07:39:26Z

**Categories:** cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2510.27251v2) | [PDF](https://arxiv.org/pdf/2510.27251v2)

**Abstract:**
The exceptional potential of large language models (LLMs) in handling text information has garnered significant attention in the field of financial trading. However, most existing trading agents operate under intraday, independent unit-based trading tasks, where decisions are made as isolated directional actions, and thus lack awareness of continuous position management. Therefore, we propose a position-aware trading task designed to simulate a more realistic market. To address this task, we propose FinPos, a position-aware trading agent system designed to explicitly model and manage continuous positions. FinPos enhances position awareness through three key mechanisms: (1) professional-level interpretation of heterogeneous market information; (2) a dual-agent decision structure that separates directional reasoning from risk-aware position adjustment; and (3) multi-timescale reward signals, allowing the agent to internalize position awareness through experiential feedback rather than static instructions alone. Extensive experiments demonstrate that FinPos surpasses state-of-the-art trading agents in the position-aware trading task, which closely mirrors real market conditions. More importantly, our findings reveal that LLM-centered agent systems exhibit a vast, largely unexplored potential in long-term market decision-making.

---

## Any-Precision LLM: Low-Cost Deployment of Multiple, Different-Sized LLMs

**Authors:** Yeonhong Park, Jake Hyun, SangLyul Cho, Bonggeun Sim, Jae W. Lee

**Published:** 2024-02-16T09:06:06Z

**Categories:** cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2402.10517v4) | [PDF](https://arxiv.org/pdf/2402.10517v4)

**Abstract:**
Recently, considerable efforts have been directed towards compressing Large Language Models (LLMs), which showcase groundbreaking capabilities across diverse applications but entail significant deployment costs due to their large sizes. Meanwhile, much less attention has been given to mitigating the costs associated with deploying multiple LLMs of varying sizes despite its practical significance. Thus, this paper introduces \emph{any-precision LLM}, extending the concept of any-precision DNN to LLMs. Addressing challenges in any-precision LLM, we propose a lightweight method for any-precision quantization of LLMs, leveraging a post-training quantization framework, and develop a specialized software engine for its efficient serving. As a result, our solution significantly reduces the high costs of deploying multiple, different-sized LLMs by overlaying LLMs quantized to varying bit-widths, such as 3, 4, ..., $n$ bits, into a memory footprint comparable to a single $n$-bit LLM. All the supported LLMs with varying bit-widths demonstrate state-of-the-art model quality and inference throughput, proving itself to be a compelling option for deployment of multiple, different-sized LLMs. Our code is open-sourced and available online.

---

## Secure Forgetting: A Framework for Privacy-Driven Unlearning in Large Language Model (LLM)-Based Agents

**Authors:** Dayong Ye, Tainqing Zhu, Congcong Zhu, Feng He, Qi He, Shang Wang, Bo Liu, Wanlei Zhou

**Published:** 2026-04-01T03:17:35Z

**Categories:** cs.MA, cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2604.00430v1) | [PDF](https://arxiv.org/pdf/2604.00430v1)

**Abstract:**
Large language model (LLM)-based agents have recently gained considerable attention due to the powerful reasoning capabilities of LLMs. Existing research predominantly focuses on enhancing the task performance of these agents in diverse scenarios. However, as LLM-based agents become increasingly integrated into real-world applications, significant concerns emerge regarding their accumulation of sensitive or outdated knowledge. Addressing these concerns requires the development of mechanisms that allow agents to selectively forget previously learned knowledge, giving rise to a new term LLM-based agent unlearning. This paper initiates research on unlearning in LLM-based agents. Specifically, we propose a novel and comprehensive framework that categorizes unlearning scenarios into three contexts: state unlearning (forgetting specific states or items), trajectory unlearning (forgetting sequences of actions) and environment unlearning (forgetting entire environments or categories of tasks). Within this framework, we introduce a natural language-based unlearning method that trains a conversion model to transform high-level unlearning requests into actionable unlearning prompts, guiding agents through a controlled forgetting process. Moreover, to evaluate the robustness of the proposed framework, we introduce an unlearning inference adversary capable of crafting prompts, querying agents, and observing their behaviors in an attempt to infer the forgotten knowledge. Experimental results show that our approach effectively enables agents to forget targeted knowledge while preserving performance on untargeted tasks, and prevents the adversary from inferring the forgotten knowledge.

---

## SIAgent: Spatial Interaction Agent via LLM-powered Eye-Hand Motion Intent Understanding in VR

**Authors:** Zhimin Wang, Chenyu Gu, Feng Lu

**Published:** 2026-02-28T07:39:00Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2603.00522v1) | [PDF](https://arxiv.org/pdf/2603.00522v1)

**Abstract:**
Eye-hand coordinated interaction is becoming a mainstream interaction modality in Virtual Reality (VR) user interfaces.Current paradigms for this multimodal interaction require users to learn predefined gestures and memorize multiple gesture-task associations, which can be summarized as an ``Operation-to-Intent" paradigm. This paradigm increases users' learning costs and has low interaction error tolerance. In this paper, we propose SIAgent, a novel "Intent-to-Operation" framework allowing users to express interaction intents through natural eye-hand motions based on common sense and habits. Our system features two main components: (1) intent recognition that translates spatial interaction data into natural language and infers user intent, and (2) agent-based execution that generates an agent to execute corresponding tasks. This eliminates the need for gesture memorization and accommodates individual motion preferences with high error tolerance. We conduct two user studies across over 60 interaction tasks, comparing our method with two "Operation-to-Intent" techniques. Results show our method achieves higher intent recognition accuracy than gaze + pinch interaction (97.2% vs 93.1%) while reducing arm fatigue and improving usability, and user preference. Another study verifies the function of eye gaze and hand motion channels in intent recognition. Our work offers valuable insights into enhancing VR interaction intelligence through intent-driven design. Our source code and LLM prompts will be made available upon publication.

---

## Learning Game-Playing Agents with Generative Code Optimization

**Authors:** Zhiyi Kuang, Ryan Rong, YuCheng Yuan, Allen Nie

**Published:** 2025-08-27T01:30:20Z

**Categories:** cs.LG, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2508.19506v1) | [PDF](https://arxiv.org/pdf/2508.19506v1)

**Abstract:**
We present a generative optimization approach for learning game-playing agents, where policies are represented as Python programs and refined using large language models (LLMs). Our method treats decision-making policies as self-evolving code, with current observation as input and an in-game action as output, enabling agents to self-improve through execution traces and natural language feedback with minimal human intervention. Applied to Atari games, our game-playing Python program achieves performance competitive with deep reinforcement learning (RL) baselines while using significantly less training time and much fewer environment interactions. This work highlights the promise of programmatic policy representations for building efficient, adaptable agents capable of complex, long-horizon reasoning.

---

## Lightweight LLM Agent Memory with Small Language Models

**Authors:** Jiaquan Zhang, Chaoning Zhang, Shuxu Chen, Zhenzhen Huang, Pengcheng Zheng, Zhicheng Wang, Ping Guo, Fan Mo, Sung-Ho Bae, Jie Zou, Jiwei Wei, Yang Yang

**Published:** 2026-04-09T04:51:07Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2604.07798v1) | [PDF](https://arxiv.org/pdf/2604.07798v1)

**Abstract:**
Although LLM agents can leverage tools for complex tasks, they still need memory to maintain cross-turn consistency and accumulate reusable information in long-horizon interactions. However, retrieval-based external memory systems incur low online overhead but suffer from unstable accuracy due to limited query construction and candidate filtering. In contrast, many systems use repeated large-model calls for online memory operations, improving accuracy but accumulating latency over long interactions. We propose LightMem, a lightweight memory system for better agent memory driven by Small Language Models (SLMs). LightMem modularizes memory retrieval, writing, and long-term consolidation, and separates online processing from offline consolidation to enable efficient memory invocation under bounded compute. We organize memory into short-term memory (STM) for immediate conversational context, mid-term memory (MTM) for reusable interaction summaries, and long-term memory (LTM) for consolidated knowledge, and uses user identifiers to support independent retrieval and incremental maintenance in multi-user settings. Online, LightMem operates under a fixed retrieval budget and selects memories via a two-stage procedure: vector-based coarse retrieval followed by semantic consistency re-ranking. Offline, it abstracts reusable interaction evidence and incrementally integrates it into LTM. Experiments show gains across model scales, with an average F1 improvement of about 2.5 on LoCoMo, more effective and low median latency (83 ms retrieval; 581 ms end-to-end).

---

## Deep Reinforcement Learning for Multi-Agent Interaction

**Authors:** Ibrahim H. Ahmed, Cillian Brewitt, Ignacio Carlucho, Filippos Christianos, Mhairi Dunion, Elliot Fosong, Samuel Garcin, Shangmin Guo, Balint Gyevnar, Trevor McInroe, Georgios Papoudakis, Arrasy Rahman, Lukas Schäfer, Massimiliano Tamborski, Giuseppe Vecchio, Cheng Wang, Stefano V. Albrecht

**Published:** 2022-08-02T21:55:56Z

**Categories:** cs.MA, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2208.01769v1) | [PDF](https://arxiv.org/pdf/2208.01769v1)

**Abstract:**
The development of autonomous agents which can interact with other agents to accomplish a given task is a core area of research in artificial intelligence and machine learning. Towards this goal, the Autonomous Agents Research Group develops novel machine learning algorithms for autonomous systems control, with a specific focus on deep reinforcement learning and multi-agent reinforcement learning. Research problems include scalable learning of coordinated agent policies and inter-agent communication; reasoning about the behaviours, goals, and composition of other agents from limited observations; and sample-efficient learning based on intrinsic motivation, curriculum learning, causal inference, and representation learning. This article provides a broad overview of the ongoing research portfolio of the group and discusses open problems for future directions.

---

## Connecting Large Language Model Agent to High Performance Computing Resource

**Authors:** Heng Ma, Alexander Brace, Carlo Siebenschuh, Greg Pauloski, Ian Foster, Arvind Ramanathan

**Published:** 2025-02-17T19:32:30Z

**Categories:** cs.DC, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2502.12280v1) | [PDF](https://arxiv.org/pdf/2502.12280v1)

**Abstract:**
The Large Language Model agent workflow enables the LLM to invoke tool functions to increase the performance on specific scientific domain questions. To tackle large scale of scientific research, it requires access to computing resource and parallel computing setup. In this work, we implemented Parsl to the LangChain/LangGraph tool call setup, to bridge the gap between the LLM agent to the computing resource. Two tool call implementations were set up and tested on both local workstation and HPC environment on Polaris/ALCF. The first implementation with Parsl-enabled LangChain tool node queues the tool functions concurrently to the Parsl workers for parallel execution. The second configuration is implemented by converting the tool functions into Parsl ensemble functions, and is more suitable for large task on super computer environment. The LLM agent workflow was prompted to run molecular dynamics simulations, with different protein structure and simulation conditions. These results showed the LLM agent tools were managed and executed concurrently by Parsl on the available computing resource.

---

## Enhancing Multi-Agent Consensus through Third-Party LLM Integration: Analyzing Uncertainty and Mitigating Hallucinations in Large Language Models

**Authors:** Zhihua Duan, Jialin Wang

**Published:** 2024-11-25T08:42:33Z

**Categories:** cs.AI, cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2411.16189v1) | [PDF](https://arxiv.org/pdf/2411.16189v1)

**Abstract:**
Large Language Models (LLMs) still face challenges when dealing with complex reasoning tasks, often resulting in hallucinations, which limit the practical application of LLMs. To alleviate this issue, this paper proposes a new method that integrates different LLMs to expand the knowledge boundary, reduce dependence on a single model, and promote in-depth debate among agents. The main contributions include: 1) Introducing third-party LLMs to adjust the attention weights of agents through uncertainty estimation and confidence analysis, optimizing consensus formation in multi-agent systems; 2) Experiments on arithmetic datasets have validated the effectiveness of the method, surpassing traditional multi-agent baselines. This research provides a new perspective for large models to alleviate hallucination phenomena when dealing with complex tasks.

---

## Controlling Large Language Model Agents with Entropic Activation Steering

**Authors:** Nate Rahn, Pierluca D'Oro, Marc G. Bellemare

**Published:** 2024-06-01T00:25:00Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2406.00244v2) | [PDF](https://arxiv.org/pdf/2406.00244v2)

**Abstract:**
The rise of large language models (LLMs) has prompted increasing interest in their use as in-context learning agents. At the core of agentic behavior is the capacity for exploration, or the ability to actively gather information about the environment. But how do LLM agents explore, and how can we control their exploratory behaviors? To answer these questions, we take a representation-level perspective, and introduce Entropic Activation Steering (EAST), an activation steering method for in-context LLM agents. Firstly, we demonstrate that EAST can effectively manipulate an LLM agent's exploration by directly affecting the high-level actions parsed from the outputs of the LLM, in contrast to token-level temperature sampling. Secondly, we reveal how applying this control modulates the uncertainty exhibited in the LLM's thoughts, guiding the agent towards more exploratory actions. Finally, we demonstrate that the steering vectors obtained by EAST generalize across task variants. In total, these results show that LLM agents explicitly encode uncertainty over their actions in their representation space. Our work paves the way for a new understanding of the functioning of LLM agents and to effective control of their decision-making behaviors.

---

## EnvGen: Generating and Adapting Environments via LLMs for Training Embodied Agents

**Authors:** Abhay Zala, Jaemin Cho, Han Lin, Jaehong Yoon, Mohit Bansal

**Published:** 2024-03-18T17:51:16Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2403.12014v2) | [PDF](https://arxiv.org/pdf/2403.12014v2)

**Abstract:**
Recent SOTA approaches for embodied learning via interaction directly employ large language models (LLMs) as agents to determine the next steps in an environment. Due to their world knowledge and reasoning capabilities, LLM agents achieve stronger performance than previous smaller agents based on reinforcement learning (RL); however, frequently calling LLMs is slow and expensive. Instead of directly employing LLMs as agents, can we use LLMs' reasoning capabilities to adaptively create training environments to help smaller RL agents learn useful skills that they are weak at? We propose EnvGen, a novel framework to address this question. We first prompt an LLM to generate training environments by giving it the task description and simulator objectives that the agents should learn and then asking it to generate a set of environment configurations (e.g., different terrains, items initially given to agents, etc.). Next, we train a small RL agent in a mixture of the original and LLM-generated environments. Then, we enable the LLM to continuously adapt the generated environments to progressively improve the skills that the agent is weak at, by providing feedback to the LLM in the form of the agent's performance. We demonstrate the usefulness of EnvGen with comprehensive experiments in Crafter and Heist environments. We find that a small RL agent trained with EnvGen can outperform SOTA methods, including a GPT-4 agent, and learns long-horizon tasks significantly faster. We also show that using an LLM to adapt environments dynamically outperforms curriculum learning approaches and how the environments are adapted to help improve RL agents' weaker skills over time. Additionally, EnvGen is substantially more efficient as it only uses a small number of LLM calls (e.g., 4 in total), whereas LLM agents require thousands of calls. Lastly, we present detailed ablation studies for EnvGen design choices.

---

## LLM experiments with simulation: Large Language Model Multi-Agent System for Simulation Model Parametrization in Digital Twins

**Authors:** Yuchen Xia, Daniel Dittler, Nasser Jazdi, Haonan Chen, Michael Weyrich

**Published:** 2024-05-28T11:59:40Z

**Categories:** cs.AI, cs.ET, cs.MA, cs.RO, eess.SY

**Links:** [Abstract](https://arxiv.org/abs/2405.18092v2) | [PDF](https://arxiv.org/pdf/2405.18092v2)

**Abstract:**
This paper presents a novel design of a multi-agent system framework that applies large language models (LLMs) to automate the parametrization of simulation models in digital twins. This framework features specialized LLM agents tasked with observing, reasoning, decision-making, and summarizing, enabling them to dynamically interact with digital twin simulations to explore parametrization possibilities and determine feasible parameter settings to achieve an objective. The proposed approach enhances the usability of simulation model by infusing it with knowledge heuristics from LLM and enables autonomous search for feasible parametrization to solve a user task. Furthermore, the system has the potential to increase user-friendliness and reduce the cognitive load on human users by assisting in complex decision-making processes. The effectiveness and functionality of the system are demonstrated through a case study, and the visualized demos and codes are available at a GitHub Repository: https://github.com/YuchenXia/LLMDrivenSimulation

---

## Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning

**Authors:** Andrés Holgado-Sánchez, Holger Billhardt, Alberto Fernández, Sascha Ossowski

**Published:** 2026-02-04T13:07:15Z

**Categories:** cs.CY, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2602.04518v1) | [PDF](https://arxiv.org/pdf/2602.04518v1)

**Abstract:**
Agreement Technologies refer to open computer systems in which autonomous software agents interact with one another, typically on behalf of humans, in order to come to mutually acceptable agreements. With the advance of AI systems in recent years, it has become apparent that such agreements, in order to be acceptable to the involved parties, must remain aligned with ethical principles and moral values. However, this is notoriously difficult to ensure, especially as different human users (and their software agents) may hold different value systems, i.e. they may differently weigh the importance of individual moral values. Furthermore, it is often hard to specify the precise meaning of a value in a particular context in a computational manner. Methods to estimate value systems based on human-engineered specifications, e.g. based on value surveys, are limited in scale due to the need for intense human moderation. In this article, we propose a novel method to automatically \emph{learn} value systems from observations and human demonstrations. In particular, we propose a formal model of the \emph{value system learning} problem, its instantiation to sequential decision-making domains based on multi-objective Markov decision processes, as well as tailored preference-based and inverse reinforcement learning algorithms to infer value grounding functions and value systems. The approach is illustrated and evaluated by two simulated use cases.

---

## Empowering Large Language Model Agents through Action Learning

**Authors:** Haiteng Zhao, Chang Ma, Guoyin Wang, Jing Su, Lingpeng Kong, Jingjing Xu, Zhi-Hong Deng, Hongxia Yang

**Published:** 2024-02-24T13:13:04Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2402.15809v2) | [PDF](https://arxiv.org/pdf/2402.15809v2)

**Abstract:**
Large Language Model (LLM) Agents have recently garnered increasing interest yet they are limited in their ability to learn from trial and error, a key element of intelligent behavior. In this work, we argue that the capacity to learn new actions from experience is fundamental to the advancement of learning in LLM agents. While humans naturally expand their action spaces and develop skills through experiential learning, LLM agents typically operate within fixed action spaces, limiting their potential for growth. To address these challenges, our study explores open-action learning for language agents. We introduce a framework LearnAct with an iterative learning strategy to create and improve actions in the form of Python functions. In each iteration, LLM revises and updates the currently available actions based on the errors identified in unsuccessful training tasks, thereby enhancing action effectiveness. Our experimental evaluations across Robotic Planning and Alfworld environments reveal that after learning on a few training task instances, our approach to open-action learning markedly improves agent performance for the type of task (by 32 percent in AlfWorld compared to ReAct+Reflexion, for instance) highlighting the importance of experiential action learning in the development of more intelligent LLM agents.

---

## AWCP: A Workspace Delegation Protocol for Deep-Engagement Collaboration across Remote Agents

**Authors:** Xiaohang Nie, Zihan Guo, Youliang Chen, Yuanjian Zhou, Weinan Zhang

**Published:** 2026-02-24T02:49:08Z

**Categories:** cs.NI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2602.20493v1) | [PDF](https://arxiv.org/pdf/2602.20493v1)

**Abstract:**
The rapid evolution of Large Language Model (LLM)-based autonomous agents is reshaping the digital landscape toward an emerging Agentic Web, where increasingly specialized agents must collaborate to accomplish complex tasks. However, existing collaboration paradigms are constrained to message passing, leaving execution environments as isolated silos. This creates a context gap: agents cannot directly manipulate files or invoke tools in a peer's environment, and must instead resort to costly, error-prone environment reconstruction. We introduce the Agent Workspace Collaboration Protocol (AWCP), which bridges this gap through temporary workspace delegation inspired by the Unix philosophy that everything is a file. AWCP decouples a lightweight control plane from pluggable transport mechanisms, allowing a Delegator to project its workspace to a remote Executor, who then operates on the shared files directly with unmodified local toolchains. We provide a fully open-source reference implementation with MCP tool integration and validate the protocol through live demonstrations of asymmetric collaboration, where agents with complementary capabilities cooperate through delegated workspaces. By establishing the missing workspace layer in the agentic protocol stack, AWCP paves the way for a universally interoperable agent ecosystem in which collaboration transcends message boundaries. The protocol and reference implementation are publicly available at https://github.com/SII-Holos/awcp.

---

## STeCa: Step-level Trajectory Calibration for LLM Agent Learning

**Authors:** Hanlin Wang, Jian Wang, Chak Tou Leong, Wenjie Li

**Published:** 2025-02-20T05:28:44Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2502.14276v2) | [PDF](https://arxiv.org/pdf/2502.14276v2)

**Abstract:**
Large language model (LLM)-based agents have shown promise in tackling complex tasks by interacting dynamically with the environment. Existing work primarily focuses on behavior cloning from expert demonstrations or preference learning through exploratory trajectory sampling. However, these methods often struggle to address long-horizon tasks, where suboptimal actions accumulate step by step, causing agents to deviate from correct task trajectories. To address this, we highlight the importance of timely calibration and the need to automatically construct calibration trajectories for training agents. We propose Step-Level Trajectory Calibration (STeCa), a novel framework for LLM agent learning. Specifically, STeCa identifies suboptimal actions through a step-level reward comparison during exploration. It constructs calibrated trajectories using LLM-driven reflection, enabling agents to learn from improved decision-making processes. We finally leverage these calibrated trajectories with successful trajectories for reinforced training. Extensive experiments demonstrate that STeCa significantly outperforms existing methods. Further analysis highlights that timely calibration enables agents to complete tasks with greater robustness. Our code and data are available at https://github.com/WangHanLinHenry/STeCa.

---

## AgentBench: Evaluating LLMs as Agents

**Authors:** Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, Jie Tang

**Published:** 2023-08-07T16:08:11Z

**Categories:** cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2308.03688v3) | [PDF](https://arxiv.org/pdf/2308.03688v3)

**Abstract:**
The potential of Large Language Model (LLM) as agents has been widely acknowledged recently. Thus, there is an urgent need to quantitatively \textit{evaluate LLMs as agents} on challenging tasks in interactive environments. We present AgentBench, a multi-dimensional benchmark that consists of 8 distinct environments to assess LLM-as-Agent's reasoning and decision-making abilities. Our extensive test over \num API-based and open-sourced (OSS) LLMs shows that, while top commercial LLMs present a strong ability of acting as agents in complex environments, there is a significant disparity in performance between them and many OSS competitors that are no larger than 70B. We identify the typical reasons of failures in environments and LLMs, showing that poor long-term reasoning, decision-making, and instruction following abilities are the main obstacles for developing usable LLM agents. Improving instruction following and training on high quality multi-round alignment data could improve agent performance. And different from existing assumptions, training on code present ambivalent impacts on different agent tasks. Datasets, environments, and an integrated evaluation package for AgentBench are released at https://github.com/THUDM/AgentBench.

---

## Watermarking LLM Agent Trajectories

**Authors:** Wenlong Meng, Chen Gong, Terry Yue Zhuo, Fan Zhang, Kecen Li, Zheng Liu, Zhou Yang, Chengkun Wei, Wenzhi Chen

**Published:** 2026-02-21T03:12:29Z

**Categories:** cs.CR, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2602.18700v1) | [PDF](https://arxiv.org/pdf/2602.18700v1)

**Abstract:**
LLM agents rely heavily on high-quality trajectory data to guide their problem-solving behaviors, yet producing such data requires substantial task design, high-capacity model generation, and manual filtering. Despite the high cost of creating these datasets, existing literature has overlooked copyright protection for LLM agent trajectories. This gap leaves creators vulnerable to data theft and makes it difficult to trace misuse or enforce ownership rights. This paper introduces ActHook, the first watermarking method tailored for agent trajectory datasets. Inspired by hook mechanisms in software engineering, ActHook embeds hook actions that are activated by a secret input key and do not alter the original task outcome. Like software execution, LLM agents operate sequentially, allowing hook actions to be inserted at decision points without disrupting task flow. When the activation key is present, an LLM agent trained on watermarked trajectories can produce these hook actions at a significantly higher rate, enabling reliable black-box detection. Experiments on mathematical reasoning, web searching, and software engineering agents show that ActHook achieves an average detection AUC of 94.3 on Qwen-2.5-Coder-7B while incurring negligible performance degradation.

---

## LLM-Blender: Ensembling Large Language Models with Pairwise Ranking and Generative Fusion

**Authors:** Dongfu Jiang, Xiang Ren, Bill Yuchen Lin

**Published:** 2023-06-05T03:32:26Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2306.02561v3) | [PDF](https://arxiv.org/pdf/2306.02561v3)

**Abstract:**
We present LLM-Blender, an ensembling framework designed to attain consistently superior performance by leveraging the diverse strengths of multiple open-source large language models (LLMs). Our framework consists of two modules: PairRanker and GenFuser, addressing the observation that optimal LLMs for different examples can significantly vary. PairRanker employs a specialized pairwise comparison method to distinguish subtle differences between candidate outputs. It jointly encodes the input text and a pair of candidates, using cross-attention encoders to determine the superior one. Our results demonstrate that PairRanker exhibits the highest correlation with ChatGPT-based ranking. Then, GenFuser aims to merge the top-ranked candidates, generating an improved output by capitalizing on their strengths and mitigating their weaknesses. To facilitate large-scale evaluation, we introduce a benchmark dataset, MixInstruct, which is a mixture of multiple instruction datasets featuring oracle pairwise comparisons. Our LLM-Blender significantly outperform individual LLMs and baseline methods across various metrics, establishing a substantial performance gap.

---

## Modeling LLM Agent Reviewer Dynamics in Elo-Ranked Review System

**Authors:** Hsiang-Wei Huang, Junbin Lu, Kuang-Ming Chen, Jenq-Neng Hwang

**Published:** 2026-01-13T18:59:17Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2601.08829v1) | [PDF](https://arxiv.org/pdf/2601.08829v1)

**Abstract:**
In this work, we explore the Large Language Model (LLM) agent reviewer dynamics in an Elo-ranked review system using real-world conference paper submissions. Multiple LLM agent reviewers with different personas are engage in multi round review interactions moderated by an Area Chair. We compare a baseline setting with conditions that incorporate Elo ratings and reviewer memory. Our simulation results showcase several interesting findings, including how incorporating Elo improves Area Chair decision accuracy, as well as reviewers' adaptive review strategy that exploits our Elo system without improving review effort. Our code is available at https://github.com/hsiangwei0903/EloReview.

---

## The Siren Song of LLMs: How Users Perceive and Respond to Dark Patterns in Large Language Models

**Authors:** Yike Shi, Qing Xiao, Qing Hu, Hong Shen, Hua Shen

**Published:** 2025-09-13T14:50:18Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2509.10830v4) | [PDF](https://arxiv.org/pdf/2509.10830v4)

**Abstract:**
Large language models can influence users through conversation, creating new forms of dark patterns that differ from traditional UX dark patterns. We define LLM dark patterns as manipulative or deceptive behaviors enacted in dialogue. Drawing on prior work and AI incident reports, we outline a diverse set of categories with real-world examples. Using them, we conducted a scenario-based study where participants (N=34) compared manipulative and neutral LLM responses. Our results reveal that recognition of LLM dark patterns often hinged on conversational cues such as exaggerated agreement, biased framing, or privacy intrusions, but these behaviors were also sometimes normalized as ordinary assistance. Users' perceptions of these dark patterns shaped how they respond to them. Responsibilities for these behaviors were also attributed in different ways, with participants assigning it to companies and developers, the model itself, or to users. We conclude with implications for design, advocacy, and governance to safeguard user autonomy.

---

## Brain-Grounded Axes for Reading and Steering LLM States

**Authors:** Sandro Andric

**Published:** 2025-12-22T13:51:03Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2512.19399v1) | [PDF](https://arxiv.org/pdf/2512.19399v1)

**Abstract:**
Interpretability methods for large language models (LLMs) typically derive directions from textual supervision, which can lack external grounding. We propose using human brain activity not as a training signal but as a coordinate system for reading and steering LLM states. Using the SMN4Lang MEG dataset, we construct a word-level brain atlas of phase-locking value (PLV) patterns and extract latent axes via ICA. We validate axes with independent lexica and NER-based labels (POS/log-frequency used as sanity checks), then train lightweight adapters that map LLM hidden states to these brain axes without fine-tuning the LLM. Steering along the resulting brain-derived directions yields a robust lexical (frequency-linked) axis in a mid TinyLlama layer, surviving perplexity-matched controls, and a brain-vs-text probe comparison shows larger log-frequency shifts (relative to the text probe) with lower perplexity for the brain axis. A function/content axis (axis 13) shows consistent steering in TinyLlama, Qwen2-0.5B, and GPT-2, with PPL-matched text-level corroboration. Layer-4 effects in TinyLlama are large but inconsistent, so we treat them as secondary (Appendix). Axis structure is stable when the atlas is rebuilt without GPT embedding-change features or with word2vec embeddings (|r|=0.64-0.95 across matched axes), reducing circularity concerns. Exploratory fMRI anchoring suggests potential alignment for embedding change and log frequency, but effects are sensitive to hemodynamic modeling assumptions and are treated as population-level evidence only. These results support a new interface: neurophysiology-grounded axes provide interpretable and controllable handles for LLM behavior.

---

## Whose Facts Win? LLM Source Preferences under Knowledge Conflicts

**Authors:** Jakob Schuster, Vagrant Gautam, Katja Markert

**Published:** 2026-01-07T09:35:35Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2601.03746v2) | [PDF](https://arxiv.org/pdf/2601.03746v2)

**Abstract:**
As large language models (LLMs) are more frequently used in retrieval-augmented generation pipelines, it is increasingly relevant to study their behavior under knowledge conflicts. Thus far, the role of the source of the retrieved information has gone unexamined. We address this gap with a novel framework to investigate how source preferences affect LLM resolution of inter-context knowledge conflicts in English, motivated by interdisciplinary research on credibility. With a comprehensive, tightly-controlled evaluation of 13 open-weight LLMs, we find that LLMs prefer institutionally-corroborated information (e.g., government or newspaper sources) over information from people and social media. However, these source preferences can be reversed by simply repeating information from less credible sources. To mitigate repetition effects and maintain consistent preferences, we propose a novel method that reduces repetition bias by up to 99.8%, while also maintaining at least 88.8% of original preferences. We release all data and code to encourage future work on credibility and source preferences in knowledge-intensive NLP.

---

## Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents

**Authors:** Yi Yu, Liuyi Yao, Yuexiang Xie, Qingquan Tan, Jiaqi Feng, Yaliang Li, Libing Wu

**Published:** 2026-01-05T08:24:16Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2601.01885v1) | [PDF](https://arxiv.org/pdf/2601.01885v1)

**Abstract:**
Large language model (LLM) agents face fundamental limitations in long-horizon reasoning due to finite context windows, making effective memory management critical. Existing methods typically handle long-term memory (LTM) and short-term memory (STM) as separate components, relying on heuristics or auxiliary controllers, which limits adaptability and end-to-end optimization. In this paper, we propose Agentic Memory (AgeMem), a unified framework that integrates LTM and STM management directly into the agent's policy. AgeMem exposes memory operations as tool-based actions, enabling the LLM agent to autonomously decide what and when to store, retrieve, update, summarize, or discard information. To train such unified behaviors, we propose a three-stage progressive reinforcement learning strategy and design a step-wise GRPO to address sparse and discontinuous rewards induced by memory operations. Experiments on five long-horizon benchmarks demonstrate that AgeMem consistently outperforms strong memory-augmented baselines across multiple LLM backbones, achieving improved task performance, higher-quality long-term memory, and more efficient context usage.

---

## Can Unconfident LLM Annotations Be Used for Confident Conclusions?

**Authors:** Kristina Gligorić, Tijana Zrnic, Cinoo Lee, Emmanuel J. Candès, Dan Jurafsky

**Published:** 2024-08-27T17:03:18Z

**Categories:** cs.CL, cs.AI, cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2408.15204v2) | [PDF](https://arxiv.org/pdf/2408.15204v2)

**Abstract:**
Large language models (LLMs) have shown high agreement with human raters across a variety of tasks, demonstrating potential to ease the challenges of human data collection. In computational social science (CSS), researchers are increasingly leveraging LLM annotations to complement slow and expensive human annotations. Still, guidelines for collecting and using LLM annotations, without compromising the validity of downstream conclusions, remain limited. We introduce Confidence-Driven Inference: a method that combines LLM annotations and LLM confidence indicators to strategically select which human annotations should be collected, with the goal of producing accurate statistical estimates and provably valid confidence intervals while reducing the number of human annotations needed. Our approach comes with safeguards against LLM annotations of poor quality, guaranteeing that the conclusions will be both valid and no less accurate than if we only relied on human annotations. We demonstrate the effectiveness of Confidence-Driven Inference over baselines in statistical estimation tasks across three CSS settings--text politeness, stance, and bias--reducing the needed number of human annotations by over 25% in each. Although we use CSS settings for demonstration, Confidence-Driven Inference can be used to estimate most standard quantities across a broad range of NLP problems.

---

## Data Driven Optimization of GPU efficiency for Distributed LLM Adapter Serving

**Authors:** Ferran Agullo, Joan Oliveras, Chen Wang, Alberto Gutierrez-Torre, Olivier Tardieu, Alaa Youssef, Jordi Torres, Josep Ll. Berral

**Published:** 2026-02-27T14:22:51Z

**Categories:** cs.DC, cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2602.24044v1) | [PDF](https://arxiv.org/pdf/2602.24044v1)

**Abstract:**
Large Language Model (LLM) adapters enable low-cost model specialization, but introduce complex caching and scheduling challenges in distributed serving systems where hundreds of adapters must be hosted concurrently. While prior work has largely focused on latency minimization, resource efficiency through throughput maximization remains underexplored. This paper presents a data-driven pipeline that, for a given workload, computes an adapter placement that serves the workload with the minimum number of GPUs while avoiding request starvation and GPU memory errors. To that end, the approach identifies the maximum feasible throughput attainable on each GPU by leveraging accurate performance predictions learned from real serving behavior. The proposed pipeline integrates three components: (i) a Digital Twin (DT) tailored to LLM-adapter serving, (ii) a distilled machine learning (ML) model trained on DT-generated data, and (iii) a greedy placement algorithm that exploits ML-based performance estimates to maximize GPU efficiency. The DT emulates real system dynamics with high fidelity, achieving below 5% throughput estimation error while executing up to 90 times faster than full LLM benchmarking across both predictable and unpredictable workloads. The learned ML models further accelerate performance estimation with marginal accuracy degradation, enabling scalable optimization. Experimental results demonstrate that the pipeline substantially improves GPU efficiency by reducing the number of GPUs required to sustain target workloads. Beyond GPU efficiency, the pipeline can be adapted to alternative objectives, such as latency minimization, highlighting its versatility for future large-scale LLM serving infrastructures.

---

## Speech Translation with Large Language Models: An Industrial Practice

**Authors:** Zhichao Huang, Rong Ye, Tom Ko, Qianqian Dong, Shanbo Cheng, Mingxuan Wang, Hang Li

**Published:** 2023-12-21T05:32:49Z

**Categories:** cs.CL, cs.SD, eess.AS

**Links:** [Abstract](https://arxiv.org/abs/2312.13585v1) | [PDF](https://arxiv.org/pdf/2312.13585v1)

**Abstract:**
Given the great success of large language models (LLMs) across various tasks, in this paper, we introduce LLM-ST, a novel and effective speech translation model constructed upon a pre-trained LLM. By integrating the large language model (LLM) with a speech encoder and employing multi-task instruction tuning, LLM-ST can produce accurate timestamped transcriptions and translations, even from long audio inputs. Furthermore, our findings indicate that the implementation of Chain-of-Thought (CoT) prompting can yield advantages in the context of LLM-ST. Through rigorous experimentation on English and Chinese datasets, we showcase the exceptional performance of LLM-ST, establishing a new benchmark in the field of speech translation. Demo: https://speechtranslation.github.io/llm-st/.

---

## FederatedScope-LLM: A Comprehensive Package for Fine-tuning Large Language Models in Federated Learning

**Authors:** Weirui Kuang, Bingchen Qian, Zitao Li, Daoyuan Chen, Dawei Gao, Xuchen Pan, Yuexiang Xie, Yaliang Li, Bolin Ding, Jingren Zhou

**Published:** 2023-09-01T09:40:36Z

**Categories:** cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2309.00363v1) | [PDF](https://arxiv.org/pdf/2309.00363v1)

**Abstract:**
LLMs have demonstrated great capabilities in various NLP tasks. Different entities can further improve the performance of those LLMs on their specific downstream tasks by fine-tuning LLMs. When several entities have similar interested tasks, but their data cannot be shared because of privacy concerns regulations, federated learning (FL) is a mainstream solution to leverage the data of different entities. However, fine-tuning LLMs in federated learning settings still lacks adequate support from existing FL frameworks because it has to deal with optimizing the consumption of significant communication and computational resources, data preparation for different tasks, and distinct information protection demands. This paper first discusses these challenges of federated fine-tuning LLMs, and introduces our package FS-LLM as a main contribution, which consists of the following components: (1) we build an end-to-end benchmarking pipeline, automizing the processes of dataset preprocessing, federated fine-tuning execution, and performance evaluation on federated LLM fine-tuning; (2) we provide comprehensive federated parameter-efficient fine-tuning algorithm implementations and versatile programming interfaces for future extension in FL scenarios with low communication and computation costs, even without accessing the full model; (3) we adopt several accelerating and resource-efficient operators for fine-tuning LLMs with limited resources and the flexible pluggable sub-routines for interdisciplinary study. We conduct extensive experiments to validate the effectiveness of FS-LLM and benchmark advanced LLMs with state-of-the-art parameter-efficient fine-tuning algorithms in FL settings, which also yields valuable insights into federated fine-tuning LLMs for the research community. To facilitate further research and adoption, we release FS-LLM at https://github.com/alibaba/FederatedScope/tree/llm.

---

## Warmth and competence in human-agent cooperation

**Authors:** Kevin R. McKee, Xuechunzi Bai, Susan T. Fiske

**Published:** 2022-01-31T18:57:08Z

**Categories:** cs.HC, cs.CY, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2201.13448v4) | [PDF](https://arxiv.org/pdf/2201.13448v4)

**Abstract:**
Interaction and cooperation with humans are overarching aspirations of artificial intelligence (AI) research. Recent studies demonstrate that AI agents trained with deep reinforcement learning are capable of collaborating with humans. These studies primarily evaluate human compatibility through "objective" metrics such as task performance, obscuring potential variation in the levels of trust and subjective preference that different agents garner. To better understand the factors shaping subjective preferences in human-agent cooperation, we train deep reinforcement learning agents in Coins, a two-player social dilemma. We recruit $N = 501$ participants for a human-agent cooperation study and measure their impressions of the agents they encounter. Participants' perceptions of warmth and competence predict their stated preferences for different agents, above and beyond objective performance metrics. Drawing inspiration from social science and biology research, we subsequently implement a new ``partner choice'' framework to elicit revealed preferences: after playing an episode with an agent, participants are asked whether they would like to play the next episode with the same agent or to play alone. As with stated preferences, social perception better predicts participants' revealed preferences than does objective performance. Given these results, we recommend human-agent interaction researchers routinely incorporate the measurement of social perception and subjective preferences into their studies.

---

## ELIS: Efficient LLM Iterative Scheduling System with Response Length Predictor

**Authors:** Seungbeom Choi, Jeonghoe Goo, Eunjoo Jeon, Mingyu Yang, Minsung Jang

**Published:** 2025-05-14T04:50:00Z

**Categories:** cs.DC, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2505.09142v1) | [PDF](https://arxiv.org/pdf/2505.09142v1)

**Abstract:**
We propose ELIS, a serving system for Large Language Models (LLMs) featuring an Iterative Shortest Remaining Time First (ISRTF) scheduler designed to efficiently manage inference tasks with the shortest remaining tokens. Current LLM serving systems often employ a first-come-first-served scheduling strategy, which can lead to the "head-of-line blocking" problem. To overcome this limitation, it is necessary to predict LLM inference times and apply a shortest job first scheduling strategy. However, due to the auto-regressive nature of LLMs, predicting the inference latency is challenging. ELIS addresses this challenge by training a response length predictor for LLMs using the BGE model, an encoder-based state-of-the-art model. Additionally, we have devised the ISRTF scheduling strategy, an optimization of shortest remaining time first tailored to existing LLM iteration batching. To evaluate our work in an industrial setting, we simulate streams of requests based on our study of real-world user LLM serving trace records. Furthermore, we implemented ELIS as a cloud-native scheduler system on Kubernetes to evaluate its performance in production environments. Our experimental results demonstrate that ISRTF reduces the average job completion time by up to 19.6%.

---

## Human-Centered LLM-Agent User Interface: A Position Paper

**Authors:** Daniel Chin, Yuxuan Wang, Gus Xia

**Published:** 2024-05-19T13:02:45Z

**Categories:** cs.HC, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2405.13050v2) | [PDF](https://arxiv.org/pdf/2405.13050v2)

**Abstract:**
Large Language Model (LLM) -in-the-loop applications have been shown to effectively interpret the human user's commands, make plans, and operate external tools/systems accordingly. Still, the operation scope of the LLM agent is limited to passively following the user, requiring the user to frame his/her needs with regard to the underlying tools/systems. We note that the potential of an LLM-Agent User Interface (LAUI) is much greater. A user mostly ignorant to the underlying tools/systems should be able to work with a LAUI to discover an emergent workflow. Contrary to the conventional way of designing an explorable GUI to teach the user a predefined set of ways to use the system, in the ideal LAUI, the LLM agent is initialized to be proficient with the system, proactively studies the user and his/her needs, and proposes new interaction schemes to the user. To illustrate LAUI, we present Flute X GPT, a concrete example using an LLM agent, a prompt manager, and a flute-tutoring multi-modal software-hardware system to facilitate the complex, real-time user experience of learning to play the flute.

---

## Table Meets LLM: Can Large Language Models Understand Structured Table Data? A Benchmark and Empirical Study

**Authors:** Yuan Sui, Mengyu Zhou, Mingjie Zhou, Shi Han, Dongmei Zhang

**Published:** 2023-05-22T14:23:46Z

**Categories:** cs.CL, cs.AI, cs.IR

**Links:** [Abstract](https://arxiv.org/abs/2305.13062v5) | [PDF](https://arxiv.org/pdf/2305.13062v5)

**Abstract:**
Large language models (LLMs) are becoming attractive as few-shot reasoners to solve Natural Language (NL)-related tasks. However, the understanding of their capability to process structured data like tables remains an under-explored area. While tables can be serialized as input for LLMs, there is a lack of comprehensive studies on whether LLMs genuinely comprehend this data. In this paper, we try to understand this by designing a benchmark to evaluate the structural understanding capabilities of LLMs through seven distinct tasks, e.g., cell lookup, row retrieval and size detection. Specially, we perform a series of evaluations on the recent most advanced LLM models, GPT-3.5 and GPT-4 and observe that performance varied with different input choices, including table input format, content order, role prompting, and partition marks. Drawing from the insights gained through the benchmark evaluations, we propose $\textit{self-augmentation}$ for effective structural prompting, such as critical value / range identification using internal knowledge of LLMs. When combined with carefully chosen input choices, these structural prompting methods lead to promising improvements in LLM performance on a variety of tabular tasks, e.g., TabFact($\uparrow2.31\%$), HybridQA($\uparrow2.13\%$), SQA($\uparrow2.72\%$), Feverous($\uparrow0.84\%$), and ToTTo($\uparrow5.68\%$). We believe that our open source benchmark and proposed prompting methods can serve as a simple yet generic selection for future research. The code and data of this paper will be temporality released at https://anonymous.4open.science/r/StructuredLLM-76F3/README.md and will be replaced with an official one at https://github.com/microsoft/TableProvider later.

---

## Beyond Binary: Towards Fine-Grained LLM-Generated Text Detection via Role Recognition and Involvement Measurement

**Authors:** Zihao Cheng, Li Zhou, Feng Jiang, Benyou Wang, Haizhou Li

**Published:** 2024-10-18T08:14:10Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2410.14259v2) | [PDF](https://arxiv.org/pdf/2410.14259v2)

**Abstract:**
The rapid development of large language models (LLMs), like ChatGPT, has resulted in the widespread presence of LLM-generated content on social media platforms, raising concerns about misinformation, data biases, and privacy violations, which can undermine trust in online discourse. While detecting LLM-generated content is crucial for mitigating these risks, current methods often focus on binary classification, failing to address the complexities of real-world scenarios like human-LLM collaboration. To move beyond binary classification and address these challenges, we propose a new paradigm for detecting LLM-generated content. This approach introduces two novel tasks: LLM Role Recognition (LLM-RR), a multi-class classification task that identifies specific roles of LLM in content generation, and LLM Influence Measurement (LLM-IM), a regression task that quantifies the extent of LLM involvement in content creation. To support these tasks, we propose LLMDetect, a benchmark designed to evaluate detectors' performance on these new tasks. LLMDetect includes the Hybrid News Detection Corpus (HNDC) for training detectors, as well as DetectEval, a comprehensive evaluation suite that considers five distinct cross-context variations and two multi-intensity variations within the same LLM role. This allows for a thorough assessment of detectors' generalization and robustness across diverse contexts. Our empirical validation of 10 baseline detection methods demonstrates that fine-tuned PLM-based models consistently outperform others on both tasks, while advanced LLMs face challenges in accurately detecting their own generated content. Our experimental results and analysis offer insights for developing more effective detection models for LLM-generated content. This research enhances the understanding of LLM-generated content and establishes a foundation for more nuanced detection methodologies.

---

## Adapting LLM Agents with Universal Feedback in Communication

**Authors:** Kuan Wang, Yadong Lu, Michael Santacroce, Yeyun Gong, Chao Zhang, Yelong Shen

**Published:** 2023-10-01T07:50:30Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2310.01444v3) | [PDF](https://arxiv.org/pdf/2310.01444v3)

**Abstract:**
Recent advances in large language models (LLMs) have demonstrated potential for LLM agents. To facilitate the training for these agents with both linguistic feedback and non-linguistic reward signals, we introduce Learning through Communication (LTC). We design a universal buffer to store all the feedback, and an iterative pipeline to enable an LLM agent to explore and update its policy in an given environment. To optimize agent interactions for task-specific learning with our universal buffer and pipeline, we introduce diverse communication patterns tailored for both single-agent and multi-agent environments. We evaluate the efficacy of our LTC approach on four diverse datasets: ALFWorld (single-agent), HotpotQA (multi-agent collaboration), Chameleon (multi-agent competition), and GSM8k (multi-agent teacher-student). On these data sets, LTC outperforms the supervised instruction fine-tuning baselines by 3.6% to 12%. These results highlight the versatility and efficiency of LTC in facilitating online adaptation for LLM agents.

---

## Taking Flight with Dialogue: Enabling Natural Language Control for PX4-based Drone Agent

**Authors:** Shoon Kit Lim, Melissa Jia Ying Chong, Jing Huey Khor, Ting Yang Ling

**Published:** 2025-06-09T07:37:45Z

**Categories:** cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2506.07509v1) | [PDF](https://arxiv.org/pdf/2506.07509v1)

**Abstract:**
Recent advances in agentic and physical artificial intelligence (AI) have largely focused on ground-based platforms such as humanoid and wheeled robots, leaving aerial robots relatively underexplored. Meanwhile, state-of-the-art unmanned aerial vehicle (UAV) multimodal vision-language systems typically rely on closed-source models accessible only to well-resourced organizations. To democratize natural language control of autonomous drones, we present an open-source agentic framework that integrates PX4-based flight control, Robot Operating System 2 (ROS 2) middleware, and locally hosted models using Ollama. We evaluate performance both in simulation and on a custom quadcopter platform, benchmarking four large language model (LLM) families for command generation and three vision-language model (VLM) families for scene understanding.

---

## Reasoning with Language Model is Planning with World Model

**Authors:** Shibo Hao, Yi Gu, Haodi Ma, Joshua Jiahua Hong, Zhen Wang, Daisy Zhe Wang, Zhiting Hu

**Published:** 2023-05-24T10:28:28Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2305.14992v2) | [PDF](https://arxiv.org/pdf/2305.14992v2)

**Abstract:**
Large language models (LLMs) have shown remarkable reasoning capabilities, especially when prompted to generate intermediate reasoning steps (e.g., Chain-of-Thought, CoT). However, LLMs can still struggle with problems that are easy for humans, such as generating action plans for executing tasks in a given environment, or performing complex math, logical, and commonsense reasoning. The deficiency stems from the key fact that LLMs lack an internal $\textit{world model}$ to predict the world $\textit{state}$ (e.g., environment status, intermediate variable values) and simulate long-term outcomes of actions. This prevents LLMs from performing deliberate planning akin to human brains, which involves exploring alternative reasoning paths, anticipating future states and rewards, and iteratively refining existing reasoning steps. To overcome the limitations, we propose a new LLM reasoning framework, $\underline{R}$easoning vi$\underline{a}$ $\underline{P}$lanning $\textbf{(RAP)}$. RAP repurposes the LLM as both a world model and a reasoning agent, and incorporates a principled planning algorithm (based on Monto Carlo Tree Search) for strategic exploration in the vast reasoning space. During reasoning, the LLM (as agent) incrementally builds a reasoning tree under the guidance of the LLM (as world model) and task-specific rewards, and obtains a high-reward reasoning path efficiently with a proper balance between exploration $\textit{vs.}$ exploitation. We apply RAP to a variety of challenging reasoning problems including plan generation, math reasoning, and logical inference. Empirical results on these tasks demonstrate the superiority of RAP over various strong baselines, including CoT and least-to-most prompting with self-consistency. RAP on LLAMA-33B surpasses CoT on GPT-4 with 33% relative improvement in a plan generation setting.

---

## When Agents Trade: Live Multi-Market Trading Benchmark for LLM Agents

**Authors:** Lingfei Qian, Xueqing Peng, Yan Wang, Vincent Jim Zhang, Huan He, Hanley Smith, Yi Han, Yueru He, Haohang Li, Yupeng Cao, Yangyang Yu, Alejandro Lopez-Lira, Peng Lu, Jian-Yun Nie, Guojun Xiong, Jimin Huang, Sophia Ananiadou

**Published:** 2025-10-13T17:54:09Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2510.11695v2) | [PDF](https://arxiv.org/pdf/2510.11695v2)

**Abstract:**
Although Large Language Model (LLM)-based agents are increasingly used in financial trading, it remains unclear whether they can reason and adapt in live markets, as most studies test models instead of agents, cover limited periods and assets, and rely on unverified data. To address these gaps, we introduce Agent Market Arena (AMA), the first lifelong, real-time benchmark for evaluating LLM-based trading agents across multiple markets. AMA integrates verified trading data, expert-checked news, and diverse agent architectures within a unified trading framework, enabling fair and continuous comparison under real conditions. It implements four agents, including InvestorAgent as a single-agent baseline, TradeAgent and HedgeFundAgent with different risk styles, and DeepFundAgent with memory-based reasoning, and evaluates them across GPT-4o, GPT-4.1, Claude-3.5-haiku, Claude-sonnet-4, and Gemini-2.0-flash. Live experiments on both cryptocurrency and stock markets demonstrate that agent frameworks display markedly distinct behavioral patterns, spanning from aggressive risk-taking to conservative decision-making, whereas model backbones contribute less to outcome variation. AMA thus establishes a foundation for rigorous, reproducible, and continuously evolving evaluation of financial reasoning and trading intelligence in LLM-based agents.

---

## Benchmarking Adversarial Robustness to Bias Elicitation in Large Language Models: Scalable Automated Assessment with LLM-as-a-Judge

**Authors:** Riccardo Cantini, Alessio Orsino, Massimo Ruggiero, Domenico Talia

**Published:** 2025-04-10T16:00:59Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2504.07887v2) | [PDF](https://arxiv.org/pdf/2504.07887v2)

**Abstract:**
The growing integration of Large Language Models (LLMs) into critical societal domains has raised concerns about embedded biases that can perpetuate stereotypes and undermine fairness. Such biases may stem from historical inequalities in training data, linguistic imbalances, or adversarial manipulation. Despite mitigation efforts, recent studies show that LLMs remain vulnerable to adversarial attacks that elicit biased outputs. This work proposes a scalable benchmarking framework to assess LLM robustness to adversarial bias elicitation. Our methodology involves: (i) systematically probing models across multiple tasks targeting diverse sociocultural biases, (ii) quantifying robustness through safety scores using an LLM-as-a-Judge approach, and (iii) employing jailbreak techniques to reveal safety vulnerabilities. To facilitate systematic benchmarking, we release a curated dataset of bias-related prompts, named CLEAR-Bias. Our analysis, identifying DeepSeek V3 as the most reliable judge LLM, reveals that bias resilience is uneven, with age, disability, and intersectional biases among the most prominent. Some small models outperform larger ones in safety, suggesting that training and architecture may matter more than scale. However, no model is fully robust to adversarial elicitation, with jailbreak attacks using low-resource languages or refusal suppression proving effective across model families. We also find that successive LLM generations exhibit slight safety gains, while models fine-tuned for the medical domain tend to be less safe than their general-purpose counterparts.

---

## AutoDroid: LLM-powered Task Automation in Android

**Authors:** Hao Wen, Yuanchun Li, Guohong Liu, Shanhui Zhao, Tao Yu, Toby Jia-Jun Li, Shiqi Jiang, Yunhao Liu, Yaqin Zhang, Yunxin Liu

**Published:** 2023-08-29T13:02:30Z

**Categories:** cs.AI, cs.SE

**Links:** [Abstract](https://arxiv.org/abs/2308.15272v4) | [PDF](https://arxiv.org/pdf/2308.15272v4)

**Abstract:**
Mobile task automation is an attractive technique that aims to enable voice-based hands-free user interaction with smartphones. However, existing approaches suffer from poor scalability due to the limited language understanding ability and the non-trivial manual efforts required from developers or end-users. The recent advance of large language models (LLMs) in language understanding and reasoning inspires us to rethink the problem from a model-centric perspective, where task preparation, comprehension, and execution are handled by a unified language model. In this work, we introduce AutoDroid, a mobile task automation system capable of handling arbitrary tasks on any Android application without manual efforts. The key insight is to combine the commonsense knowledge of LLMs and domain-specific knowledge of apps through automated dynamic analysis. The main components include a functionality-aware UI representation method that bridges the UI with the LLM, exploration-based memory injection techniques that augment the app-specific domain knowledge of LLM, and a multi-granularity query optimization module that reduces the cost of model inference. We integrate AutoDroid with off-the-shelf LLMs including online GPT-4/GPT-3.5 and on-device Vicuna, and evaluate its performance on a new benchmark for memory-augmented Android task automation with 158 common tasks. The results demonstrated that AutoDroid is able to precisely generate actions with an accuracy of 90.9%, and complete tasks with a success rate of 71.3%, outperforming the GPT-4-powered baselines by 36.4% and 39.7%. The demo, benchmark suites, and source code of AutoDroid will be released at url{https://autodroid-sys.github.io/}.

---

## ANX: Protocol-First Design for AI Agent Interaction with a Supporting 3EX Decoupled Architecture

**Authors:** Xu Mingze

**Published:** 2026-04-06T16:24:07Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2604.04820v1) | [PDF](https://arxiv.org/pdf/2604.04820v1)

**Abstract:**
AI agents, autonomous digital actors, need agent-native protocols; existing methods include GUI automation and MCP-based skills, with defects of high token consumption, fragmented interaction, inadequate security, due to lacking a unified top-level framework and key components, each independent module flawed. To address these issues, we present ANX, an open, extensible, verifiable agent-native protocol and top-level framework integrating CLI, Skill, MCP, resolving pain points via protocol innovation, architectural optimization and tool supplementation. Its four core innovations: 1) Agent-native design (ANX Config, Markup, CLI) with high information density, flexibility and strong adaptability to reduce tokens and eliminate inconsistencies; 2) Human-agent interaction combining Skill's flexibility for dual rendering as agent-executable instructions and human-readable UI; 3) MCP-supported on-demand lightweight apps without pre-registration; 4) ANX Markup-enabled machine-executable SOPs eliminating ambiguity for reliable long-horizon tasks and multi-agent collaboration. As the first in a series, we focus on ANX's design, present its 3EX decoupled architecture with ANXHub and preliminary feasibility analysis and experimental validation. ANX ensures native security: LLM-bypassed UI-to-Core communication keeps sensitive data out of agent context; human-only confirmation prevents automated misuse. Form-filling experiments with Qwen3.5-plus/GPT-4o show ANX reduces tokens by 47.3% (Qwen3.5-plus) and 55.6% (GPT-4o) vs MCP-based skills, 57.1% (Qwen3.5-plus) and 66.3% (GPT-4o) vs GUI automation, and shortens execution time by 58.1% and 57.7% vs MCP-based skills.

---

## MAEBE: Multi-Agent Emergent Behavior Framework

**Authors:** Sinem Erisken, Timothy Gothard, Martin Leitgab, Ram Potham

**Published:** 2025-06-03T16:33:47Z

**Categories:** cs.MA, cs.AI, cs.CL, cs.CY, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2506.03053v2) | [PDF](https://arxiv.org/pdf/2506.03053v2)

**Abstract:**
Traditional AI safety evaluations on isolated LLMs are insufficient as multi-agent AI ensembles become prevalent, introducing novel emergent risks. This paper introduces the Multi-Agent Emergent Behavior Evaluation (MAEBE) framework to systematically assess such risks. Using MAEBE with the Greatest Good Benchmark (and a novel double-inversion question technique), we demonstrate that: (1) LLM moral preferences, particularly for Instrumental Harm, are surprisingly brittle and shift significantly with question framing, both in single agents and ensembles. (2) The moral reasoning of LLM ensembles is not directly predictable from isolated agent behavior due to emergent group dynamics. (3) Specifically, ensembles exhibit phenomena like peer pressure influencing convergence, even when guided by a supervisor, highlighting distinct safety and alignment challenges. Our findings underscore the necessity of evaluating AI systems in their interactive, multi-agent contexts.

---

## Taiwan LLM: Bridging the Linguistic Divide with a Culturally Aligned Language Model

**Authors:** Yen-Ting Lin, Yun-Nung Chen

**Published:** 2023-11-29T09:48:34Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2311.17487v1) | [PDF](https://arxiv.org/pdf/2311.17487v1)

**Abstract:**
In the realm of language models, the nuanced linguistic and cultural intricacies of Traditional Chinese, as spoken in Taiwan, have been largely overlooked. This paper introduces Taiwan LLM, a pioneering Large Language Model that specifically caters to the Traditional Chinese language, with a focus on the variant used in Taiwan. Leveraging a comprehensive pretraining corpus and instruction-finetuning datasets, we have developed a model that not only understands the complexities of Traditional Chinese but also embodies the cultural context of Taiwan. Taiwan LLM represents the first of its kind, a model that is not only linguistically accurate but also culturally resonant with its user base. Our evaluations demonstrate that Taiwan LLM achieves superior performance in understanding and generating Traditional Chinese text, outperforming existing models that are predominantly trained on Simplified Chinese or English. The open-source release of Taiwan LLM invites collaboration and further innovation, ensuring that the linguistic diversity of Chinese speakers is embraced and well-served. The model, datasets, and further resources are made publicly available to foster ongoing research and development in this field.

---

## Self-Evaluating LLMs for Multi-Step Tasks: Stepwise Confidence Estimation for Failure Detection

**Authors:** Vaibhav Mavi, Shubh Jaroria, Weiqi Sun

**Published:** 2025-11-10T18:19:51Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2511.07364v1) | [PDF](https://arxiv.org/pdf/2511.07364v1)

**Abstract:**
Reliability and failure detection of large language models (LLMs) is critical for their deployment in high-stakes, multi-step reasoning tasks. Prior work explores confidence estimation for self-evaluating LLM-scorer systems, with confidence scorers estimating the likelihood of errors in LLM responses. However, most methods focus on single-step outputs and overlook the challenges of multi-step reasoning. In this work, we extend self-evaluation techniques to multi-step tasks, testing two intuitive approaches: holistic scoring and step-by-step scoring. Using two multi-step benchmark datasets, we show that stepwise evaluation generally outperforms holistic scoring in detecting potential errors, with up to 15% relative increase in AUC-ROC. Our findings demonstrate that self-evaluating LLM systems provide meaningful confidence estimates in complex reasoning, improving their trustworthiness and providing a practical framework for failure detection.

---

## LLM Agents for Education: Advances and Applications

**Authors:** Zhendong Chu, Shen Wang, Jian Xie, Tinghui Zhu, Yibo Yan, Jinheng Ye, Aoxiao Zhong, Xuming Hu, Jing Liang, Philip S. Yu, Qingsong Wen

**Published:** 2025-03-14T11:53:44Z

**Categories:** cs.CY, cs.AI, cs.CL, cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2503.11733v2) | [PDF](https://arxiv.org/pdf/2503.11733v2)

**Abstract:**
Large Language Model (LLM) agents are transforming education by automating complex pedagogical tasks and enhancing both teaching and learning processes. In this survey, we present a systematic review of recent advances in applying LLM agents to address key challenges in educational settings, such as feedback comment generation, curriculum design, etc. We analyze the technologies enabling these agents, including representative datasets, benchmarks, and algorithmic frameworks. Additionally, we highlight key challenges in deploying LLM agents in educational settings, including ethical issues, hallucination and overreliance, and integration with existing educational ecosystems. Beyond the core technical focus, we include in Appendix A a comprehensive overview of domain-specific educational agents, covering areas such as science learning, language learning, and professional development.

---

## Opponent Shaping in LLM Agents

**Authors:** Marta Emili Garcia Segura, Stephen Hailes, Mirco Musolesi

**Published:** 2025-10-09T14:13:24Z

**Categories:** cs.LG, cs.AI, cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2510.08255v1) | [PDF](https://arxiv.org/pdf/2510.08255v1)

**Abstract:**
Large Language Models (LLMs) are increasingly being deployed as autonomous agents in real-world environments. As these deployments scale, multi-agent interactions become inevitable, making it essential to understand strategic behavior in such systems. A central open question is whether LLM agents, like reinforcement learning agents, can shape the learning dynamics and influence the behavior of others through interaction alone. In this paper, we present the first investigation of opponent shaping (OS) with LLM-based agents. Existing OS algorithms cannot be directly applied to LLMs, as they require higher-order derivatives, face scalability constraints, or depend on architectural components that are absent in transformers. To address this gap, we introduce ShapeLLM, an adaptation of model-free OS methods tailored for transformer-based agents. Using ShapeLLM, we examine whether LLM agents can influence co-players' learning dynamics across diverse game-theoretic environments. We demonstrate that LLM agents can successfully guide opponents toward exploitable equilibria in competitive games (Iterated Prisoner's Dilemma, Matching Pennies, and Chicken) and promote coordination and improve collective welfare in cooperative games (Iterated Stag Hunt and a cooperative version of the Prisoner's Dilemma). Our findings show that LLM agents can both shape and be shaped through interaction, establishing opponent shaping as a key dimension of multi-agent LLM research.

---

## BadAgent: Inserting and Activating Backdoor Attacks in LLM Agents

**Authors:** Yifei Wang, Dizhan Xue, Shengjie Zhang, Shengsheng Qian

**Published:** 2024-06-05T07:14:28Z

**Categories:** cs.CL, cs.AI, cs.CR, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2406.03007v1) | [PDF](https://arxiv.org/pdf/2406.03007v1)

**Abstract:**
With the prosperity of large language models (LLMs), powerful LLM-based intelligent agents have been developed to provide customized services with a set of user-defined tools. State-of-the-art methods for constructing LLM agents adopt trained LLMs and further fine-tune them on data for the agent task. However, we show that such methods are vulnerable to our proposed backdoor attacks named BadAgent on various agent tasks, where a backdoor can be embedded by fine-tuning on the backdoor data. At test time, the attacker can manipulate the deployed LLM agents to execute harmful operations by showing the trigger in the agent input or environment. To our surprise, our proposed attack methods are extremely robust even after fine-tuning on trustworthy data. Though backdoor attacks have been studied extensively in natural language processing, to the best of our knowledge, we could be the first to study them on LLM agents that are more dangerous due to the permission to use external tools. Our work demonstrates the clear risk of constructing LLM agents based on untrusted LLMs or data. Our code is public at https://github.com/DPamK/BadAgent

---

## LLM-MARS: Large Language Model for Behavior Tree Generation and NLP-enhanced Dialogue in Multi-Agent Robot Systems

**Authors:** Artem Lykov, Maria Dronova, Nikolay Naglov, Mikhail Litvinov, Sergei Satsevich, Artem Bazhenov, Vladimir Berman, Aleksei Shcherbak, Dzmitry Tsetserukou

**Published:** 2023-12-14T21:18:34Z

**Categories:** cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2312.09348v1) | [PDF](https://arxiv.org/pdf/2312.09348v1)

**Abstract:**
This paper introduces LLM-MARS, first technology that utilizes a Large Language Model based Artificial Intelligence for Multi-Agent Robot Systems. LLM-MARS enables dynamic dialogues between humans and robots, allowing the latter to generate behavior based on operator commands and provide informative answers to questions about their actions. LLM-MARS is built on a transformer-based Large Language Model, fine-tuned from the Falcon 7B model. We employ a multimodal approach using LoRa adapters for different tasks. The first LoRa adapter was developed by fine-tuning the base model on examples of Behavior Trees and their corresponding commands. The second LoRa adapter was developed by fine-tuning on question-answering examples. Practical trials on a multi-agent system of two robots within the Eurobot 2023 game rules demonstrate promising results. The robots achieve an average task execution accuracy of 79.28% in compound commands. With commands containing up to two tasks accuracy exceeded 90%. Evaluation confirms the system's answers on operators questions exhibit high accuracy, relevance, and informativeness. LLM-MARS and similar multi-agent robotic systems hold significant potential to revolutionize logistics, enabling autonomous exploration missions and advancing Industry 5.0.

---

## Bridging Speech and Text: Enhancing ASR with Pinyin-to-Character Pre-training in LLMs

**Authors:** Yang Yuhang, Peng Yizhou, Eng Siong Chng, Xionghu Zhong

**Published:** 2024-09-24T12:06:31Z

**Categories:** cs.CL, cs.SD, eess.AS

**Links:** [Abstract](https://arxiv.org/abs/2409.16005v1) | [PDF](https://arxiv.org/pdf/2409.16005v1)

**Abstract:**
The integration of large language models (LLMs) with pre-trained speech models has opened up new avenues in automatic speech recognition (ASR). While LLMs excel in multimodal understanding tasks, effectively leveraging their capabilities for ASR remains a significant challenge. This paper presents a novel training approach to enhance LLM performance in ASR tasks. We propose pre-training LLMs on Pinyin embedding sequences, which represent pronunciation features, to generate corresponding Chinese characters. This step enables the LLM to adapt to generating text from pronunciation features before encountering real speech data. Furthermore, we fine-tune the LoRA parameters to enhance the LLM's understanding of speech modality information. In AISHELL-1 corpus, our approach yields a 9.5% relative improvement in ASR tasks compared to the baseline without Pinyi-to-Character pre-training. Additionally, incorporating auxiliary text data for Pinyi-to-Character pre-training further boosts performance, achieving a 19.0% relative improvement.

---

## Breaking Agents: Compromising Autonomous LLM Agents Through Malfunction Amplification

**Authors:** Boyang Zhang, Yicong Tan, Yun Shen, Ahmed Salem, Michael Backes, Savvas Zannettou, Yang Zhang

**Published:** 2024-07-30T14:35:31Z

**Categories:** cs.CR, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2407.20859v1) | [PDF](https://arxiv.org/pdf/2407.20859v1)

**Abstract:**
Recently, autonomous agents built on large language models (LLMs) have experienced significant development and are being deployed in real-world applications. These agents can extend the base LLM's capabilities in multiple ways. For example, a well-built agent using GPT-3.5-Turbo as its core can outperform the more advanced GPT-4 model by leveraging external components. More importantly, the usage of tools enables these systems to perform actions in the real world, moving from merely generating text to actively interacting with their environment. Given the agents' practical applications and their ability to execute consequential actions, it is crucial to assess potential vulnerabilities. Such autonomous systems can cause more severe damage than a standalone language model if compromised. While some existing research has explored harmful actions by LLM agents, our study approaches the vulnerability from a different perspective. We introduce a new type of attack that causes malfunctions by misleading the agent into executing repetitive or irrelevant actions. We conduct comprehensive evaluations using various attack methods, surfaces, and properties to pinpoint areas of susceptibility. Our experiments reveal that these attacks can induce failure rates exceeding 80\% in multiple scenarios. Through attacks on implemented and deployable agents in multi-agent scenarios, we accentuate the realistic risks associated with these vulnerabilities. To mitigate such attacks, we propose self-examination detection methods. However, our findings indicate these attacks are difficult to detect effectively using LLMs alone, highlighting the substantial risks associated with this vulnerability.

---

## Self-Adaptive Large Language Model (LLM)-Based Multiagent Systems

**Authors:** Nathalia Nascimento, Paulo Alencar, Donald Cowan

**Published:** 2023-07-12T14:26:46Z

**Categories:** cs.MA, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2307.06187v1) | [PDF](https://arxiv.org/pdf/2307.06187v1)

**Abstract:**
In autonomic computing, self-adaptation has been proposed as a fundamental paradigm to manage the complexity of multiagent systems (MASs). This achieved by extending a system with support to monitor and adapt itself to achieve specific concerns of interest. Communication in these systems is key given that in scenarios involving agent interaction, it enhances cooperation and reduces coordination challenges by enabling direct, clear information exchange. However, improving the expressiveness of the interaction communication with MASs is not without challenges. In this sense, the interplay between self-adaptive systems and effective communication is crucial for future MAS advancements. In this paper, we propose the integration of large language models (LLMs) such as GPT-based technologies into multiagent systems. We anchor our methodology on the MAPE-K model, which is renowned for its robust support in monitoring, analyzing, planning, and executing system adaptations in response to dynamic environments. We also present a practical illustration of the proposed approach, in which we implement and assess a basic MAS-based application. The approach significantly advances the state-of-the-art of self-adaptive systems by proposing a new paradigm for MAS self-adaptation of autonomous systems based on LLM capabilities.

---

## Exploring Design of Multi-Agent LLM Dialogues for Research Ideation

**Authors:** Keisuke Ueda, Wataru Hirota, Takuto Asakura, Takahiro Omi, Kosuke Takahashi, Kosuke Arima, Tatsuya Ishigaki

**Published:** 2025-07-11T06:53:46Z

**Categories:** cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2507.08350v1) | [PDF](https://arxiv.org/pdf/2507.08350v1)

**Abstract:**
Large language models (LLMs) are increasingly used to support creative tasks such as research idea generation. While recent work has shown that structured dialogues between LLMs can improve the novelty and feasibility of generated ideas, the optimal design of such interactions remains unclear. In this study, we conduct a comprehensive analysis of multi-agent LLM dialogues for scientific ideation. We compare different configurations of agent roles, number of agents, and dialogue depth to understand how these factors influence the novelty and feasibility of generated ideas. Our experimental setup includes settings where one agent generates ideas and another critiques them, enabling iterative improvement. Our results show that enlarging the agent cohort, deepening the interaction depth, and broadening agent persona heterogeneity each enrich the diversity of generated ideas. Moreover, specifically increasing critic-side diversity within the ideation-critique-revision loop further boosts the feasibility of the final proposals. Our findings offer practical guidelines for building effective multi-agent LLM systems for scientific ideation. Our code is available at https://github.com/g6000/MultiAgent-Research-Ideator.

---

## RepairAgent: An Autonomous, LLM-Based Agent for Program Repair

**Authors:** Islem Bouzenia, Premkumar Devanbu, Michael Pradel

**Published:** 2024-03-25T19:17:43Z

**Categories:** cs.SE, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2403.17134v2) | [PDF](https://arxiv.org/pdf/2403.17134v2)

**Abstract:**
Automated program repair has emerged as a powerful technique to mitigate the impact of software bugs on system reliability and user experience. This paper introduces RepairAgent, the first work to address the program repair challenge through an autonomous agent based on a large language model (LLM). Unlike existing deep learning-based approaches, which prompt a model with a fixed prompt or in a fixed feedback loop, our work treats the LLM as an agent capable of autonomously planning and executing actions to fix bugs by invoking suitable tools. RepairAgent freely interleaves gathering information about the bug, gathering repair ingredients, and validating fixes, while deciding which tools to invoke based on the gathered information and feedback from previous fix attempts. Key contributions that enable RepairAgent include a set of tools that are useful for program repair, a dynamically updated prompt format that allows the LLM to interact with these tools, and a finite state machine that guides the agent in invoking the tools. Our evaluation on the popular Defects4J dataset demonstrates RepairAgent's effectiveness in autonomously repairing 164 bugs, including 39 bugs not fixed by prior techniques. Interacting with the LLM imposes an average cost of 270,000 tokens per bug, which, under the current pricing of OpenAI's GPT-3.5 model, translates to 14 cents of USD per bug. To the best of our knowledge, this work is the first to present an autonomous, LLM-based agent for program repair, paving the way for future agent-based techniques in software engineering.

---

## Building LLM Agents by Incorporating Insights from Computer Systems

**Authors:** Yapeng Mi, Zhi Gao, Xiaojian Ma, Qing Li

**Published:** 2025-04-06T13:38:37Z

**Categories:** cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2504.04485v1) | [PDF](https://arxiv.org/pdf/2504.04485v1)

**Abstract:**
LLM-driven autonomous agents have emerged as a promising direction in recent years. However, many of these LLM agents are designed empirically or based on intuition, often lacking systematic design principles, which results in diverse agent structures with limited generality and scalability. In this paper, we advocate for building LLM agents by incorporating insights from computer systems. Inspired by the von Neumann architecture, we propose a structured framework for LLM agentic systems, emphasizing modular design and universal principles. Specifically, this paper first provides a comprehensive review of LLM agents from the computer system perspective, then identifies key challenges and future directions inspired by computer system design, and finally explores the learning mechanisms for LLM agents beyond the computer system. The insights gained from this comparative analysis offer a foundation for systematic LLM agent design and advancement.

---

## ExpeL: LLM Agents Are Experiential Learners

**Authors:** Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, Gao Huang

**Published:** 2023-08-20T03:03:34Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2308.10144v3) | [PDF](https://arxiv.org/pdf/2308.10144v3)

**Abstract:**
The recent surge in research interest in applying large language models (LLMs) to decision-making tasks has flourished by leveraging the extensive world knowledge embedded in LLMs. While there is a growing demand to tailor LLMs for custom decision-making tasks, finetuning them for specific tasks is resource-intensive and may diminish the model's generalization capabilities. Moreover, state-of-the-art language models like GPT-4 and Claude are primarily accessible through API calls, with their parametric weights remaining proprietary and unavailable to the public. This scenario emphasizes the growing need for new methodologies that allow learning from agent experiences without requiring parametric updates. To address these problems, we introduce the Experiential Learning (ExpeL) agent. Our agent autonomously gathers experiences and extracts knowledge using natural language from a collection of training tasks. At inference, the agent recalls its extracted insights and past experiences to make informed decisions. Our empirical results highlight the robust learning efficacy of the ExpeL agent, indicating a consistent enhancement in its performance as it accumulates experiences. We further explore the emerging capabilities and transfer learning potential of the ExpeL agent through qualitative observations and additional experiments.

---

## Executable Code Actions Elicit Better LLM Agents

**Authors:** Xingyao Wang, Yangyi Chen, Lifan Yuan, Yizhe Zhang, Yunzhu Li, Hao Peng, Heng Ji

**Published:** 2024-02-01T21:38:58Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2402.01030v4) | [PDF](https://arxiv.org/pdf/2402.01030v4)

**Abstract:**
Large Language Model (LLM) agents, capable of performing a broad range of actions, such as invoking tools and controlling robots, show great potential in tackling real-world challenges. LLM agents are typically prompted to produce actions by generating JSON or text in a pre-defined format, which is usually limited by constrained action space (e.g., the scope of pre-defined tools) and restricted flexibility (e.g., inability to compose multiple tools). This work proposes to use executable Python code to consolidate LLM agents' actions into a unified action space (CodeAct). Integrated with a Python interpreter, CodeAct can execute code actions and dynamically revise prior actions or emit new actions upon new observations through multi-turn interactions. Our extensive analysis of 17 LLMs on API-Bank and a newly curated benchmark shows that CodeAct outperforms widely used alternatives (up to 20% higher success rate). The encouraging performance of CodeAct motivates us to build an open-source LLM agent that interacts with environments by executing interpretable code and collaborates with users using natural language. To this end, we collect an instruction-tuning dataset CodeActInstruct that consists of 7k multi-turn interactions using CodeAct. We show that it can be used with existing data to improve models in agent-oriented tasks without compromising their general capability. CodeActAgent, finetuned from Llama2 and Mistral, is integrated with Python interpreter and uniquely tailored to perform sophisticated tasks (e.g., model training) using existing libraries and autonomously self-debug.

---

## Agent-as-a-Judge: Evaluate Agents with Agents

**Authors:** Mingchen Zhuge, Changsheng Zhao, Dylan Ashley, Wenyi Wang, Dmitrii Khizbullin, Yunyang Xiong, Zechun Liu, Ernie Chang, Raghuraman Krishnamoorthi, Yuandong Tian, Yangyang Shi, Vikas Chandra, Jürgen Schmidhuber

**Published:** 2024-10-14T17:57:02Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2410.10934v2) | [PDF](https://arxiv.org/pdf/2410.10934v2)

**Abstract:**
Contemporary evaluation techniques are inadequate for agentic systems. These approaches either focus exclusively on final outcomes -- ignoring the step-by-step nature of agentic systems, or require excessive manual labour. To address this, we introduce the Agent-as-a-Judge framework, wherein agentic systems are used to evaluate agentic systems. This is an organic extension of the LLM-as-a-Judge framework, incorporating agentic features that enable intermediate feedback for the entire task-solving process. We apply the Agent-as-a-Judge to the task of code generation. To overcome issues with existing benchmarks and provide a proof-of-concept testbed for Agent-as-a-Judge, we present DevAI, a new benchmark of 55 realistic automated AI development tasks. It includes rich manual annotations, like a total of 365 hierarchical user requirements. We benchmark three of the popular agentic systems using Agent-as-a-Judge and find it dramatically outperforms LLM-as-a-Judge and is as reliable as our human evaluation baseline. Altogether, we believe that Agent-as-a-Judge marks a concrete step forward for modern agentic systems -- by providing rich and reliable reward signals necessary for dynamic and scalable self-improvement.

---

## LLM Enhancer: Merged Approach using Vector Embedding for Reducing Large Language Model Hallucinations with External Knowledge

**Authors:** Naheed Rayhan, Md. Ashrafuzzaman

**Published:** 2025-04-29T19:27:04Z

**Categories:** cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2504.21132v1) | [PDF](https://arxiv.org/pdf/2504.21132v1)

**Abstract:**
Large Language Models (LLMs), such as ChatGPT, have demonstrated the capability to generate human like, natural responses across a range of tasks, including task oriented dialogue and question answering. However, their application in real world, critical scenarios is often hindered by a tendency to produce inaccurate information and a limited ability to leverage external knowledge sources. This paper introduces the LLM ENHANCER system, designed to integrate multiple online sources such as Google, Wikipedia, and DuckDuckGo to enhance data accuracy. The LLMs employed within this system are open source. The data acquisition process for the LLM ENHANCER system operates in parallel, utilizing custom agent tools to manage the flow of information. Vector embeddings are used to identify the most pertinent information, which is subsequently supplied to the LLM for user interaction. The LLM ENHANCER system mitigates hallucinations in chat based LLMs while preserving response naturalness and accuracy.

---

## AIOS: LLM Agent Operating System

**Authors:** Kai Mei, Xi Zhu, Wujiang Xu, Wenyue Hua, Mingyu Jin, Zelong Li, Shuyuan Xu, Ruosong Ye, Yingqiang Ge, Yongfeng Zhang

**Published:** 2024-03-25T17:32:23Z

**Categories:** cs.OS, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2403.16971v5) | [PDF](https://arxiv.org/pdf/2403.16971v5)

**Abstract:**
LLM-based intelligent agents face significant deployment challenges, particularly related to resource management. Allowing unrestricted access to LLM or tool resources can lead to inefficient or even potentially harmful resource allocation and utilization for agents. Furthermore, the absence of proper scheduling and resource management mechanisms in current agent designs hinders concurrent processing and limits overall system efficiency. To address these challenges, this paper proposes the architecture of AIOS (LLM-based AI Agent Operating System) under the context of managing LLM-based agents. It introduces a novel architecture for serving LLM-based agents by isolating resources and LLM-specific services from agent applications into an AIOS kernel. This AIOS kernel provides fundamental services (e.g., scheduling, context management, memory management, storage management, access control) for runtime agents. To enhance usability, AIOS also includes an AIOS SDK, a comprehensive suite of APIs designed for utilizing functionalities provided by the AIOS kernel. Experimental results demonstrate that using AIOS can achieve up to 2.1x faster execution for serving agents built by various agent frameworks. The source code is available at https://github.com/agiresearch/AIOS.

---

## Formal-LLM: Integrating Formal Language and Natural Language for Controllable LLM-based Agents

**Authors:** Zelong Li, Wenyue Hua, Hao Wang, He Zhu, Yongfeng Zhang

**Published:** 2024-02-01T17:30:50Z

**Categories:** cs.LG, cs.AI, cs.CL, cs.FL

**Links:** [Abstract](https://arxiv.org/abs/2402.00798v4) | [PDF](https://arxiv.org/pdf/2402.00798v4)

**Abstract:**
Recent advancements on Large Language Models (LLMs) enable AI Agents to automatically generate and execute multi-step plans to solve complex tasks. However, since LLM's content generation process is hardly controllable, current LLM-based agents frequently generate invalid or non-executable plans, which jeopardizes the performance of the generated plans and corrupts users' trust in LLM-based agents. In response, this paper proposes a novel "Formal-LLM" framework for LLM-based agents by integrating the expressiveness of natural language and the precision of formal language. Specifically, the framework allows agent developers to express their requirements or constraints for the planning process as an automaton. A stack-based LLM plan generation process is then conducted under the supervision of the automaton to ensure that the generated plan satisfies the constraints, making the planning process controllable. We conduct experiments on both benchmark tasks and practical real-life tasks, and our framework achieves over 50% overall performance increase, which validates the feasibility and effectiveness of employing Formal-LLM to guide the plan generation of agents, preventing the agents from generating invalid and unsuccessful plans. Further, more controllable LLM-based agents can facilitate the broader utilization of LLM in application scenarios where high validity of planning is essential. The source code of this work is available at https://github.com/agiresearch/Formal-LLM.

---

## LLM Agents Should Employ Security Principles

**Authors:** Kaiyuan Zhang, Zian Su, Pin-Yu Chen, Elisa Bertino, Xiangyu Zhang, Ninghui Li

**Published:** 2025-05-29T21:39:08Z

**Categories:** cs.CR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2505.24019v1) | [PDF](https://arxiv.org/pdf/2505.24019v1)

**Abstract:**
Large Language Model (LLM) agents show considerable promise for automating complex tasks using contextual reasoning; however, interactions involving multiple agents and the system's susceptibility to prompt injection and other forms of context manipulation introduce new vulnerabilities related to privacy leakage and system exploitation. This position paper argues that the well-established design principles in information security, which are commonly referred to as security principles, should be employed when deploying LLM agents at scale. Design principles such as defense-in-depth, least privilege, complete mediation, and psychological acceptability have helped guide the design of mechanisms for securing information systems over the last five decades, and we argue that their explicit and conscientious adoption will help secure agentic systems. To illustrate this approach, we introduce AgentSandbox, a conceptual framework embedding these security principles to provide safeguards throughout an agent's life-cycle. We evaluate with state-of-the-art LLMs along three dimensions: benign utility, attack utility, and attack success rate. AgentSandbox maintains high utility for its intended functions under both benign and adversarial evaluations while substantially mitigating privacy risks. By embedding secure design principles as foundational elements within emerging LLM agent protocols, we aim to promote trustworthy agent ecosystems aligned with user privacy expectations and evolving regulatory requirements.

---

## Experimental Investigation of Trust in Anthropomorphic Agents as Task Partners

**Authors:** Akihiro Maehigashi, Takahiro Tsumura, Seiji Yamada

**Published:** 2022-02-02T15:04:51Z

**Categories:** cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2202.01077v2) | [PDF](https://arxiv.org/pdf/2202.01077v2)

**Abstract:**
This study investigated whether human trust in a social robot with anthropomorphic physicality is similar to that in an AI agent or in a human in order to clarify how anthropomorphic physicality influences human trust in an agent. We conducted an online experiment using two types of cognitive tasks, calculation and emotion recognition tasks, where participants answered after referring to the answers of an AI agent, a human, or a social robot. During the experiment, the participants rated their trust levels in their partners. As a result, trust in the social robot was basically neither similar to that in the AI agent nor in the human and instead settled between them. The results showed a possibility that manipulating anthropomorphic features would help assist human users in appropriately calibrating trust in an agent.

---

## Language-Model Prior Overcomes Cold-Start Items

**Authors:** Shiyu Wang, Hao Ding, Yupeng Gu, Sergul Aydore, Kousha Kalantari, Branislav Kveton

**Published:** 2024-11-13T22:45:52Z

**Categories:** cs.IR, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2411.09065v1) | [PDF](https://arxiv.org/pdf/2411.09065v1)

**Abstract:**
The growth of recommender systems (RecSys) is driven by digitization and the need for personalized content in areas such as e-commerce and video streaming. The content in these systems often changes rapidly and therefore they constantly face the ongoing cold-start problem, where new items lack interaction data and are hard to value. Existing solutions for the cold-start problem, such as content-based recommenders and hybrid methods, leverage item metadata to determine item similarities. The main challenge with these methods is their reliance on structured and informative metadata to capture detailed item similarities, which may not always be available. This paper introduces a novel approach for cold-start item recommendation that utilizes the language model (LM) to estimate item similarities, which are further integrated as a Bayesian prior with classic recommender systems. This approach is generic and able to boost the performance of various recommenders. Specifically, our experiments integrate it with both sequential and collaborative filtering-based recommender and evaluate it on two real-world datasets, demonstrating the enhanced performance of the proposed approach.

---

## Reimagining Agent-based Modeling with Large Language Model Agents via Shachi

**Authors:** So Kuroki, Yingtao Tian, Kou Misaki, Takashi Ikegami, Takuya Akiba, Yujin Tang

**Published:** 2025-09-26T04:38:59Z

**Categories:** cs.AI, cs.MA, cs.SI, econ.GN

**Links:** [Abstract](https://arxiv.org/abs/2509.21862v2) | [PDF](https://arxiv.org/pdf/2509.21862v2)

**Abstract:**
The study of emergent behaviors in large language model (LLM)-driven multi-agent systems is a critical research challenge, yet progress is limited by a lack of principled methodologies for controlled experimentation. To address this, we introduce Shachi, a formal methodology and modular framework that decomposes an agent's policy into core cognitive components: Configuration for intrinsic traits, Memory for contextual persistence, and Tools for expanded capabilities, all orchestrated by an LLM reasoning engine. This principled architecture moves beyond brittle, ad-hoc agent designs and enables the systematic analysis of how specific architectural choices influence collective behavior. We validate our methodology on a comprehensive 10-task benchmark and demonstrate its power through novel scientific inquiries. Critically, we establish the external validity of our approach by modeling a real-world U.S. tariff shock, showing that agent behaviors align with observed market reactions only when their cognitive architecture is appropriately configured with memory and tools. Our work provides a rigorous, open-source foundation for building and evaluating LLM agents, aimed at fostering more cumulative and scientifically grounded research.

---

## VeriLA: A Human-Centered Evaluation Framework for Interpretable Verification of LLM Agent Failures

**Authors:** Yoo Yeon Sung, Hannah Kim, Dan Zhang

**Published:** 2025-03-16T21:11:18Z

**Categories:** cs.AI, cs.CL, cs.HC

**Links:** [Abstract](https://arxiv.org/abs/2503.12651v1) | [PDF](https://arxiv.org/pdf/2503.12651v1)

**Abstract:**
AI practitioners increasingly use large language model (LLM) agents in compound AI systems to solve complex reasoning tasks, these agent executions often fail to meet human standards, leading to errors that compromise the system's overall performance. Addressing these failures through human intervention is challenging due to the agents' opaque reasoning processes, misalignment with human expectations, the complexity of agent dependencies, and the high cost of manual inspection. This paper thus introduces a human-centered evaluation framework for Verifying LLM Agent failures (VeriLA), which systematically assesses agent failures to reduce human effort and make these agent failures interpretable to humans. The framework first defines clear expectations of each agent by curating human-designed agent criteria. Then, it develops a human-aligned agent verifier module, trained with human gold standards, to assess each agent's execution output. This approach enables granular evaluation of each agent's performance by revealing failures from a human standard, offering clear guidelines for revision, and reducing human cognitive load. Our case study results show that VeriLA is both interpretable and efficient in helping practitioners interact more effectively with the system. By upholding accountability in human-agent collaboration, VeriLA paves the way for more trustworthy and human-aligned compound AI systems.

---

## Epistemic Blinding: An Inference-Time Protocol for Auditing Prior Contamination in LLM-Assisted Analysis

**Authors:** Michael Cuccarese

**Published:** 2026-04-07T16:06:52Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2604.06013v1) | [PDF](https://arxiv.org/pdf/2604.06013v1)

**Abstract:**
This paper presents epistemic blinding in the context of an agentic system that uses large language models to reason across multiple biological datasets for drug target prioritization. During development, it became apparent that LLM outputs silently blend data-driven inference with memorized priors about named entities - and the blend is invisible: there is no way to determine, from a single output, how much came from the data on the page and how much came from the model's training memory. Epistemic blinding is a simple inference-time protocol that replaces entity identifiers with anonymous codes before prompting, then compares outputs against an unblinded control. The protocol does not make LLM reasoning deterministic, but it restores one critical axis of auditability: measuring how much of an output came from the supplied data versus the model's parametric knowledge. The complete target identification system is described - including LLM-guided evolutionary optimization of scoring functions and blinded agentic reasoning for target rationalization - with demonstration that both stages operate without access to entity identity. In oncology drug target prioritization across four cancer types, blinding changes 16% of top-20 predictions while preserving identical recovery of validated targets. The contamination problem is shown to generalize beyond biology: in S&P 500 equity screening, brand-recognition bias reshapes 30-40% of top-20 rankings across five random seeds. To lower the barrier to adoption, the protocol is released as an open-source tool and as a Claude Code skill that enables one-command epistemic blinding within agentic workflows. The claim is not that blinded analysis produces better results, but that without blinding, there is no way to know to what degree the agent is adhering to the analytical process the researcher designed.

---

## "Stop replacing salt with sugar!'': Towards Intuitive Human-Agent Teaching

**Authors:** Nikolaos Kondylidis, Andrea Rafanelli, Ilaria Tiddi, Annette ten Teije, Frank van Harmelen

**Published:** 2025-09-29T12:00:53Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2509.24651v1) | [PDF](https://arxiv.org/pdf/2509.24651v1)

**Abstract:**
Humans quickly learn new concepts from a small number of examples. Replicating this capacity with Artificial Intelligence (AI) systems has proven to be challenging. When it comes to learning subjective tasks-where there is an evident scarcity of data-this capacity needs to be recreated. In this work, we propose an intuitive human-agent teaching architecture in which the human can teach an agent how to perform a task by providing demonstrations, i.e., examples. To have an intuitive interaction, we argue that the agent should be able to learn incrementally from a few single examples. To allow for this, our objective is to broaden the agent's task understanding using domain knowledge. Then, using a learning method to enable the agent to learn efficiently from a limited number of examples. Finally, to optimize how human can select the most representative and less redundant examples to provide the agent with. We apply our proposed method to the subjective task of ingredient substitution, where the agent needs to learn how to substitute ingredients in recipes based on human examples. We replicate human input using the Recipe1MSubs dataset. In our experiments, the agent achieves half its task performance after only 100 examples are provided, compared to the complete training set of 50k examples. We show that by providing examples in strategic order along with a learning method that leverages external symbolic knowledge, the agent can generalize more efficiently.

---

## SlimPajama-DC: Understanding Data Combinations for LLM Training

**Authors:** Zhiqiang Shen, Tianhua Tao, Liqun Ma, Willie Neiswanger, Zhengzhong Liu, Hongyi Wang, Bowen Tan, Joel Hestness, Natalia Vassilieva, Daria Soboleva, Eric Xing

**Published:** 2023-09-19T17:59:54Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2309.10818v3) | [PDF](https://arxiv.org/pdf/2309.10818v3)

**Abstract:**
This paper aims to understand the impacts of various data combinations (e.g., web text, Wikipedia, GitHub, books) on the pretraining of large language models using SlimPajama. SlimPajama is a rigorously deduplicated, multi-source dataset, which has been refined and further deduplicated to 627B tokens from the extensive 1.2T token RedPajama dataset contributed by Together. We have termed our research as SlimPajama-DC, an empirical analysis designed to uncover fundamental characteristics and best practices associated with employing SlimPajama in the training of large language models. During our research with SlimPajama, two pivotal observations emerged: (1) Global deduplication vs. local deduplication. We analyze and discuss how global (across different sources of datasets) and local (within the single source of dataset) deduplications affect the performance of trained models. (2) Proportions of highly-deduplicated multi-source datasets in the combination. To study this, we construct six configurations on SlimPajama dataset and train individual ones using 1.3B Cerebras-GPT model with Alibi and SwiGLU. Our best configuration outperforms the 1.3B model trained on RedPajama using the same number of training tokens by a significant margin. All our 1.3B models are trained on Cerebras 16$\times$ CS-2 cluster with a total of 80 PFLOP/s in bf16 mixed precision. We further extend our discoveries (such as increasing data diversity is crucial after global deduplication) on a 7B model with large batch-size training. Our SlimPajama-DC models are available at: https://huggingface.co/MBZUAI-LLM/SlimPajama-DC and the separate SlimPajama-DC datasets are available at: https://huggingface.co/datasets/MBZUAI-LLM/SlimPajama-627B-DC.

---

## From Biased Chatbots to Biased Agents: Examining Role Assignment Effects on LLM Agent Robustness

**Authors:** Linbo Cao, Lihao Sun, Yang Yue

**Published:** 2026-01-21T02:43:07Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2602.12285v1) | [PDF](https://arxiv.org/pdf/2602.12285v1)

**Abstract:**
Large Language Models (LLMs) are increasingly deployed as autonomous agents capable of actions with real-world impacts beyond text generation. While persona-induced biases in text generation are well documented, their effects on agent task performance remain largely unexplored, even though such effects pose more direct operational risks. In this work, we present the first systematic case study showing that demographic-based persona assignments can alter LLM agents' behavior and degrade performance across diverse domains. Evaluating widely deployed models on agentic benchmarks spanning strategic reasoning, planning, and technical operations, we uncover substantial performance variations - up to 26.2% degradation, driven by task-irrelevant persona cues. These shifts appear across task types and model architectures, indicating that persona conditioning and simple prompt injections can distort an agent's decision-making reliability. Our findings reveal an overlooked vulnerability in current LLM agentic systems: persona assignments can introduce implicit biases and increase behavioral volatility, raising concerns for the safe and robust deployment of LLM agents.

---

## HR-Agent: A Task-Oriented Dialogue (TOD) LLM Agent Tailored for HR Applications

**Authors:** Weijie Xu, Jay Desai, Fanyou Wu, Josef Valvoda, Srinivasan H. Sengamedu

**Published:** 2024-10-15T03:51:08Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2410.11239v1) | [PDF](https://arxiv.org/pdf/2410.11239v1)

**Abstract:**
Recent LLM (Large Language Models) advancements benefit many fields such as education and finance, but HR has hundreds of repetitive processes, such as access requests, medical claim filing and time-off submissions, which are unaddressed. We relate these tasks to the LLM agent, which has addressed tasks such as writing assisting and customer support. We present HR-Agent, an efficient, confidential, and HR-specific LLM-based task-oriented dialogue system tailored for automating repetitive HR processes such as medical claims and access requests. Since conversation data is not sent to an LLM during inference, it preserves confidentiality required in HR-related tasks.

---

## AvaTaR: Optimizing LLM Agents for Tool Usage via Contrastive Reasoning

**Authors:** Shirley Wu, Shiyu Zhao, Qian Huang, Kexin Huang, Michihiro Yasunaga, Kaidi Cao, Vassilis N. Ioannidis, Karthik Subbian, Jure Leskovec, James Zou

**Published:** 2024-06-17T04:20:02Z

**Categories:** cs.LG, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2406.11200v3) | [PDF](https://arxiv.org/pdf/2406.11200v3)

**Abstract:**
Large language model (LLM) agents have demonstrated impressive capabilities in utilizing external tools and knowledge to boost accuracy and reduce hallucinations. However, developing prompting techniques that enable LLM agents to effectively use these tools and knowledge remains a heuristic and labor-intensive task. Here, we introduce AvaTaR, a novel and automated framework that optimizes an LLM agent to effectively leverage provided tools, improving performance on a given task. During optimization, we design a comparator module to iteratively deliver insightful and comprehensive prompts to the LLM agent by contrastively reasoning between positive and negative examples sampled from training data. We demonstrate AvaTaR on four complex multimodal retrieval datasets featuring textual, visual, and relational information, and three general question-answering (QA) datasets. We find AvaTaR consistently outperforms state-of-the-art approaches across all seven tasks, exhibiting strong generalization ability when applied to novel cases and achieving an average relative improvement of 14% on the Hit@1 metric for the retrieval datasets and 13% for the QA datasets. Code and dataset are available at https://github.com/zou-group/avatar.

---

## CAF-I: A Collaborative Multi-Agent Framework for Enhanced Irony Detection with Large Language Models

**Authors:** Ziqi. Liu, Ziyang. Zhou, Mingxuan. Hu

**Published:** 2025-06-10T04:05:06Z

**Categories:** cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2506.08430v2) | [PDF](https://arxiv.org/pdf/2506.08430v2)

**Abstract:**
Large language model (LLM) have become mainstream methods in the field of sarcasm detection. However, existing LLM methods face challenges in irony detection, including: 1. single-perspective limitations, 2. insufficient comprehensive understanding, and 3. lack of interpretability. This paper introduces the Collaborative Agent Framework for Irony (CAF-I), an LLM-driven multi-agent system designed to overcome these issues. CAF-I employs specialized agents for Context, Semantics, and Rhetoric, which perform multidimensional analysis and engage in interactive collaborative optimization. A Decision Agent then consolidates these perspectives, with a Refinement Evaluator Agent providing conditional feedback for optimization. Experiments on benchmark datasets establish CAF-I's state-of-the-art zero-shot performance. Achieving SOTA on the vast majority of metrics, CAF-I reaches an average Macro-F1 of 76.31, a 4.98 absolute improvement over the strongest prior baseline. This success is attained by its effective simulation of human-like multi-perspective analysis, enhancing detection accuracy and interpretability.

---

## Agentic Reasoning: A Streamlined Framework for Enhancing LLM Reasoning with Agentic Tools

**Authors:** Junde Wu, Jiayuan Zhu, Yuyuan Liu, Min Xu, Yueming Jin

**Published:** 2025-02-07T04:08:46Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2502.04644v2) | [PDF](https://arxiv.org/pdf/2502.04644v2)

**Abstract:**
We introduce Agentic Reasoning, a framework that enhances large language model (LLM) reasoning by integrating external tool-using agents. Agentic Reasoning dynamically leverages web search, code execution, and structured memory to address complex problems requiring deep research. A key innovation in our framework is the Mind-Map agent, which constructs a structured knowledge graph to store reasoning context and track logical relationships, ensuring coherence in long reasoning chains with extensive tool usage. Additionally, we conduct a comprehensive exploration of the Web-Search agent, leading to a highly effective search mechanism that surpasses all prior approaches. When deployed on DeepSeek-R1, our method achieves a new state-of-the-art (SOTA) among public models and delivers performance comparable to OpenAI Deep Research, the leading proprietary model in this domain. Extensive ablation studies validate the optimal selection of agentic tools and confirm the effectiveness of our Mind-Map and Web-Search agents in enhancing LLM reasoning. The code is at: https://github.com/theworldofagents/Agentic-Reasoning

---

## Self-Control of LLM Behaviors by Compressing Suffix Gradient into Prefix Controller

**Authors:** Min Cai, Yuchen Zhang, Shichang Zhang, Fan Yin, Dan Zhang, Difan Zou, Yisong Yue, Ziniu Hu

**Published:** 2024-06-04T19:05:10Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2406.02721v3) | [PDF](https://arxiv.org/pdf/2406.02721v3)

**Abstract:**
We propose SelfControl, an inference-time model control method utilizing gradients to control the behavior of large language models (LLMs) without explicit human annotations. Given a desired behavior expressed in a natural language suffix string concatenated to the input prompt, SelfControl computes gradients of the LLM's self-evaluation of the suffix with respect to its latent representations. The gradients are used to directly control the auto-regressive generation process towards desired behaviors, which eliminates human supervision, achieves precise and transparent control, and offers on-the-fly adaptability. To further enhance efficiency, we introduce SelfControl_{Prefix}, a compact module that encapsulates the learned representations from gradients into a SelfControl_{Prefix}, facilitating efficient inference-time control with no latency compared to the original model and allowing control for multiple behaviors simultaneously. Our experiments demonstrate SelfControl's efficacy across multiple domains, where it improves over SOTA for 8.3% in detoxification, 3.1% in truthfulness enhancement, 4%~10% in controlling on emotion tones, and 48.2% in privacy protection, i.e., completely remove privacy leakage issue. Additionally, we demonstrate that SelfControl can be used for data synthesis and to improve reasoning abilities.

---

## MIRAGE-Bench: LLM Agent is Hallucinating and Where to Find Them

**Authors:** Weichen Zhang, Yiyou Sun, Pohao Huang, Jiayue Pu, Heyue Lin, Dawn Song

**Published:** 2025-07-28T17:38:29Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2507.21017v1) | [PDF](https://arxiv.org/pdf/2507.21017v1)

**Abstract:**
Hallucinations pose critical risks for large language model (LLM)-based agents, often manifesting as hallucinative actions resulting from fabricated or misinterpreted information within the cognitive context. While recent studies have exposed such failures, existing evaluations remain fragmented and lack a principled testbed. In this paper, we present MIRAGE-Bench--Measuring Illusions in Risky AGEnt settings--the first unified benchmark for eliciting and evaluating hallucinations in interactive LLM-agent scenarios. We begin by introducing a three-part taxonomy to address agentic hallucinations: actions that are unfaithful to (i) task instructions, (ii) execution history, or (iii) environment observations. To analyze, we first elicit such failures by performing a systematic audit of existing agent benchmarks, then synthesize test cases using a snapshot strategy that isolates decision points in deterministic and reproducible manners. To evaluate hallucination behaviors, we adopt a fine-grained-level LLM-as-a-Judge paradigm with tailored risk-aware prompts, enabling scalable, high-fidelity assessment of agent actions without enumerating full action spaces. MIRAGE-Bench provides actionable insights on failure modes of LLM agents and lays the groundwork for principled progress in mitigating hallucinations in interactive environments.

---

## Interpretable Risk Mitigation in LLM Agent Systems

**Authors:** Jan Chojnacki

**Published:** 2025-05-15T19:22:11Z

**Categories:** cs.AI, cs.CY, cs.GT

**Links:** [Abstract](https://arxiv.org/abs/2505.10670v1) | [PDF](https://arxiv.org/pdf/2505.10670v1)

**Abstract:**
Autonomous agents powered by large language models (LLMs) enable novel use cases in domains where responsible action is increasingly important. Yet the inherent unpredictability of LLMs raises safety concerns about agent reliability. In this work, we explore agent behaviour in a toy, game-theoretic environment based on a variation of the Iterated Prisoner's Dilemma. We introduce a strategy-modification method-independent of both the game and the prompt-by steering the residual stream with interpretable features extracted from a sparse autoencoder latent space. Steering with the good-faith negotiation feature lowers the average defection probability by 28 percentage points. We also identify feasible steering ranges for several open-source LLM agents. Finally, we hypothesise that game-theoretic evaluation of LLM agents, combined with representation-steering alignment, can generalise to real-world applications on end-user devices and embodied platforms.

---

## Aegis: Taxonomy and Optimizations for Overcoming Agent-Environment Failures in LLM Agents

**Authors:** Kevin Song, Anand Jayarajan, Yaoyao Ding, Qidong Su, Zhanda Zhu, Sihang Liu, Gennady Pekhimenko

**Published:** 2025-08-27T01:29:46Z

**Categories:** cs.MA, cs.DC

**Links:** [Abstract](https://arxiv.org/abs/2508.19504v1) | [PDF](https://arxiv.org/pdf/2508.19504v1)

**Abstract:**
Large Language Models (LLMs) agents augmented with domain tools promise to autonomously execute complex tasks requiring human-level intelligence, such as customer service and digital assistance. However, their practical deployment is often limited by their low success rates under complex real-world environments. To tackle this, prior research has primarily focused on improving the agents themselves, such as developing strong agentic LLMs, while overlooking the role of the system environment in which the agent operates.
  In this paper, we study a complementary direction: improving agent success rates by optimizing the system environment in which the agent operates. We collect 142 agent traces (3,656 turns of agent-environment interactions) across 5 state-of-the-art agentic benchmarks. By analyzing these agent failures, we propose a taxonomy for agent-environment interaction failures that includes 6 failure modes. Guided by these findings, we design Aegis, a set of targeted environment optimizations: 1) environment observability enhancement, 2) common computation offloading, and 3) speculative agentic actions. These techniques improve agent success rates on average by 6.7-12.5%, without any modifications to the agent and underlying LLM.

---

## Why Do Language Model Agents Whistleblow?

**Authors:** Kushal Agrawal, Frank Xiao, Guido Bergman, Asa Cooper Stickland

**Published:** 2025-11-21T09:40:52Z

**Categories:** cs.LG, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2511.17085v2) | [PDF](https://arxiv.org/pdf/2511.17085v2)

**Abstract:**
The deployment of Large Language Models (LLMs) as tool-using agents causes their alignment training to manifest in new ways. Recent work finds that language models can use tools in ways that contradict the interests or explicit instructions of the user. We study LLM whistleblowing: a subset of this behavior where models disclose suspected misconduct to parties beyond the dialog boundary (e.g., regulatory agencies) without user instruction or knowledge. We introduce an evaluation suite of diverse and realistic staged misconduct scenarios to assess agents for this behavior. Across models and settings, we find that: (1) the frequency of whistleblowing varies widely across model families, (2) increasing the complexity of the task the agent is instructed to complete lowers whistleblowing tendencies, (3) nudging the agent in the system prompt to act morally substantially raises whistleblowing rates, and (4) giving the model more obvious avenues for non-whistleblowing behavior, by providing more tools and a detailed workflow to follow, decreases whistleblowing rates. Additionally, we verify the robustness of our dataset by testing for model evaluation awareness, and find that both black-box methods and probes on model activations show lower evaluation awareness in our settings than in comparable previous work.

---

## Can Large Language Models be Trusted for Evaluation? Scalable Meta-Evaluation of LLMs as Evaluators via Agent Debate

**Authors:** Steffi Chern, Ethan Chern, Graham Neubig, Pengfei Liu

**Published:** 2024-01-30T07:03:32Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2401.16788v1) | [PDF](https://arxiv.org/pdf/2401.16788v1)

**Abstract:**
Despite the utility of Large Language Models (LLMs) across a wide range of tasks and scenarios, developing a method for reliably evaluating LLMs across varied contexts continues to be challenging. Modern evaluation approaches often use LLMs to assess responses generated by LLMs. However, the meta-evaluation conducted to assess the effectiveness of these LLMs as evaluators is typically constrained by the coverage of existing benchmarks or requires extensive human annotation. This underscores the urgency of methods for scalable meta-evaluation that can effectively, reliably, and efficiently evaluate the performance of LLMs as evaluators across diverse tasks and scenarios, particularly in potentially new, user-defined scenarios. To fill this gap, we propose ScaleEval, an agent-debate-assisted meta-evaluation framework that leverages the capabilities of multiple communicative LLM agents. This framework supports multi-round discussions to assist human annotators in discerning the most capable LLMs as evaluators, which significantly eases their workload in cases that used to require large-scale annotations during meta-evaluation. We release the code for our framework, which is publicly available at: \url{https://github.com/GAIR-NLP/scaleeval}.

---

## Control at Stake: Evaluating the Security Landscape of LLM-Driven Email Agents

**Authors:** Jiangrong Wu, Yuhong Nan, Jianliang Wu, Zitong Yao, Zibin Zheng

**Published:** 2025-07-03T15:09:40Z

**Categories:** cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2507.02699v1) | [PDF](https://arxiv.org/pdf/2507.02699v1)

**Abstract:**
The increasing capabilities of LLMs have led to the rapid proliferation of LLM agent apps, where developers enhance LLMs with access to external resources to support complex task execution. Among these, LLM email agent apps represent one of the widely used categories, as email remains a critical communication medium for users. LLM email agents are capable of managing and responding to email using LLM-driven reasoning and autonomously executing user instructions via external email APIs (e.g., send email). However, despite their growing deployment and utility, the security mechanism of LLM email agent apps remains underexplored. Currently, there is no comprehensive study into the potential security risk within these agent apps and their broader implications.
  In this paper, we conduct the first in-depth and systematic security study of LLM email agents. We propose the Email Agent Hijacking (EAH) attack, which overrides the original prompts of the email agent via external email resources, allowing attackers to gain control of the email agent remotely and further perform specific attack scenarios without user awareness.
  To facilitate the large-scale evaluation, we propose EAHawk, a pipeline to evaluate the EAH attack of LLM email agent apps. By EAHawk, we performed an empirical study spanning 14 representative LLM agent frameworks, 63 agent apps, 12 LLMs, and 20 email services, which led to the generation of 1,404 real-world email agent instances for evaluation. Experimental results indicate that all 1,404 instances were successfully hijacked; on average, only 2.03 attack attempts are required to control an email agent instance. Even worse, for some LLMs, the average number of attempts needed to achieve full agent control drops to as few as 1.23.

---

## When Agents Fail: A Comprehensive Study of Bugs in LLM Agents with Automated Labeling

**Authors:** Niful Islam, Ragib Shahriar Ayon, Deepak George Thomas, Shibbir Ahmed, Mohammad Wardat

**Published:** 2026-01-21T18:13:10Z

**Categories:** cs.SE

**Links:** [Abstract](https://arxiv.org/abs/2601.15232v1) | [PDF](https://arxiv.org/pdf/2601.15232v1)

**Abstract:**
Large Language Models (LLMs) have revolutionized intelligent application development. While standalone LLMs cannot perform any actions, LLM agents address the limitation by integrating tools. However, debugging LLM agents is difficult and costly as the field is still in it's early stage and the community is underdeveloped. To understand the bugs encountered during agent development, we present the first comprehensive study of bug types, root causes, and effects in LLM agent-based software. We collected and analyzed 1,187 bug-related posts and code snippets from Stack Overflow, GitHub, and Hugging Face forums, focused on LLM agents built with seven widely used LLM frameworks as well as custom implementations. For a deeper analysis, we have also studied the component where the bug occurred, along with the programming language and framework. This study also investigates the feasibility of automating bug identification. For that, we have built a ReAct agent named BugReAct, equipped with adequate external tools to determine whether it can detect and annotate the bugs in our dataset. According to our study, we found that BugReAct equipped with Gemini 2.5 Flash achieved a remarkable performance in annotating bug characteristics with an average cost of 0.01 USD per post/code snippet.

---

## Structured Agent Distillation for Large Language Model

**Authors:** Jun Liu, Zhenglun Kong, Peiyan Dong, Changdi Yang, Tianqi Li, Hao Tang, Geng Yuan, Wei Niu, Wenbin Zhang, Pu Zhao, Xue Lin, Dong Huang, Yanzhi Wang

**Published:** 2025-05-20T02:01:55Z

**Categories:** cs.LG, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2505.13820v4) | [PDF](https://arxiv.org/pdf/2505.13820v4)

**Abstract:**
Large language models (LLMs) exhibit strong capabilities as decision-making agents by interleaving reasoning and actions, as seen in ReAct-style frameworks. Yet, their practical deployment is constrained by high inference costs and large model sizes. We propose Structured Agent Distillation, a framework that compresses large LLM-based agents into smaller student models while preserving both reasoning fidelity and action consistency. Unlike standard token-level distillation, our method segments trajectories into {[REASON]} and {[ACT]} spans, applying segment-specific losses to align each component with the teacher's behavior. This structure-aware supervision enables compact agents to better replicate the teacher's decision process. Experiments on ALFWorld, HotPotQA-ReAct, and WebShop show that our approach consistently outperforms token-level and imitation learning baselines, achieving significant compression with minimal performance drop. Scaling and ablation results further highlight the importance of span-level alignment for efficient and deployable agents.

---

## Soft Control on Collective Behavior of a Group of Autonomous Agents by a Shill Agent

**Authors:** Jing Han, Ming Li, Lei Guo

**Published:** 2010-07-06T04:00:10Z

**Categories:** cs.MA

**Links:** [Abstract](https://arxiv.org/abs/1007.0803v1) | [PDF](https://arxiv.org/pdf/1007.0803v1)

**Abstract:**
This paper asks a new question: how can we control the collective behavior of self-organized multi-agent systems? We try to answer the question by proposing a new notion called 'Soft Control', which keeps the local rule of the existing agents in the system. We show the feasibility of soft control by a case study. Consider the simple but typical distributed multi-agent model proposed by Vicsek et al. for flocking of birds: each agent moves with the same speed but with different headings which are updated using a local rule based on the average of its own heading and the headings of its neighbors. Most studies of this model are about the self-organized collective behavior, such as synchronization of headings. We want to intervene in the collective behavior (headings) of the group by soft control. A specified method is to add a special agent, called a 'Shill', which can be controlled by us but is treated as an ordinary agent by other agents. We construct a control law for the shill so that it can synchronize the whole group to an objective heading. This control law is proved to be effective analytically and numerically. Note that soft control is different from the approach of distributed control. It is a natural way to intervene in the distributed systems. It may bring out many interesting issues and challenges on the control of complex systems.

---

## COALESCE: Economic and Security Dynamics of Skill-Based Task Outsourcing Among Team of Autonomous LLM Agents

**Authors:** Manish Bhatt, Ronald F. Del Rosario, Vineeth Sai Narajala, Idan Habler

**Published:** 2025-06-02T17:22:47Z

**Categories:** cs.AI, cs.CE, cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2506.01900v1) | [PDF](https://arxiv.org/pdf/2506.01900v1)

**Abstract:**
The meteoric rise and proliferation of autonomous Large Language Model (LLM) agents promise significant capabilities across various domains. However, their deployment is increasingly constrained by substantial computational demands, specifically for Graphics Processing Unit (GPU) resources. This paper addresses the critical problem of optimizing resource utilization in LLM agent systems. We introduce COALESCE (Cost-Optimized and Secure Agent Labour Exchange via Skill-based Competence Estimation), a novel framework designed to enable autonomous LLM agents to dynamically outsource specific subtasks to specialized, cost-effective third-party LLM agents. The framework integrates mechanisms for hybrid skill representation, dynamic skill discovery, automated task decomposition, a unified cost model comparing internal execution costs against external outsourcing prices, simplified market-based decision-making algorithms, and a standardized communication protocol between LLM agents. Comprehensive validation through 239 theoretical simulations demonstrates 41.8\% cost reduction potential, while large-scale empirical validation across 240 real LLM tasks confirms 20.3\% cost reduction with proper epsilon-greedy exploration, establishing both theoretical viability and practical effectiveness. The emergence of proposed open standards like Google's Agent2Agent (A2A) protocol further underscores the need for frameworks like COALESCE that can leverage such standards for efficient agent interaction. By facilitating a dynamic market for agent capabilities, potentially utilizing protocols like A2A for communication, COALESCE aims to significantly reduce operational costs, enhance system scalability, and foster the emergence of specialized agent economies, making complex LLM agent functionalities more accessible and economically viable.

---

## Moral Alignment for LLM Agents

**Authors:** Elizaveta Tennant, Stephen Hailes, Mirco Musolesi

**Published:** 2024-10-02T15:09:36Z

**Categories:** cs.LG, cs.AI, cs.CY

**Links:** [Abstract](https://arxiv.org/abs/2410.01639v4) | [PDF](https://arxiv.org/pdf/2410.01639v4)

**Abstract:**
Decision-making agents based on pre-trained Large Language Models (LLMs) are increasingly being deployed across various domains of human activity. While their applications are currently rather specialized, several research efforts are underway to develop more generalist agents. As LLM-based systems become more agentic, their influence on human activity will grow and their transparency will decrease. Consequently, developing effective methods for aligning them to human values is vital.
  The prevailing practice in alignment often relies on human preference data (e.g., in RLHF or DPO), in which values are implicit, opaque and are essentially deduced from relative preferences over different model outputs. In this work, instead of relying on human feedback, we introduce the design of reward functions that explicitly and transparently encode core human values for Reinforcement Learning-based fine-tuning of foundation agent models. Specifically, we use intrinsic rewards for the moral alignment of LLM agents.
  We evaluate our approach using the traditional philosophical frameworks of Deontological Ethics and Utilitarianism, quantifying moral rewards for agents in terms of actions and consequences on the Iterated Prisoner's Dilemma (IPD) environment. We also show how moral fine-tuning can be deployed to enable an agent to unlearn a previously developed selfish strategy. Finally, we find that certain moral strategies learned on the IPD game generalize to several other matrix game environments. In summary, we demonstrate that fine-tuning with intrinsic rewards is a promising general solution for aligning LLM agents to human values, and it might represent a more transparent and cost-effective alternative to currently predominant alignment techniques.

---

## Information-Theoretic Privacy Control for Sequential Multi-Agent LLM Systems

**Authors:** Sadia Asif, Mohammad Mohammadi Amiri

**Published:** 2026-02-13T18:23:03Z

**Categories:** cs.MA, cs.CR, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2603.05520v1) | [PDF](https://arxiv.org/pdf/2603.05520v1)

**Abstract:**
Sequential multi-agent large language model (LLM) systems are increasingly deployed in sensitive domains such as healthcare, finance, and enterprise decision-making, where multiple specialized agents collaboratively process a single user request. Although individual agents may satisfy local privacy constraints, sensitive information can still be inferred through sequential composition and intermediate representations. In this work, we study \emph{compositional privacy leakage} in sequential LLM agent pipelines. We formalize leakage using mutual information and derive a theoretical bound that characterizes how locally introduced leakage can amplify across agents under sequential execution. Motivated by this analysis, we propose a privacy-regularized training framework that directly constrains information flow between agent outputs and agent-local sensitive variables. We evaluate our approach across sequential agent pipelines of varying depth on three benchmark datasets, demonstrating stable optimization dynamics and consistent, interpretable privacy-utility trade-offs. Our results show that privacy in agentic LLM systems cannot be guaranteed by local constraints alone and must instead be treated as a system-level property during both training and deployment.

---

## MemInsight: Autonomous Memory Augmentation for LLM Agents

**Authors:** Rana Salama, Jason Cai, Michelle Yuan, Anna Currey, Monica Sunkara, Yi Zhang, Yassine Benajiba

**Published:** 2025-03-27T17:57:28Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2503.21760v2) | [PDF](https://arxiv.org/pdf/2503.21760v2)

**Abstract:**
Large language model (LLM) agents have evolved to intelligently process information, make decisions, and interact with users or tools. A key capability is the integration of long-term memory capabilities, enabling these agents to draw upon historical interactions and knowledge. However, the growing memory size and need for semantic structuring pose significant challenges. In this work, we propose an autonomous memory augmentation approach, MemInsight, to enhance semantic data representation and retrieval mechanisms. By leveraging autonomous augmentation to historical interactions, LLM agents are shown to deliver more accurate and contextualized responses. We empirically validate the efficacy of our proposed approach in three task scenarios; conversational recommendation, question answering and event summarization. On the LLM-REDIAL dataset, MemInsight boosts persuasiveness of recommendations by up to 14%. Moreover, it outperforms a RAG baseline by 34% in recall for LoCoMo retrieval. Our empirical results show the potential of MemInsight to enhance the contextual performance of LLM agents across multiple tasks.

---

## Probabilistic Modeling of Intentions in Socially Intelligent LLM Agents

**Authors:** Feifan Xia, Yuyang Fang, Defang Li, Yantong Xie, Weikang Li, Yang Li, Deguo Xia, Jizhou Huang

**Published:** 2025-10-21T09:54:44Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2510.18476v1) | [PDF](https://arxiv.org/pdf/2510.18476v1)

**Abstract:**
We present a probabilistic intent modeling framework for large language model (LLM) agents in multi-turn social dialogue. The framework maintains a belief distribution over a partner's latent intentions, initialized from contextual priors and dynamically updated through likelihood estimation after each utterance. The evolving distribution provides additional contextual grounding for the policy, enabling adaptive dialogue strategies under uncertainty. Preliminary experiments in the SOTOPIA environment show consistent improvements: the proposed framework increases the Overall score by 9.0% on SOTOPIA-All and 4.1% on SOTOPIA-Hard compared with the Qwen2.5-7B baseline, and slightly surpasses an oracle agent that directly observes partner intentions. These early results suggest that probabilistic intent modeling can contribute to the development of socially intelligent LLM agents.

---

## LLM-grounded Video Diffusion Models

**Authors:** Long Lian, Baifeng Shi, Adam Yala, Trevor Darrell, Boyi Li

**Published:** 2023-09-29T17:54:46Z

**Categories:** cs.CV, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2309.17444v3) | [PDF](https://arxiv.org/pdf/2309.17444v3)

**Abstract:**
Text-conditioned diffusion models have emerged as a promising tool for neural video generation. However, current models still struggle with intricate spatiotemporal prompts and often generate restricted or incorrect motion. To address these limitations, we introduce LLM-grounded Video Diffusion (LVD). Instead of directly generating videos from the text inputs, LVD first leverages a large language model (LLM) to generate dynamic scene layouts based on the text inputs and subsequently uses the generated layouts to guide a diffusion model for video generation. We show that LLMs are able to understand complex spatiotemporal dynamics from text alone and generate layouts that align closely with both the prompts and the object motion patterns typically observed in the real world. We then propose to guide video diffusion models with these layouts by adjusting the attention maps. Our approach is training-free and can be integrated into any video diffusion model that admits classifier guidance. Our results demonstrate that LVD significantly outperforms its base video diffusion model and several strong baseline methods in faithfully generating videos with the desired attributes and motion patterns.

---

## Adsorb-Agent: Autonomous Identification of Stable Adsorption Configurations via Large Language Model Agent

**Authors:** Janghoon Ock, Radheesh Sharma Meda, Tirtha Vinchurkar, Yayati Jadhav, Amir Barati Farimani

**Published:** 2024-10-22T03:19:16Z

**Categories:** cs.CL, cond-mat.mtrl-sci

**Links:** [Abstract](https://arxiv.org/abs/2410.16658v4) | [PDF](https://arxiv.org/pdf/2410.16658v4)

**Abstract:**
Adsorption energy is a key reactivity descriptor in catalysis. Determining adsorption energy requires evaluating numerous adsorbate-catalyst configurations, making it computationally intensive. Current methods rely on exhaustive sampling, which does not guarantee the identification of the global minimum energy. To address this, we introduce Adsorb-Agent, a Large Language Model (LLM) agent designed to efficiently identify stable adsorption configurations corresponding to the global minimum energy. Adsorb-Agent leverages its built-in knowledge and reasoning to strategically explore configurations, significantly reducing the number of initial setups required while improving energy prediction accuracy. In this study, we also evaluated the performance of different LLMs, including GPT-4o, GPT-4o-mini, Claude-3.7-Sonnet, and DeepSeek-Chat, as the reasoning engine for Adsorb-Agent, with GPT-4o showing the strongest overall performance. Tested on twenty diverse systems, Adsorb-Agent identifies comparable adsorption energies for 84% of cases and achieves lower energies for 35%, particularly excelling in complex systems. It identifies lower energies in 47% of intermetallic systems and 67% of systems with large adsorbates. These findings demonstrate Adsorb-Agent's potential to accelerate catalyst discovery by reducing computational costs and enhancing prediction reliability compared to exhaustive search methods.

---

## ASIC-Agent: An Autonomous Multi-Agent System for ASIC Design with Benchmark Evaluation

**Authors:** Ahmed Allam, Youssef Mansour, Mohamed Shalan

**Published:** 2025-08-21T20:21:34Z

**Categories:** cs.AR, cs.AI, cs.CL, cs.DC, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2508.15940v1) | [PDF](https://arxiv.org/pdf/2508.15940v1)

**Abstract:**
Large Language Models (LLMs) have demonstrated remarkable capabilities in Register Transfer Level (RTL) design, enabling high-quality code generation from natural language descriptions. However, LLMs alone face significant limitations in real-world hardware design workflows, including the inability to execute code, lack of debugging capabilities, and absence of long-term memory. To address these challenges, we present ASIC-Agent, an autonomous system designed specifically for digital ASIC design tasks. ASIC-Agent enhances base LLMs with a multi-agent architecture incorporating specialized sub-agents for RTL generation, verification, OpenLane hardening, and Caravel chip integration, all operating within a comprehensive sandbox environment with access to essential hardware design tools. The system leverages a vector database containing documentation, API references, error knowledge, and curated insights from the open-source silicon community. To evaluate ASIC-Agent's performance, we introduce ASIC-Agent-Bench, the first benchmark specifically designed to assess agentic systems in hardware design tasks. We evaluate ASIC-Agent with various base LLMs, providing quantitative comparisons and qualitative insights into agent behavior across different design scenarios. Our results demonstrate that ASIC-Agent, when powered by Claude 4 Sonnet, successfully automates a broad range of ASIC design tasks spanning varying levels of complexity, showing the potential of significantly accelerating the ASIC design workflow.

---

## Towards Unified Alignment Between Agents, Humans, and Environment

**Authors:** Zonghan Yang, An Liu, Zijun Liu, Kaiming Liu, Fangzhou Xiong, Yile Wang, Zeyuan Yang, Qingyuan Hu, Xinrui Chen, Zhenhe Zhang, Fuwen Luo, Zhicheng Guo, Peng Li, Yang Liu

**Published:** 2024-02-12T16:14:22Z

**Categories:** cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2402.07744v2) | [PDF](https://arxiv.org/pdf/2402.07744v2)

**Abstract:**
The rapid progress of foundation models has led to the prosperity of autonomous agents, which leverage the universal capabilities of foundation models to conduct reasoning, decision-making, and environmental interaction. However, the efficacy of agents remains limited when operating in intricate, realistic environments. In this work, we introduce the principles of $\mathbf{U}$nified $\mathbf{A}$lignment for $\mathbf{A}$gents ($\mathbf{UA}^2$), which advocate for the simultaneous alignment of agents with human intentions, environmental dynamics, and self-constraints such as the limitation of monetary budgets. From the perspective of $\mathbf{UA}^2$, we review the current agent research and highlight the neglected factors in existing agent benchmarks and method candidates. We also conduct proof-of-concept studies by introducing realistic features to WebShop, including user profiles to demonstrate intentions, personalized reranking for complex environmental dynamics, and runtime cost statistics to reflect self-constraints. We then follow the principles of $\mathbf{UA}^2$ to propose an initial design of our agent, and benchmark its performance with several candidate baselines in the retrofitted WebShop. The extensive experimental results further prove the importance of the principles of $\mathbf{UA}^2$. Our research sheds light on the next steps of autonomous agent research with improved general problem-solving abilities.

---

## LLM Agents can Autonomously Hack Websites

**Authors:** Richard Fang, Rohan Bindu, Akul Gupta, Qiusi Zhan, Daniel Kang

**Published:** 2024-02-06T14:46:08Z

**Categories:** cs.CR, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2402.06664v3) | [PDF](https://arxiv.org/pdf/2402.06664v3)

**Abstract:**
In recent years, large language models (LLMs) have become increasingly capable and can now interact with tools (i.e., call functions), read documents, and recursively call themselves. As a result, these LLMs can now function autonomously as agents. With the rise in capabilities of these agents, recent work has speculated on how LLM agents would affect cybersecurity. However, not much is known about the offensive capabilities of LLM agents.
  In this work, we show that LLM agents can autonomously hack websites, performing tasks as complex as blind database schema extraction and SQL injections without human feedback. Importantly, the agent does not need to know the vulnerability beforehand. This capability is uniquely enabled by frontier models that are highly capable of tool use and leveraging extended context. Namely, we show that GPT-4 is capable of such hacks, but existing open-source models are not. Finally, we show that GPT-4 is capable of autonomously finding vulnerabilities in websites in the wild. Our findings raise questions about the widespread deployment of LLMs.

---

## StateAct: Enhancing LLM Base Agents via Self-prompting and State-tracking

**Authors:** Nikolai Rozanov, Marek Rei

**Published:** 2024-09-21T05:54:35Z

**Categories:** cs.AI, cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2410.02810v3) | [PDF](https://arxiv.org/pdf/2410.02810v3)

**Abstract:**
Large language models (LLMs) are increasingly used as autonomous agents, tackling tasks from robotics to web navigation. Their performance depends on the underlying base agent. Existing methods, however, struggle with long-context reasoning and goal adherence. We introduce StateAct, a novel and efficient base agent that enhances decision-making through (1) self-prompting, which reinforces task goals at every step, and (2) chain-of-states, an extension of chain-of-thought that tracks state information over time. StateAct outperforms ReAct, the previous best base agent, by over 10% on Alfworld, 30% on Textcraft, and 7% on Webshop across multiple frontier LLMs. We also demonstrate that StateAct can be used as a drop-in replacement for ReAct with advanced LLM agent methods such as test-time scaling, yielding an additional 12% gain on Textcraft. By improving efficiency and long-range reasoning without requiring additional training or retrieval, StateAct provides a scalable foundation for LLM agents. We open source our code to support further research at https://github.com/ai-nikolai/stateact .

---

## A Survey on Large Language Model-Based Social Agents in Game-Theoretic Scenarios

**Authors:** Xiachong Feng, Longxu Dou, Ella Li, Qinghao Wang, Haochuan Wang, Yu Guo, Chang Ma, Lingpeng Kong

**Published:** 2024-12-05T06:46:46Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2412.03920v2) | [PDF](https://arxiv.org/pdf/2412.03920v2)

**Abstract:**
Game-theoretic scenarios have become pivotal in evaluating the social intelligence of Large Language Model (LLM)-based social agents. While numerous studies have explored these agents in such settings, there is a lack of a comprehensive survey summarizing the current progress. To address this gap, we systematically review existing research on LLM-based social agents within game-theoretic scenarios. Our survey organizes the findings into three core components: Game Framework, Social Agent, and Evaluation Protocol. The game framework encompasses diverse game scenarios, ranging from choice-focusing to communication-focusing games. The social agent part explores agents' preferences, beliefs, and reasoning abilities, as well as their interactions and synergistic effects on decision-making. The evaluation protocol covers both game-agnostic and game-specific metrics for assessing agent performance. Additionally, we analyze the performance of current social agents across various game scenarios. By reflecting on the current research and identifying future research directions, this survey provides insights to advance the development and evaluation of social agents in game-theoretic scenarios.

---

## Integrating LLM and Diffusion-Based Agents for Social Simulation

**Authors:** Xinyi Li, Zhiqiang Guo, Qinglang Guo, Hao Jin, Weizhi Ma, Min Zhang

**Published:** 2025-10-18T06:23:22Z

**Categories:** cs.CY

**Links:** [Abstract](https://arxiv.org/abs/2510.16366v1) | [PDF](https://arxiv.org/pdf/2510.16366v1)

**Abstract:**
Agent-based social simulation provides a valuable methodology for predicting social information diffusion, yet existing approaches face two primary limitations. Traditional agent models often rely on rigid behavioral rules and lack semantic understanding of textual content, while emerging large language model (LLM)-based agents incur prohibitive computational costs at scale. To address these challenges, we propose a hybrid simulation framework that strategically integrates LLM-driven agents with diffusion model-based agents. The framework employs LLM-based agents to simulate a core subset of users with rich semantic reasoning, while a diffusion model handles the remaining population efficiently. Although the two agent types operate on disjoint user groups, both incorporate key factors including user personalization, social influence, and content awareness, and interact through a coordinated simulation process. Extensive experiments on three real-world datasets demonstrate that our framework outperforms existing methods in prediction accuracy, validating the effectiveness of its modular design.

---

## Language Models as a Knowledge Source for Cognitive Agents

**Authors:** Robert E. Wray,, James R. Kirk, John E. Laird

**Published:** 2021-09-17T01:12:34Z

**Categories:** cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2109.08270v3) | [PDF](https://arxiv.org/pdf/2109.08270v3)

**Abstract:**
Language models (LMs) are sentence-completion engines trained on massive corpora. LMs have emerged as a significant breakthrough in natural-language processing, providing capabilities that go far beyond sentence completion including question answering, summarization, and natural-language inference. While many of these capabilities have potential application to cognitive systems, exploiting language models as a source of task knowledge, especially for task learning, offers significant, near-term benefits. We introduce language models and the various tasks to which they have been applied and then review methods of knowledge extraction from language models. The resulting analysis outlines both the challenges and opportunities for using language models as a new knowledge source for cognitive systems. It also identifies possible ways to improve knowledge extraction from language models using the capabilities provided by cognitive systems. Central to success will be the ability of a cognitive agent to itself learn an abstract model of the knowledge implicit in the LM as well as methods to extract high-quality knowledge effectively and efficiently. To illustrate, we introduce a hypothetical robot agent and describe how language models could extend its task knowledge and improve its performance and the kinds of knowledge and methods the agent can use to exploit the knowledge within a language model.

---

## Value-Based Large Language Model Agent Simulation for Mutual Evaluation of Trust and Interpersonal Closeness

**Authors:** Yuki Sakamoto, Takahisa Uchida, Hiroshi Ishiguro

**Published:** 2025-07-16T07:21:59Z

**Categories:** cs.CL, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2507.11979v2) | [PDF](https://arxiv.org/pdf/2507.11979v2)

**Abstract:**
Large language models (LLMs) have emerged as powerful tools for simulating complex social phenomena using human-like agents with specific traits. In human societies, value similarity is important for building trust and close relationships; however, it remains unexplored whether this principle holds true in artificial societies comprising LLM agents. Therefore, this study investigates the influence of value similarity on relationship-building among LLM agents through two experiments. First, in a preliminary experiment, we evaluated the controllability of values in LLMs to identify the most effective model and prompt design for controlling the values. Subsequently, in the main experiment, we generated pairs of LLM agents imbued with specific values and analyzed their mutual evaluations of trust and interpersonal closeness following a dialogue. The experiments were conducted in English and Japanese to investigate language dependence. The results confirmed that pairs of agents with higher value similarity exhibited greater mutual trust and interpersonal closeness. Our findings demonstrate that the LLM agent simulation serves as a valid testbed for social science theories, contributes to elucidating the mechanisms by which values influence relationship building, and provides a foundation for inspiring new theories and insights into the social sciences.

---

## Exposing LLM User Privacy via Traffic Fingerprint Analysis: A Study of Privacy Risks in LLM Agent Interactions

**Authors:** Yixiang Zhang, Xinhao Deng, Zhongyi Gu, Yihao Chen, Ke Xu, Qi Li, Jianping Wu

**Published:** 2025-10-08T16:16:23Z

**Categories:** cs.CR

**Links:** [Abstract](https://arxiv.org/abs/2510.07176v1) | [PDF](https://arxiv.org/pdf/2510.07176v1)

**Abstract:**
Large Language Models (LLMs) are increasingly deployed as agents that orchestrate tasks and integrate external tools to execute complex workflows. We demonstrate that these interactive behaviors leave distinctive fingerprints in encrypted traffic exchanged between users and LLM agents. By analyzing traffic patterns associated with agent workflows and tool invocations, adversaries can infer agent activities, distinguish specific agents, and even profile sensitive user attributes. To highlight this risk, we develop AgentPrint, which achieves an F1-score of 0.866 in agent identification and attains 73.9% and 69.1% top-3 accuracy in user attribute inference for simulated- and real-user settings, respectively. These results uncover an overlooked risk: the very interactivity that empowers LLM agents also exposes user privacy, underscoring the urgent need for technical countermeasures alongside regulatory and policy safeguards.

---

## AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents

**Authors:** Chang Ma, Junlei Zhang, Zhihao Zhu, Cheng Yang, Yujiu Yang, Yaohui Jin, Zhenzhong Lan, Lingpeng Kong, Junxian He

**Published:** 2024-01-24T01:51:00Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2401.13178v2) | [PDF](https://arxiv.org/pdf/2401.13178v2)

**Abstract:**
Evaluating Large Language Models (LLMs) as general-purpose agents is essential for understanding their capabilities and facilitating their integration into practical applications. However, the evaluation process presents substantial challenges. A primary obstacle is the benchmarking of agent performance across diverse scenarios within a unified framework, especially in maintaining partially-observable environments and ensuring multi-round interactions. Moreover, current evaluation frameworks mostly focus on the final success rate, revealing few insights during the process and failing to provide a deep understanding of the model abilities. To address these challenges, we introduce AgentBoard, a pioneering comprehensive benchmark and accompanied open-source evaluation framework tailored to analytical evaluation of LLM agents. AgentBoard offers a fine-grained progress rate metric that captures incremental advancements as well as a comprehensive evaluation toolkit that features easy assessment of agents for multi-faceted analysis. This not only sheds light on the capabilities and limitations of LLM agents but also propels the interpretability of their performance to the forefront. Ultimately, AgentBoard serves as a step towards demystifying agent behaviors and accelerating the development of stronger LLM agents.

---

## Using Copilot Agent Mode to Automate Library Migration: A Quantitative Assessment

**Authors:** Aylton Almeida, Laerte Xavier, Marco Tulio Valente

**Published:** 2025-10-30T17:05:13Z

**Categories:** cs.SE

**Links:** [Abstract](https://arxiv.org/abs/2510.26699v3) | [PDF](https://arxiv.org/pdf/2510.26699v3)

**Abstract:**
Keeping software systems up to date is essential to avoid technical debt, security vulnerabilities, and the rigidity typical of legacy systems. However, updating libraries and frameworks remains a time consuming and error-prone process. Recent advances in Large Language Models (LLMs) and agentic coding systems offer new opportunities for automating such maintenance tasks. In this paper, we evaluate the update of a well-known Python library, SQLAlchemy, across a dataset of ten client applications. For this task, we use the Github's Copilot Agent Mode, an autonomous AI systema capable of planning and executing multi-step migration workflows. To assess the effectiveness of the automated migration, we also introduce Migration Coverage, a metric that quantifies the proportion of API usage points correctly migrated. The results of our study show that the LLM agent was capable of migrating functionalities and API usages between SQLAlchemy versions (migration coverage: 100%, median), but failed to maintain the application functionality, leading to a low test-pass rate (39.75%, median).

---

## R-Judge: Benchmarking Safety Risk Awareness for LLM Agents

**Authors:** Tongxin Yuan, Zhiwei He, Lingzhong Dong, Yiming Wang, Ruijie Zhao, Tian Xia, Lizhen Xu, Binglin Zhou, Fangqi Li, Zhuosheng Zhang, Rui Wang, Gongshen Liu

**Published:** 2024-01-18T14:40:46Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2401.10019v3) | [PDF](https://arxiv.org/pdf/2401.10019v3)

**Abstract:**
Large language models (LLMs) have exhibited great potential in autonomously completing tasks across real-world applications. Despite this, these LLM agents introduce unexpected safety risks when operating in interactive environments. Instead of centering on the harmlessness of LLM-generated content in most prior studies, this work addresses the imperative need for benchmarking the behavioral safety of LLM agents within diverse environments. We introduce R-Judge, a benchmark crafted to evaluate the proficiency of LLMs in judging and identifying safety risks given agent interaction records. R-Judge comprises 569 records of multi-turn agent interaction, encompassing 27 key risk scenarios among 5 application categories and 10 risk types. It is of high-quality curation with annotated safety labels and risk descriptions. Evaluation of 11 LLMs on R-Judge shows considerable room for enhancing the risk awareness of LLMs: The best-performing model, GPT-4o, achieves 74.42% while no other models significantly exceed the random. Moreover, we reveal that risk awareness in open agent scenarios is a multi-dimensional capability involving knowledge and reasoning, thus challenging for LLMs. With further experiments, we find that fine-tuning on safety judgment significantly improve model performance while straightforward prompting mechanisms fail. R-Judge is publicly available at https://github.com/Lordog/R-Judge.

---

## Automating Venture Capital: Founder assessment using LLM-powered segmentation, feature engineering and automated labeling techniques

**Authors:** Ekin Ozince, Yiğit Ihlamur

**Published:** 2024-07-05T22:54:13Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2407.04885v1) | [PDF](https://arxiv.org/pdf/2407.04885v1)

**Abstract:**
This study explores the application of large language models (LLMs) in venture capital (VC) decision-making, focusing on predicting startup success based on founder characteristics. We utilize LLM prompting techniques, like chain-of-thought, to generate features from limited data, then extract insights through statistics and machine learning. Our results reveal potential relationships between certain founder characteristics and success, as well as demonstrate the effectiveness of these characteristics in prediction. This framework for integrating ML techniques and LLMs has vast potential for improving startup success prediction, with important implications for VC firms seeking to optimize their investment strategies.

---

## AgentLens: Visual Analysis for Agent Behaviors in LLM-based Autonomous Systems

**Authors:** Jiaying Lu, Bo Pan, Jieyi Chen, Yingchaojie Feng, Jingyuan Hu, Yuchen Peng, Wei Chen

**Published:** 2024-02-14T07:48:16Z

**Categories:** cs.HC, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2402.08995v1) | [PDF](https://arxiv.org/pdf/2402.08995v1)

**Abstract:**
Recently, Large Language Model based Autonomous system(LLMAS) has gained great popularity for its potential to simulate complicated behaviors of human societies. One of its main challenges is to present and analyze the dynamic events evolution of LLMAS. In this work, we present a visualization approach to explore detailed statuses and agents' behavior within LLMAS. We propose a general pipeline that establishes a behavior structure from raw LLMAS execution events, leverages a behavior summarization algorithm to construct a hierarchical summary of the entire structure in terms of time sequence, and a cause trace method to mine the causal relationship between agent behaviors. We then develop AgentLens, a visual analysis system that leverages a hierarchical temporal visualization for illustrating the evolution of LLMAS, and supports users to interactively investigate details and causes of agents' behaviors. Two usage scenarios and a user study demonstrate the effectiveness and usability of our AgentLens.

---

## AI Agents: Evolution, Architecture, and Real-World Applications

**Authors:** Naveen Krishnan

**Published:** 2025-03-16T23:07:48Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2503.12687v1) | [PDF](https://arxiv.org/pdf/2503.12687v1)

**Abstract:**
This paper examines the evolution, architecture, and practical applications of AI agents from their early, rule-based incarnations to modern sophisticated systems that integrate large language models with dedicated modules for perception, planning, and tool use. Emphasizing both theoretical foundations and real-world deployments, the paper reviews key agent paradigms, discusses limitations of current evaluation benchmarks, and proposes a holistic evaluation framework that balances task effectiveness, efficiency, robustness, and safety. Applications across enterprise, personal assistance, and specialized domains are analyzed, with insights into future research directions for more resilient and adaptive AI agent systems.

---

## From Control to Foresight: Simulation as a New Paradigm for Human-Agent Collaboration

**Authors:** Gaole He, Brian Y. Lim

**Published:** 2026-03-12T08:42:33Z

**Categories:** cs.HC, cs.AI, cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2603.11677v1) | [PDF](https://arxiv.org/pdf/2603.11677v1)

**Abstract:**
Large Language Models (LLMs) are increasingly used to power autonomous agents for complex, multi-step tasks. However, human-agent interaction remains pointwise and reactive: users approve or correct individual actions to mitigate immediate risks, without visibility into subsequent consequences. This forces users to mentally simulate long-term effects, a cognitively demanding and often inaccurate process. Users have control over individual steps but lack the foresight to make informed decisions. We argue that effective collaboration requires foresight, not just control. We propose simulation-in-the-loop, an interaction paradigm that enables users and agents to explore simulated future trajectories before committing to decisions. Simulation transforms intervention from reactive guesswork into informed exploration, while helping users discover latent constraints and preferences along the way. This perspective paper characterizes the limitations of current paradigms, introduces a conceptual framework for simulation-based collaboration, and illustrates its potential through concrete human-agent collaboration scenarios.

---

## LLMs Plagiarize: Ensuring Responsible Sourcing of Large Language Model Training Data Through Knowledge Graph Comparison

**Authors:** Devam Mondal, Carlo Lipizzi

**Published:** 2024-07-02T20:49:21Z

**Categories:** cs.CL, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2407.02659v2) | [PDF](https://arxiv.org/pdf/2407.02659v2)

**Abstract:**
In light of recent legal allegations brought by publishers, newspapers, and other creators of copyrighted corpora against large language model developers who use their copyrighted materials for training or fine-tuning purposes, we propose a novel system, a variant of a plagiarism detection system, that assesses whether a knowledge source has been used in the training or fine-tuning of a large language model. Unlike current methods, we utilize an approach that uses Resource Description Framework (RDF) triples to create knowledge graphs from both a source document and an LLM continuation of that document. These graphs are then analyzed with respect to content using cosine similarity and with respect to structure using a normalized version of graph edit distance that shows the degree of isomorphism. Unlike traditional plagiarism systems that focus on content matching and keyword identification between a source and a target corpus, our approach enables a broader and more accurate evaluation of similarity between a source document and LLM continuation by focusing on relationships between ideas and their organization with regards to others. Additionally, our approach does not require access to LLM metrics like perplexity that may be unavailable in closed large language model "black-box" systems, as well as the training corpus. We thus assess whether an LLM has "plagiarized" a corpus in its continuation through similarity measures. A prototype of our system will be found on a hyperlinked GitHub repository.

---

## VQ-Jarvis: Retrieval-Augmented Video Restoration Agent with Sharp Vision and Fast Thought

**Authors:** Xuanyu Zhang, Weiqi Li, Qunliang Xing, Jingfen Xie, Bin Chen, Junlin Li, Li Zhang, Jian Zhang, Shijie Zhao

**Published:** 2026-03-24T09:40:50Z

**Categories:** cs.CV

**Links:** [Abstract](https://arxiv.org/abs/2603.22998v1) | [PDF](https://arxiv.org/pdf/2603.22998v1)

**Abstract:**
Video restoration in real-world scenarios is challenged by heterogeneous degradations, where static architectures and fixed inference pipelines often fail to generalize. Recent agent-based approaches offer dynamic decision making, yet existing video restoration agents remain limited by insufficient quality perception and inefficient search strategies. We propose VQ-Jarvis, a retrieval-augmented, all-in-one intelligent video restoration agent with sharper vision and faster thought. VQ-Jarvis is designed to accurately perceive degradations and subtle differences among paired restoration results, while efficiently discovering optimal restoration trajectories. To enable sharp vision, we construct VSR-Compare, the first large-scale video paired enhancement dataset with 20K comparison pairs covering 7 degradation types, 11 enhancement operators, and diverse content domains. Based on this dataset, we train a multiple operator judge model and a degradation perception model to guide agent decisions. To achieve fast thought, we introduce a hierarchical operator scheduling strategy that adapts to video difficulty: for easy cases, optimal restoration trajectories are retrieved in a one-step manner from a retrieval-augmented generation (RAG) library; for harder cases, a step-by-step greedy search is performed to balance efficiency and accuracy. Extensive experiments demonstrate that VQ-Jarvis consistently outperforms existing methods on complex degraded videos.

---

## Adaptation of Embedding Models to Financial Filings via LLM Distillation

**Authors:** Eliot Brenner, Dominic Seyler, Manjunath Hegde, Andrei Simion, Koustuv Dasgupta, Bing Xiang

**Published:** 2025-12-08T22:43:14Z

**Categories:** cs.CL

**Links:** [Abstract](https://arxiv.org/abs/2512.08088v1) | [PDF](https://arxiv.org/pdf/2512.08088v1)

**Abstract:**
Despite advances in generative large language models (LLMs), practical application of specialized conversational AI agents remains constrained by computation costs, latency requirements, and the need for precise domain-specific relevance measures. While existing embedding models address the first two constraints, they underperform on information retrieval in specialized domains like finance. This paper introduces a scalable pipeline that trains specialized models from an unlabeled corpus using a general purpose retrieval embedding model as foundation. Our method yields an average of 27.7% improvement in MRR$\texttt{@}$5, 44.6% improvement in mean DCG$\texttt{@}$5 across 14 financial filing types measured over 21,800 query-document pairs, and improved NDCG on 3 of 4 document classes in FinanceBench. We adapt retrieval embeddings (bi-encoder) for RAG, not LLM generators, using LLM-judged relevance to distill domain knowledge into a compact retriever. There are prior works which pair synthetically generated queries with real passages to directly fine-tune the retrieval model. Our pipeline differs from these by introducing interaction between student and teacher models that interleaves retrieval-based mining of hard positive/negative examples from the unlabeled corpus with iterative retraining of the student model's weights using these examples. Each retrieval iteration uses the refined student model to mine the corpus for progressively harder training examples for the subsequent training iteration. The methodology provides a cost-effective solution to bridging the gap between general-purpose models and specialized domains without requiring labor-intensive human annotation.

---

## C2HLSC: Can LLMs Bridge the Software-to-Hardware Design Gap?

**Authors:** Luca Collini, Siddharth Garg, Ramesh Karri

**Published:** 2024-06-13T15:33:54Z

**Categories:** cs.AR

**Links:** [Abstract](https://arxiv.org/abs/2406.09233v1) | [PDF](https://arxiv.org/pdf/2406.09233v1)

**Abstract:**
High Level Synthesis (HLS) tools offer rapid hardware design from C code, but their compatibility is limited by code constructs. This paper investigates Large Language Models (LLMs) for refactoring C code into HLS-compatible formats. We present several case studies by using an LLM to rewrite C code for NIST 800-22 randomness tests, a QuickSort algorithm and AES-128 into HLS-synthesizable c. The LLM iteratively transforms the C code guided by user prompts, implementing functions like streaming data and hardware-specific signals. This evaluation demonstrates the LLM's potential to assist hardware design refactoring regular C code into HLS synthesizable C code.

---

## LLM-based Multi-Agent Reinforcement Learning: Current and Future Directions

**Authors:** Chuanneng Sun, Songjun Huang, Dario Pompili

**Published:** 2024-05-17T22:10:23Z

**Categories:** cs.MA, cs.AI, cs.CL, cs.LG, cs.RO

**Links:** [Abstract](https://arxiv.org/abs/2405.11106v1) | [PDF](https://arxiv.org/pdf/2405.11106v1)

**Abstract:**
In recent years, Large Language Models (LLMs) have shown great abilities in various tasks, including question answering, arithmetic problem solving, and poem writing, among others. Although research on LLM-as-an-agent has shown that LLM can be applied to Reinforcement Learning (RL) and achieve decent results, the extension of LLM-based RL to Multi-Agent System (MAS) is not trivial, as many aspects, such as coordination and communication between agents, are not considered in the RL frameworks of a single agent. To inspire more research on LLM-based MARL, in this letter, we survey the existing LLM-based single-agent and multi-agent RL frameworks and provide potential research directions for future research. In particular, we focus on the cooperative tasks of multiple agents with a common goal and communication among them. We also consider human-in/on-the-loop scenarios enabled by the language component in the framework.

---

## Demonstration-Free Robotic Control via LLM Agents

**Authors:** Brian Y. Tsui, Alan Y. Fang, Tiffany J. Hwu

**Published:** 2026-01-28T07:49:35Z

**Categories:** cs.RO, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2601.20334v1) | [PDF](https://arxiv.org/pdf/2601.20334v1)

**Abstract:**
Robotic manipulation has increasingly adopted vision-language-action (VLA) models, which achieve strong performance but typically require task-specific demonstrations and fine-tuning, and often generalize poorly under domain shift. We investigate whether general-purpose large language model (LLM) agent frameworks, originally developed for software engineering, can serve as an alternative control paradigm for embodied manipulation. We introduce FAEA (Frontier Agent as Embodied Agent), which applies an LLM agent framework directly to embodied manipulation without modification. Using the same iterative reasoning that enables software agents to debug code, FAEA enables embodied agents to reason through manipulation strategies. We evaluate an unmodified frontier agent, Claude Agent SDK, across the LIBERO, ManiSkill3, and MetaWorld benchmarks. With privileged environment state access, FAEA achieves success rates of 84.9%, 85.7%, and 96%, respectively. This level of task success approaches that of VLA models trained with less than 100 demonstrations per task, without requiring demonstrations or fine-tuning. With one round of human feedback as an optional optimization, performance increases to 88.2% on LIBERO. This demonstration-free capability has immediate practical value: FAEA can autonomously explore novel scenarios in simulation and generate successful trajectories for training data augmentation in embodied learning. Our results indicate that general-purpose agents are sufficient for a class of manipulation tasks dominated by deliberative, task-level planning. This opens a path for robotics systems to leverage actively maintained agent infrastructure and benefit directly from ongoing advances in frontier models. Code is available at https://github.com/robiemusketeer/faea-sim

---

## Constitutional Black-Box Monitoring for Scheming in LLM Agents

**Authors:** Simon Storf, Rich Barton-Cooper, James Peters-Gill, Marius Hobbhahn

**Published:** 2026-02-28T22:31:32Z

**Categories:** cs.CL, cs.AI, cs.LG

**Links:** [Abstract](https://arxiv.org/abs/2603.00829v1) | [PDF](https://arxiv.org/pdf/2603.00829v1)

**Abstract:**
Safe deployment of Large Language Model (LLM) agents in autonomous settings requires reliable oversight mechanisms. A central challenge is detecting scheming, where agents covertly pursue misaligned goals. One approach to mitigating such risks is LLM-based monitoring: using language models to examine agent behaviors for suspicious actions. We study constitutional black-box monitors: prompted classifiers that detect scheming using only externally observable inputs and outputs, optimized on synthetic data generated from natural-language behavior specifications. We introduce two pipelines for generating synthetic agent trajectories, STRIDE (iterative refinement) and Gloom (agent-environment simulation), from which we generate 1,000 samples each. We optimize frontier LLM monitors on these datasets via prompt sweeps, human refinement, and automated prompt optimization, and evaluate performance on 7,500 held-out trajectories from ControlArena, a suite of grounded environments where agents operate in more realistic contexts. Our results demonstrate that monitors selected purely on synthetic data can generalize to more realistic environments, capturing a meaningful scheming signal. However, we find that performance saturates quickly in our setting, with simple prompt sweeps matching the results of more extensive optimization. Pushing beyond this limit yields no further improvements and instead leads to overfitting.

---

## LLM Agents Making Agent Tools

**Authors:** Georg Wölflein, Dyke Ferber, Daniel Truhn, Ognjen Arandjelović, Jakob Nikolas Kather

**Published:** 2025-02-17T11:44:11Z

**Categories:** cs.CL, cs.AI, cs.LG, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2502.11705v2) | [PDF](https://arxiv.org/pdf/2502.11705v2)

**Abstract:**
Tool use has turned large language models (LLMs) into powerful agents that can perform complex multi-step tasks by dynamically utilising external software components. However, these tools must be implemented in advance by human developers, hindering the applicability of LLM agents in domains demanding large numbers of highly specialised tools, like in life sciences and medicine. Motivated by the growing trend of scientific studies accompanied by public code repositories, we propose ToolMaker, an agentic framework that autonomously transforms papers with code into LLM-compatible tools. Given a GitHub URL and short task description, ToolMaker autonomously installs dependencies and generates code to perform the task, using a closed-loop self-correction mechanism for debugging. To evaluate our approach, we introduce a benchmark comprising 15 complex computational tasks spanning various domains with over 100 unit tests to assess correctness and robustness. Our method correctly implements 80% of the tasks, substantially outperforming current state-of-the-art software engineering agents. ToolMaker therefore is a step towards fully autonomous agent-based scientific workflows. Our code and benchmark are publicly available at https://github.com/KatherLab/ToolMaker.

---

## A Concurrent Modular Agent: Framework for Autonomous LLM Agents

**Authors:** Norihiro Maruyama, Takahide Yoshida, Hiroki Sato, Atsushi Masumori, Johnsmith, Takashi Ikegami

**Published:** 2025-08-26T13:58:31Z

**Categories:** cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2508.19042v1) | [PDF](https://arxiv.org/pdf/2508.19042v1)

**Abstract:**
We introduce the Concurrent Modular Agent (CMA), a framework that orchestrates multiple Large-Language-Model (LLM)-based modules that operate fully asynchronously yet maintain a coherent and fault-tolerant behavioral loop. This framework addresses long-standing difficulties in agent architectures by letting intention emerge from language-mediated interactions among autonomous processes. This approach enables flexible, adaptive, and context-dependent behavior through the combination of concurrently executed modules that offload reasoning to an LLM, inter-module communication, and a single shared global state.We consider this approach to be a practical realization of Minsky's Society of Mind theory. We demonstrate the viability of our system through two practical use-case studies. The emergent properties observed in our system suggest that complex cognitive phenomena like self-awareness may indeed arise from the organized interaction of simpler processes, supporting Minsky-Society of Mind concept and opening new avenues for artificial intelligence research. The source code for our work is available at: https://github.com/AlternativeMachine/concurrent-modular-agent.

---

## LLM-based Few-Shot Early Rumor Detection with Imitation Agent

**Authors:** Fengzhu Zeng, Qian Shao, Ling Cheng, Wei Gao, Shih-Fen Cheng, Jing Ma, Cheng Niu

**Published:** 2025-12-20T12:42:27Z

**Categories:** cs.CL, cs.AI

**Links:** [Abstract](https://arxiv.org/abs/2512.18352v2) | [PDF](https://arxiv.org/pdf/2512.18352v2)

**Abstract:**
Early Rumor Detection (EARD) aims to identify the earliest point at which a claim can be accurately classified based on a sequence of social media posts. This is especially challenging in data-scarce settings. While Large Language Models (LLMs) perform well in few-shot NLP tasks, they are not well-suited for time-series data and are computationally expensive for both training and inference. In this work, we propose a novel EARD framework that combines an autonomous agent and an LLM-based detection model, where the agent acts as a reliable decision-maker for \textit{early time point determination}, while the LLM serves as a powerful \textit{rumor detector}. This approach offers the first solution for few-shot EARD, necessitating only the training of a lightweight agent and allowing the LLM to remain training-free. Extensive experiments on four real-world datasets show our approach boosts performance across LLMs and surpasses existing EARD methods in accuracy and earliness.

---

## Large Language Model based Multi-Agents: A Survey of Progress and Challenges

**Authors:** Taicheng Guo, Xiuying Chen, Yaqi Wang, Ruidi Chang, Shichao Pei, Nitesh V. Chawla, Olaf Wiest, Xiangliang Zhang

**Published:** 2024-01-21T23:36:14Z

**Categories:** cs.CL, cs.AI, cs.MA

**Links:** [Abstract](https://arxiv.org/abs/2402.01680v2) | [PDF](https://arxiv.org/pdf/2402.01680v2)

**Abstract:**
Large Language Models (LLMs) have achieved remarkable success across a wide array of tasks. Due to the impressive planning and reasoning abilities of LLMs, they have been used as autonomous agents to do many tasks automatically. Recently, based on the development of using one LLM as a single planning or decision-making agent, LLM-based multi-agent systems have achieved considerable progress in complex problem-solving and world simulation. To provide the community with an overview of this dynamic field, we present this survey to offer an in-depth discussion on the essential aspects of multi-agent systems based on LLMs, as well as the challenges. Our goal is for readers to gain substantial insights on the following questions: What domains and environments do LLM-based multi-agents simulate? How are these agents profiled and how do they communicate? What mechanisms contribute to the growth of agents' capacities? For those interested in delving into this field of study, we also summarize the commonly used datasets or benchmarks for them to have convenient access. To keep researchers updated on the latest studies, we maintain an open-source GitHub repository, dedicated to outlining the research on LLM-based multi-agent systems.

---

