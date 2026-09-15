# Introduction 文献与大纲讨论笔记（2026-09-14）

本笔记用于讨论论证结构，不代表已完成云端案例或比较实验。`outline.md`、`main.tex` 暂不修改。

## 与本文最相关的原始工作

| 工作 | 论文实际做了什么 | 对本文定位的影响 |
|---|---|---|
| [AutoBA, *Advanced Science* (2024)](https://doi.org/10.1002/advs.202407094) | 根据少量用户输入生成多组学分析计划、代码并执行，带自动代码修复；案例涉及多种组学。 | 不能笼统说“生信智能体只能讨论工具”或“无法执行端到端分析”。需说明本文关注的微生物组工作负载和运行机制。 |
| [Biomni, 原始论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC12157518/) | 通用生物医学智能体，检索工具、规划和执行；其微生物组评估让智能体与专家对五组已有丰度表/元数据做差异丰度分析。 | 不能说此前智能体没有微生物组分析；可区分“已有表格的下游分析”与“从原始 reads 到多个可检查产物”，但必须按实际案例证明。 |
| [BioAgents, *Scientific Reports* (2025)](https://www.nature.com/articles/s41598-025-25919-z) | 基于小模型、微调与 RAG 的多智能体生信方案。 | Related work 应谈真实的生物智能体系统，而非泛称 domain GPT wrappers。 |
| [MetaClaw, bioRxiv v2 预印本 (2026)](https://www.biorxiv.org/content/10.64898/2026.07.21.739769v2)；[实现说明](https://github.com/BGI-AI-models/MetaClaw) | 同样建立在 OpenClaw 上，使用每作业目录、skills、registry；云端 FlowHub 负责确定性上游流程，本地容器负责可组合下游。仓库有 16S/ITS amplicon 流程，v2 报告四个 shotgun 队列（共 769 个 profile）及扰动/消融。[v1](https://www.biorxiv.org/content/10.64898/2026.07.21.739769v1.full) 明确说其功能分析、组装、amplicon 等能力未在所报告的案例复现中评估；v2 的评估边界需再次逐节核对。 | **最接近的对照**。不能把 OpenClaw、skills、job bundle、16S+shotgun 覆盖或消融实验本身写成本文独有。若本文的差异是本地主机 conda、agent 逐步驱动原始工具、MAG 实际完成，应在 Methods 与实证中逐项证明，并说明与 MetaClaw 的关系。预印本版本在变，投稿前需重新核对。 |
| [BixBench (2025)](https://arxiv.org/abs/2503.00096)、[BioAgent Bench (2026)](https://arxiv.org/abs/2601.21800)、[BixBench3 (2026)](https://arxiv.org/abs/2608.25286) | 从数据分析问答、端到端产物检查，发展到从原始数据复现研究级产物；BioAgent Bench 还测受扰动输入。 | 评估不应只看对话或命令是否退出 0。应预先定义输入、期望产物、关键数值/统计方向、重试/人工介入、成本/耗时和扰动条件。不能声称“其他智能体不能做长任务”：BixBench3 已实测数小时运行。 |

## 对现大纲的判断

1. **研究空白定得过宽。** `outline.md` 中“LLM agents can talk but cannot finish”“none of these give one agent ...”不符合上述文献；尤其 MetaClaw 已具备相近系统部件与跨分析类型能力。
2. **分析家族更适合作为评估范围，不宜单独作为创新点。** 三个 case 能展示广度，但如果没有正确性、端到端产物与运行可靠性的度量，只是示范；也不能由三例推断一般性的可靠性。
3. **系统主张应更具体。** 当前源码能支持的候选主张是：OpenClaw agent 直接按 step skill 调用宿主 conda 工具；运行时与参考库由 registry 解析；稳定 session key 绑定 job；长执行进程通过唤醒继续。它与 MetaClaw 的固定 FlowHub 上游/容器下游分工不同，但“更灵活/更可靠/更可复现”均需比较证据。
4. **结果尚不应预设方向。** `outline.md` 的“ablation show ... necessary”“hallucinated paths prevented”都先写了结论。应改为中性的预注册问题，例如移除组件后完成率、错误率、介入次数如何变化。
5. **Introduction 的 Related work 应重排。** 目前三个传统工具家族占主导，真正的相邻领域生物智能体只有一小段。对于软件/智能体论文，更自然的顺序是：微生物组任务异质性 → 现有生物智能体与证据 → 微生物组近邻 MetaClaw → 本文解决的问题与意义 → 本文贡献及支撑证据。传统工具与工作流管理器压缩为背景，并避免贬低其已有能力。

## MetaClaw Introduction 的论证方法

MetaClaw 的 Introduction 不是从功能列表开始，而是逐层收窄问题：

1. 原始组学数据到生物学结论需要一连串相互依赖的决策；工作流系统降低工程负担，但研究者仍需选择和解释。
2. AutoBA、Biomni 等智能体已经证明规划和执行可行，同时指出多步推理、可复现性和生物学依据仍有挑战。
3. 它把缺口明确限定为：现有评估是否能证明智能体复现完整研究的主要生物学结论，而非只生成合理流程或成功退出。
4. 它进一步说明宏基因组数据规模、异质性和隐私性为什么让这个缺口重要。
5. 最后用“需要的不是另一条宏基因组流程，而是可审计的执行范式”凝练意义，再列出系统和评估贡献。

MicroBioAgent 不应复制其“结论级复现”主线。适合本文的对应主线是：**需要的不是另一条固定微生物组流程，而是一层可适应研究问题的执行层；它在步骤层面保持规范，在研究层面动态组合流程，同时让原始测序计算留在本地，并在长任务运行期间保留人的控制。** 这直接回答本文为何有意义：研究者不必先把每项研究编码成完整 DAG，仍能从 reads 推进到可检查的上下游产物；当中间结果或研究重点变化时，也可修订未执行的分析，而不必等待整个长流程结束。

## “降低分析门槛”的文献依据与表述

- [GenePiper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6940285/) 明确指出，许多微生物组工具依赖命令行，对一般用户学习曲线陡峭，且多来源依赖与兼容性增加安装维护难度；在线服务还面临大数据传输和安全问题。
- [Explicet](https://academic.oup.com/bioinformatics/article/29/23/3100/246994) 指出，即使完成基本微生物组分析也常要求一定的计算机技能。
- [微生物组实用分析指南](https://pmc.ncbi.nlm.nih.gov/articles/PMC8106563/) 指出，快速增加的软件和流程使缺少生物信息学背景的研究者难以选择合适方法。
- [微生物组机器学习工具综述](https://pmc.ncbi.nlm.nih.gov/articles/PMC10704913/) 将相关工具描述为分散在不同仓库与文献中，完整分析常需把多个方法组合成数据科学工作流。

因此 Introduction 可以明确提出：微生物组分析门槛来自**计算操作与生物学判断的叠加**，包括软件安装、命令行/编程、格式和数据库衔接、方法选择以及结果整合。MicroBioAgent 通过自然语言目标、步骤选择与执行、环境/数据库解析、产物检查和结果组织来降低其中的**计算与操作门槛**。在没有用户研究或对照实验前，避免把 “greatly lowers the barrier” 写成定量结论；可以写成 “is designed to lower the computational and operational barrier” 或具体说明它减少了哪些前置工作。

## 建议的 Introduction 五段骨架

1. **任务背景**：微生物组研究依据 assay 与科学问题在 amplicon、read-based shotgun、MAG 路径间选择；任务的难点是把科学问题贯穿到异质的分析阶段和产物。
2. **现有计算方案**：成熟工具解决单项分析，工作流系统可靠执行预先定义的路径；其边界是完整研究路径需要预先选定和编码。
3. **智能体进展与近邻**：AutoBA、Biomni、BioAgents 已展示规划和执行；MetaClaw 通过注册的 FlowHub 上游流程与本地下游 skills 完成可审计宏基因组研究复现。由此把本文问题收窄到不依赖固定完整流程的本地、动态和长任务可交互执行。
4. **意义与所需范式**：需要的是在步骤层保持规范、在研究层按目标和中间结果组合流程的执行层。它让研究者无需先写完整 DAG，允许 reads 留在本地，并能在长分析过程中修改后续决策。
5. **本文贡献**：MicroBioAgent 的全流程覆盖、步骤级动态组合、本地执行和长任务中途反馈四项贡献；三类 case 用于展示实际覆盖范围。

## 需要先确认的策略问题

- 作者已确认本项目与 BGI MetaClaw 独立开发。论文仍需引用该近邻工作，并明确区分本地逐步执行与其 FlowHub 上游/容器下游架构；在有证据前不宣称优越性。
- 云端三例是否都从 raw reads 开始，且 Case 1 的 MetaPhlAn、Case 2 的 HUMAnN/分类器、Case 3 的 MAG 组装与恢复确实由 agent 跑完？如果有人工补跑，需据实定义“端到端”。
- 是否能做可比基线（如同模型无 skills/registry、固定 workflow、或 MetaClaw 可用配置）？若不行，主张应定位为系统实现与案例可行性，而不是相对优越性。
