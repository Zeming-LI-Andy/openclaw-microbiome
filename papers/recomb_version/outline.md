# MicroBioAgent：RECOMB 2027 会议版段落大纲

本文件是结构设计稿，不是完成的投稿论文。基于 `../main.tex` 当前内容重构；原稿未改动。中文核心句说明每个自然段的唯一任务；对应英文主题句同步写入 `main.tex`，便于随后逐段扩写。数值是原稿报告值，本轮未重跑实验或独立核验全部原始日志。

## 1. 建议定位与总论点

**暂定题目：MicroBioAgent: An AI Agent for Study-Specific Microbiome Analysis**

**核心研究问题：如何根据研究者的目标与测序数据，组织并执行从序列处理到群落比较、功能分析和基因组重建的微生物组分析？**

核心论点：MicroBioAgent 将微生物组领域技能、软件环境与参考数据库连接起来，根据研究目标组合并执行分析步骤，覆盖 16S 扩增子、参考数据库驱动的 shotgun 分析和组装驱动的基因组分析，并衔接下游统计、功能注释与结果展示。

文章首先回答系统能开展哪些微生物组分析、产出哪些有生物学意义的结果，以及这些分析在不同模型和提示词下的完成情况与输出表现。三类案例是主要分析能力证据；稳健性实验检验重复运行表现；异步执行与研究者反馈用于说明长时间计算中的运行支持能力。

表述边界：不将系统定位为自主发现科学或分析问题并进行纠正的系统；不以自主诊断、自我纠错或自主修订作为核心贡献。执行状态与文件检查属于操作流程，不能等同于科学判断。方法变更明确归属于研究者指令，例如番茄案例中的 MetaPhlAn 版本切换。现有输出错误仍如实作为局限报告。

### 方法命名层级

- 框架层：**study-specific microbiome analysis**（面向研究目标的微生物组分析）。
- 方法组件：**event-driven execution coordination**（事件驱动的执行协调）；功能小节可用 **Asynchronous human guidance and automatic continuation**。
- 实现层：**a version-pinned extension to the OpenClaw runtime**；首次交代“distributed as a patch set”，补丁编号和应用方式放 Appendix A.1。
- 消融条件：叙事使用 **full system / without asynchronous coordination**；明确后者按实现移除了整套运行时扩展。保留原日志键 `full` / `no-patch` 做映射，不更改原数据标签，不称其为严格的单一机制消融。

“patch”准确描述交付形式，但不宜作为核心方法的名称；“runtime extension”也不代表独立的新调度器。方法名称必须落到已有的让出回合、完成事件路由与会话恢复行为。

## 2. RECOMB 2027 规则与版面预算

核查日期：2026-10-29。官方来源：[Call for Papers](https://recomb.org/recomb2027/call_for_papers)、[Key dates](https://recomb.org/recomb2027/keydates_and_deadlines.html)。

- Letter 纸张、1 inch 页边距、字体至少 10 pt；正文上限 10 页，含图、表和图注；参考文献不计入。
- 可另加含题目、作者与摘要的标题页；无强制专用模板，故骨架采用 article，不能直接套用默认页边距不合规的 LNCS。
- 单盲审稿；保留原稿作者及单位。附录不限页，但正文必须自洽，不能依赖审稿人阅读附录才能判断核心结论。
- 新软件/方法须在截止前提供公开且有充分 README 的源码链接；骨架沿用原稿仓库地址，尚未验证公开访问。
- 官方强调实质性计算或方法贡献；仅应用现有方法或组装流程不符合其重点，agentic workflows 也需满足这一要求。
- 摘要登记截止为 2026-10-28 23:59 AoE，即香港时间 2026-10-29 19:59；全文更新截止为 2026-11-04 23:59 AoE，即香港时间 2026-11-05 19:59。全文阶段仅允许已有登记更新，且题目、作者、摘要应与登记内容保持实质一致。此处题目为建议，未知是否已有登记，不代表可任意更改登记。

| 内容 | 建议正文页数（含相应图表） | 目的 |
|---|---:|---|
| Introduction | 1.25 | 明确计算问题、文献位置与贡献 |
| Problem formulation | 0.50 | 定义任务和可观察的成功标准 |
| Method | 2.25 | 分析能力、技能与资源组织、执行及交互支持 |
| Experimental design | 1.00 | 评测条件、公平比较与评分口径 |
| Results | 3.50 | 先分析案例，再稳健性，最后运行协调消融与交互 |
| Discussion | 0.75 | 贡献解释与实质限制 |
| Conclusion | 0.25 | 一段收束 |
| Code and data availability | 0.10 | 数据、源码与复现入口 |
| 余量 | 0.40 | 控制浮动、标题与分页 |

以上是扩写后 10 页正文的分配目标，不是当前骨架的页数。摘要独占额外标题页；参考文献从正文后另页开始，附录另起部分。

## 3. 逐自然段设计（33 段）

标签含义：A 摘要；I 引言；P 问题；M 方法；E 实验设计；R 结果；D 讨论；C 结论；V 可用性。英文句子是扩写锚点，不能直接当作完整段落投稿。

### Abstract｜摘要

**A1｜核心句：MicroBioAgent 根据研究目标组合并执行微生物组分析步骤，覆盖 16S 扩增子、参考驱动的 shotgun 分析和组装驱动的基因组分析，并通过三类案例、跨模型与提示词测试及运行消融评价分析能力、稳健性和执行支持。**

英文主题句：MicroBioAgent composes and executes study-specific microbiome analyses across 16S amplicon, reference-based shotgun, and assembly-based workflows, evaluated through case studies, model--prompt robustness tests, and execution ablations.

证据与扩写边界：原稿 abstract、sec:robustness、tab:e2e-ablation、tab:hitl-ablation；最终摘要写成一个自然段，依次放问题、方法、关键结果和适用边界，约 180–220 词；先概括三类分析能力与代表性生物学结果，再简述稳健性和运行支持；token 数值不取代分析结果成为摘要主线。

### Introduction｜引言

**I1｜核心句：微生物组研究需要将测序数据处理、物种和功能解析与下游统计连接起来，而工具选择、软件环境及参考数据库配置增加了开展完整分析的难度。**

英文主题句：Microbiome studies connect sequencing-data processing with taxonomic and functional characterization and downstream statistics, requiring researchers to select tools and configure software and reference resources.

证据与扩写边界：原稿 Introduction 第 1–2 段；压缩生物学背景，快速引出计算问题。

**I2｜核心句：工作流管理器和生物医学智能体为分析自动化提供了基础，本文关注如何将这些执行能力与微生物组领域方法结合，支持不同研究目标下的完整分析。**

英文主题句：Workflow managers and biomedical agents provide foundations for analysis automation, motivating their integration with microbiome-specific methods to support diverse study objectives.

证据与扩写边界：原稿 Introduction 第 2–3 段；保留 Snakemake、Nextflow、AutoBA、Biomni 等必要定位；不能笼统声称现有系统没有异步能力。

**I3｜核心句：针对微生物组分析，本文关注在用户计算环境中组合上游处理与下游分析步骤，以支持不同数据类型和研究问题。**

英文主题句：For microbiome research, this study focuses on composing upstream processing and downstream analyses in user-controlled computing environments across data types and study objectives.

证据与扩写边界：原稿 Introduction MetaClaw 段及 tab:agent-capabilities；对照表是文献层面的功能比较，不能写成同条件性能排名；具体竞争系统描述待原始论文逐项复核。

**I4｜核心句：本文研究如何将研究者提出的微生物组问题和输入数据转化为覆盖序列处理、群落与功能比较以及基因组重建的可执行分析。**

英文主题句：We investigate how microbiome research objectives and input data can be translated into executable analyses spanning sequence processing, community and functional comparisons, and genome reconstruction.

证据与扩写边界：原稿 Introduction、sec:analysis-planning 与 sec:asynchronous-execution；研究问题围绕微生物组分析能力；异步协调用于支持分析执行；不主张自主纠错或预设整体优于所有基线。

**I5｜核心句：MicroBioAgent 将领域技能、运行环境和参考资源结合，以三类案例验证微生物组分析能力，并以重复会话及运行消融评价稳健性和长时间计算支持。**

英文主题句：MicroBioAgent integrates domain skills, execution environments, and reference resources, with three case studies evaluating microbiome analysis capabilities and additional experiments assessing robustness and execution support.

证据与扩写边界：原稿 Introduction 末段；贡献表述限为方法设计、受控运行证据、分析能力验证；不声称发明新的生物信息学算法。

### Problem formulation｜问题定义

**P1｜核心句：给定研究目标、测序数据和样本信息，系统需要选择并连接相应分析步骤，生成所需的定量结果、图表和分析记录。**

英文主题句：Given a study objective, sequencing data, and sample metadata, the system selects and connects analytical steps to produce quantitative results, figures, and analysis records.

证据与扩写边界：原稿 sec:analysis-planning 与三案例 Methods；明确输入、任务及输出即可，不为提高形式感额外构造优化问题。

**P2｜核心句：评价以分析任务完成情况和产出结果为核心，同时考察不同模型与提示词下的表现，以及长时间计算中的执行开销和研究者交互。**

英文主题句：Evaluation centers on analytical task completion and outputs, with further assessment of model--prompt robustness, execution overhead, and researcher interaction during computation.

证据与扩写边界：原稿各实验的评分定义；任务产物、科学有效性和交互行为分别评价；输出文件存在不能视为科学正确性证明。

### Method｜方法

**M1｜核心句：MicroBioAgent 将微生物组领域技能与本地工具和参考资源连接，支持从上游测序处理到下游群落、功能和基因组分析的步骤组合。**

英文主题句：MicroBioAgent connects microbiome domain skills with local tools and reference resources to compose workflows from sequencing-data processing to community, functional, and genome-resolved analyses.

证据与扩写边界：原稿 sec:system-overview、sec:analysis-planning；Figure 1 架构总览；运行主体是 OpenClaw，插件不是自建调度引擎。

**M2｜核心句：正常提供会话标识时，mgx_create_job 将会话绑定到可复用的分析目录，使跨步骤输入、结果、脚本和日志保持可追溯的归属。**

英文主题句：With a session identifier, mgx_create_job binds a conversation to a reusable job directory that organizes inputs, outputs, scripts, and logs across analytical steps.

证据与扩写边界：原稿 sec:analysis-planning；src/runtime/job.ts；不把日志保存等同于自动完整审计或确定性复现。

**M3｜核心句：分析技能提供方法步骤与预期产物，运行环境和参考数据库注册表提供实际资源位置，使智能体能够按研究问题组合工具而无需预先登记完整端到端流程。**

英文主题句：Method-specific skills guide analytical steps, while runtime and reference registries resolve the resources needed to compose study-specific analyses.

证据与扩写边界：原稿 sec:skills-execution；不把 Markdown 指南包装成机器强制验证的输入输出契约；能力全集移附录。

**M4｜核心句：系统依据分析目标和领域技能选择工具与参数，通过命令与脚本执行各步骤，并记录执行状态、日志和生成文件，供研究者检查分析过程。**

英文主题句：The system selects tools and parameters from the study objective and domain skills, executes analytical commands and scripts, and records execution status, logs, and generated files for researcher inspection.

证据与扩写边界：原稿 sec:analysis-planning；说明命令执行与记录方式，检查文件存在不代表系统能够自主发现和纠正分析问题。

**M5｜核心句：长命令在初始等待窗口后继续后台执行，智能体通过让出会话回合等待完成事件，使计算继续运行时仍可接收用户对待执行计划的修改。**

英文主题句：Commands that outlast the initial wait continue in the background while the agent yields its turn, allowing user feedback to revise pending analyses during computation.

证据与扩写边界：原稿 sec:asynchronous-execution；exec 的 yieldMs=30000、timeout=0 与 sessions_yield；Figure 2 执行时序。

**M6｜核心句：事件驱动的执行协调将后台完成事件送回原会话，并根据会话活跃状态安排事件处理与后续激活，使智能体能够检查已完成命令并继续分析。**

英文主题句：Event-driven execution coordination routes completion events to the originating session and arranges their processing according to active-run state so that the agent can inspect outputs and continue analysis.

证据与扩写边界：原稿 sec:asynchronous-execution；补丁 manifest.json 和 README 的 0001–0005；最终方法须与 streaming 状态处理对齐，不简单写成所有事件都直接 steer 或全部排队。

**M7｜核心句：分析步骤生成丰度表、多样性与差异分析结果、分类模型或基因组注释等产物，并通过图表和报告呈现研究目标所需的结果。**

英文主题句：Analytical steps produce abundance profiles, diversity and differential-abundance results, classifiers, or genome annotations, with figures and reports presenting outputs relevant to the study objective.

证据与扩写边界：原稿分析能力表、三案例结果与报告能力；依实际任务说明输出，不将所有能力写成每个案例均已执行。

### Experimental design｜实验设计

#### Study-specific analytical capability

**E1｜核心句：三项公开研究的 230 个测序文库分别覆盖配对扩增子与短读长宏基因组、CRC 功能分类以及长读长基因组重建，用于测试分析任务覆盖及原研究关键模式的恢复。**

英文主题句：Three published datasets comprising 230 sequencing libraries assess paired amplicon and shotgun analysis, CRC functional classification, and long-read genome-resolved metagenomics.

证据与扩写边界：原稿 sec:case-design；Table 1 数据/任务/指标；60+36、128、6 是文库数，不能写成 230 个独立受试者；恢复原研究模式不等于精确计算复现。

#### Robustness across models and prompts

**E2｜核心句：稳健性实验在相同的预处理 Case 1 输入与资源配置上交叉三种模型和三档提示词，每种组合重复三次，以六项任务产物评价完成情况并比较可对齐的定量输出。**

英文主题句：The robustness experiment crosses three models and three prompt levels with three sessions per combination on shared preprocessed Case 1 inputs, assessing six output-defined tasks and comparable quantitative results.

证据与扩写边界：原稿 sec:reliability-experiments；27 会话、162 任务评估；shotgun 为清洗后 20% 读深输入；完成定义须进入正文，不仅放附录。

#### Execution coordination: overhead and completion

**E3｜核心句：运行协调消融固定模型、详细提示词、预处理输入、领域技能和运行资源，比较完整系统与移除异步协调扩展的系统，并记录输出、方法要求、调用和总 token。**

英文主题句：The execution-coordination ablation holds the model, prompt, inputs, skills, and resources constant while comparing the full system with the runtime extension removed, recording outputs, method adherence, calls, and total tokens.

证据与扩写边界：原稿消融 Methods、tab:e2e-ablation；每条件 3 次；总 token 为输入输出之和且包括 reasoning，不能当作唯一 token 数、实际费用或缓存后计费量；补丁同时改变工具指导与唤醒逻辑。

#### Guidance during active computation

**E4｜核心句：交互实验在确认 QIIME 2 分类进程仍运行时要求改用 DESeq2 并新增显著属热图，以运行中计划更新和完成后的无追加提示续跑作为两个独立成功标准。**

英文主题句：The interaction experiment requests DESeq2 and a significant-genus heatmap during active QIIME 2 classification, scoring mid-run plan revision and completion-triggered continuation separately.

证据与扩写边界：原稿 HITL Methods、tab:hitl-ablation；每条件 3 次；分钟级任务；与 I/O 归档完整性指标分开，保留事件时间线供复核。

### Results｜结果

#### Study-specific analytical capability

**R1｜核心句：番茄案例完成了扩增子与 shotgun 的跨模态分析，但第二个已报道物种标志物是在研究者要求切换至原研究所用 MetaPhlAn2 后才恢复，说明版本差异和人工反馈会改变结果恢复程度。**

英文主题句：The tomato reanalysis linked amplicon and shotgun results, while recovering the second reported species marker required investigator-guided reanalysis with the original MetaPhlAn2 version.

证据与扩写边界：原稿 sec:case-tomato；不写成全程无人干预或自动发现版本原因；完整多样性、属富集图移附录，正文 Figure 3a 保留与方法主线有关的版本分支。

**R2｜核心句：CRC 案例连接物种与功能分析及嵌套交叉验证分类，得到基因家族和 KO 模型 0.902 与 0.632 的 out-of-fold AUROC，展示从上游量化到下游建模的任务组合能力。**

英文主题句：The CRC analysis connected species and functional profiling to nested cross-validated classification, with pooled out-of-fold AUROCs of 0.902 for gene families and 0.632 for KO features.

证据与扩写边界：原稿 sec:case-crc；Figure 3b；结论是任务能力，不是新的诊断模型或临床验证；特征选择须确认在训练折内；没有外部验证时不声称临床可推广。

**R3｜核心句：环境案例从六个长读长文库中获得 75 个去冗余代表基因组并对焦点类群进行功能注释，支持系统覆盖基因组重建任务，但基因存在只能指示代谢潜力。**

英文主题句：The environmental analysis recovered 75 dereplicated representative genomes from six long-read libraries and annotated focal taxa, demonstrating genome-resolved analysis while limiting functional interpretation to genetic potential.

证据与扩写边界：原稿 sec:case-mag；Figure 3c；153 个合格 MAG 到 75 代表基因组、11 焦点 MAG 的细节放附录；不把烷烃代谢基因等同于实验证实聚乙烯降解。

#### Robustness across models and prompts

**R4｜核心句：跨模型与提示词的 27 次会话完成了 160/162 项任务评估，未完成的两项集中在同一会话遗漏 shotgun 分析，表明任务产物生成总体稳定但并非每次会话均完整。**

英文主题句：Across 27 model--prompt sessions, 160 of 162 task evaluations were completed, with both omissions arising from one session that skipped shotgun analysis.

证据与扩写边界：原稿 sec:robustness、fig:robustness-models；按现有六任务评分可推得完整会话 26/27，但最终稿需核对逐会话表后才新增该统计；不能将 98.8% 标为会话成功率或正确率。

**R5｜核心句：在原稿采用的可对齐条目与同方法子集中，多样性和差异丰度结果未检出若干比较间的分布差异，但这种结果尚不足以建立数值等价或生物标志物选择的一致性。**

英文主题句：Within the comparable entries and method-matched subsets analyzed in the source manuscript, diversity and differential-abundance distributions showed limited detected differences, without establishing numerical equivalence.

证据与扩写边界：原稿稳健性定量段、Methods 的条目筛选与平均规则；现有 MWU/Holm 结果可描述；共享输入、距离对不独立、先跨重复取平均及 ≥5% 丰度筛选均限制推断；建议补配对误差、效应方向或标志物重叠，均标为待分析。

**R6｜核心句：分类区域选择、特征标识对齐和 MetaPhlAn 归一化参数的变化导致部分丰度结果不一致，揭示任务完成率不能替代输出语义正确性与参数一致性的检查。**

英文主题句：Differences in amplicon-region selection, feature-identifier alignment, and MetaPhlAn normalization expose output-validity failures that task-completion counts alone do not capture.

证据与扩写边界：原稿稳健性失败原因段；Figure 4 可将完成热图与失效类型并列；没有逐类分母时不虚构错误率；这些限制保留正文。

#### Execution coordination: overhead and completion

**R7｜核心句：在固定模型和提示词的三次运行中，完整系统相对移除异步协调扩展的系统将平均模型调用从 286.3 降至 133.3、平均总 token 从 35.08 百万降至 14.53 百万，支持异步协调降低该设置下的模型等待开销。**

英文主题句：Across three sessions per configuration, the full system reduced mean model calls from 286.3 to 133.3 and mean total tokens from 35.08 million to 14.53 million relative to the configuration without the coordination extension.

证据与扩写边界：原稿 tab:e2e-ablation；token 相对 no-patch 下降约 58.6%；用各次运行记录展示范围，不做 n=3 下的广泛泛化；Table 2。

**R8｜核心句：完整系统和移除异步协调扩展的系统分别生成 27/27 与 26/27 项请求输出且均满足 24/24 项方法要求，说明该消融主要改变执行协调与开销，而未显示分析方法准确性的提升。**

英文主题句：The full system and the configuration without the coordination extension produced 27/27 and 26/27 requested outputs, respectively, while both met 24/24 method requirements.

证据与扩写边界：原稿 tab:e2e-ablation；缺失项是一次脚本归档；九输出与稳健性六任务是不同评分表；保留这个接近的结果，不能隐藏在附录。

#### Guidance during active computation

**R9｜核心句：分钟级分类任务中的计划修改和自动续跑在完整系统均为 3/3 成功、移除异步协调扩展的系统均为 0/3，支持该受测设置下会话让出与完成事件处理的交互价值。**

英文主题句：During the minutes-scale classification task, mid-run revision and automatic continuation each succeeded in 3/3 full-system sessions and 0/3 sessions without the coordination extension.

证据与扩写边界：原稿 tab:hitl-ablation；Figure 2 时间线 + Table 2；不能外推为任意计划变更、任意小时级任务或所有 OpenClaw 版本都保证成功。

### Discussion｜讨论

**D1｜核心句：三类案例展示 MicroBioAgent 对扩增子、参考驱动和基因组解析分析的支持，重复会话揭示完成情况及输出差异，运行消融则说明异步机制对这些分析的支持作用。**

英文主题句：The case studies demonstrate support for amplicon, reference-based, and genome-resolved analyses, while repeated sessions characterize completion and output variation and ablations assess asynchronous execution support.

证据与扩写边界：原稿 Discussion；综合主张不重复所有数字；与工作流管理器互补，领域技能本身的独立增益尚未被隔离。

**D2｜核心句：研究尚缺少与同资源通用编码智能体的直接比较，且消融只移除了整套运行时扩展，因此现有结果不能分别归因于领域技能、工具指导或事件唤醒中的某一个组成部分。**

英文主题句：A direct comparison with a resource-matched general coding agent and component-wise ablations are needed to isolate the contributions of domain skills, tool guidance, and event handling.

证据与扩写边界：原稿 Discussion 局限及补丁 manifest；明确这是证据缺口而非新实验结果；优先计划直接基线与拆分消融。

**D3｜核心句：稳健性与消融主要来自预处理的单一案例，现有输出差异也说明分析结果仍需研究者核查，系统在更多数据集和实际使用条件下的表现有待评价。**

英文主题句：Robustness and ablation tests are concentrated on preprocessed inputs from one case, and observed output discrepancies underscore the need for researcher verification and evaluation across further datasets and use conditions.

证据与扩写边界：原稿 Discussion 最后一段；本地执行不等于 LLM 数据零外传，不写未经审查的隐私保证；不假设未来模型自然消除已观察错误。

### Conclusion｜结论

**C1｜核心句：MicroBioAgent 支持研究者从目标与测序数据开展多类型微生物组分析，三类重分析展示了其任务覆盖与生物学结果，重复会话和运行消融进一步界定了其稳健性及执行支持能力。**

英文主题句：MicroBioAgent supports study-specific microbiome analysis from research objectives and sequencing data, with reanalyses demonstrating task coverage and biological outputs and additional evaluations characterizing robustness and execution support.

证据与扩写边界：以有边界的贡献收束；不新增实验数字或未经证明的应用扩展。

### Code and data availability｜代码与数据可用性

**V1｜核心句：代码、技能、提示词、环境配置和版本固定的运行时补丁应通过公开仓库提供，并将三项公开数据的 accession 与各实验脚本和日志建立可复核的对应关系。**

英文主题句：Code, skills, prompts, environment specifications, and the version-pinned runtime patch are provided through the project repository; dataset accessions and evaluation artifacts must be linked to reproducible analyses.

证据与扩写边界：原稿 Data/Code availability；仓库链接沿用原稿，公开可访问性、release、归档 DOI 和完整结果包尚待提交前核查；PRJNA777724、PRJEB10878、PRJEB97175。


## 4. 术语约定

| 统一用法 | 首次定义与本版处理 |
|---|---|
| MicroBioAgent | 系统论文名；openclaw-microbiome 仅指实现仓库，OpenClaw 指宿主运行时 |
| domain skills | 方法说明文档与可选参考脚本；不称为独立工具 API 或强制类型契约 |
| event-driven asynchronous execution | 完成事件驱动的异步执行；不宣称零轮询或恰好一次保证 |
| full / no-patch | 有/无整套运行时补丁；不等同于有/无领域技能 |
| task completion | 对应评分表中请求产物的完成；与 output validity、科学正确性分开 |
| human-in-the-loop (HITL) | 研究者在运行过程中修改待执行计划；本版明确分钟级交互测试边界 |
| metagenome-assembled genome (MAG) | 宏基因组组装基因组；区分初始 bins、合格 MAG 与去冗余代表 |
| colorectal cancer (CRC) / KEGG Orthology (KO) | 首次全称后使用缩写；分类结果称 pooled out-of-fold AUROC |

后续调整可直接按段落 ID 指定，例如修改 I4 的研究问题或调整 R1 的案例角色；其余段落保持稳定。

## 5. 实验—结果对应关系

两部分不必机械采用相同段落数，但本稿采用相同的实验族顺序，降低设置与结果之间的查找负担。每个实验先提出评价问题、说明输入/条件/指标，结果部分再回答同一问题。

| 评价问题 | 实验设计 | 结果 | 附录 |
|---|---|---|---|
| 能否完成不同微生物组研究任务并恢复指定模式？ | E1：三案例 | R1–R3：番茄、CRC、环境 | A.2 |
| 更换模型和提示词后，任务完成与输出变化如何？ | E2：27 会话 | R4–R6：完成、定量比较、失败 | A.3（AP6–AP7） |
| 异步协调对开销和输出完成有何影响？ | E3：固定条件消融 | R7–R8：开销与任务/方法完成 | A.3（AP8） |
| 运行中能否接收修改并自动继续？ | E4：运行中反馈 | R9：两项交互判据 | A.3（AP9） |

一个 Appendix 下设实现与复现、案例细节与补充结果、补充评测细节三个小节；逐段核心句及素材需求见 `appendix-outline.md`；`main.tex` 在正文后同步提供附录骨架。附录提供完整细节，正文保留核心机制、公平比较条件、主要结果与改变结论的限制。

## 6. 正文图表安排

| 显示项 | 内容与作用 | 现有来源 | 对应段落 |
|---|---|---|---|
| Figure 1 | 系统概览：三类分析路径、领域技能、资源与执行关系；突出分析输入与结果 | 原稿 fig:architecture、fig:workflow；源码与 workspace 指导 | M1–M4 |
| Figure 2 | full 与 no-patch 时序；标注分类开始、用户修改、完成事件与恢复，不用示意时长伪装实测 | 原稿异步 Methods；HITL 日志；需整理为新图 | M5–M6、R9 |
| Table 1 | 三案例输入规模、任务、数据 accession、评价目标，另注明重复实验用预处理 Case 1 | 原稿 tab:cases-overview、sec:reliability-experiments | E1–E4 |
| Table 2 | 每次运行及均值的 token、调用、输出/方法完成数；附 HITL 两项成功数 | 原稿 tab:e2e-ablation、tab:hitl-ablation | R7–R9 |
| Figure 3 | 三案例各保留一个关键面板：番茄版本分支/物种标志物、CRC ROC、MAG 重建与注释摘要 | 原稿 fig:tomato-diversity、fig:crc、fig:mag；版本分支需基于表格重绘 | R1–R3 |
| Figure 4 | 27 会话六任务完成热图与输出失效说明；若补一致性分析，再增加配对误差等面板 | 原稿 fig:robustness-models 和原始结果表；新指标待计算 | R4–R6 |

Figure 1 与 2 若占用过多版面，可合并为一张含机制和时序的图。正文所有显示项和图注均占 10 页预算；引用原图前需检查可读性，不缩小到无法审阅。

正文依次说明微生物组分析范围与实现、三类案例结果、稳健性及运行协调作用；图表优先保留能直接支撑这些结论的面板。完整实验条件和逐运行记录统一由 `appendix-outline.md` 安排。
