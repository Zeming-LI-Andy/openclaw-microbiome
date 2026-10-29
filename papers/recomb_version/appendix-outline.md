# Appendix 大纲

采用 **一个 Appendix：Supplementary Methods and Results**，下设三个主题小节。附录承担实现复现、案例补充和评测细节三项工作；同一实验的方法与补充结果放在一起，减少跨节查找。

正文保留核心方法、关键实验条件、指标定义、主要结果及影响结论的限制。附录只补充理解或复核这些内容所需的细节。以下为 9 个解释性自然段的核心句；图表、完整提示词和参数清单直接呈现，不为每份材料另设一节或重复写说明段。

## A.1 Implementation and reproducibility｜实现与复现

对应正文：M1–M7、V1。

**AP1｜核心句：MicroBioAgent 的实现由会话作业管理、领域技能与资源配置共同支持，复现分析需要固定这些组件及其软件和数据库版本。**

英文主题句：MicroBioAgent combines session-level job management, domain skills, and resource configuration, whose software and database versions must be fixed for reproducibility.

支撑材料：合并原 A.1–A.2、G.1–G.2；列出实现职责、技能与环境/数据库版本；提供代码版本及脚本—结果索引。完整安装步骤和文件校验清单放代码仓库。

**AP2｜核心句：事件驱动的执行协调通过版本固定的 OpenClaw 运行时扩展实现，其会话让出、完成事件处理与自动续跑路径决定消融比较实际移除了哪些功能。**

英文主题句：Event-driven execution coordination is implemented through a version-pinned OpenClaw runtime extension whose event-handling and continuation behavior defines the functions removed in the ablation.

支撑材料：合并原 A.3 与 E.1 的实现部分；记录精确 commit、扩展修改及 idle/active/streaming 行为；保留 full/no-patch 原始条件映射。正文保留机制解释，这里仅补实现细节。

## A.2 Case-study details and extended results｜案例细节与补充结果

对应正文：E1、R1–R3。

**AP3｜核心句：番茄案例的补充材料应将样本分组、扩增子与 shotgun 分析方法及完整结果放在一起，并明确第二个物种标志物的恢复依赖研究者指定的版本重分析。**

英文主题句：Supplementary tomato results link sample groups and analytical procedures to the full outputs and distinguish the investigator-guided profiler-version reanalysis.

支撑材料：合并原 B.1、F.1；PRJNA777724，60/36 文库映射、关键参数、多样性与属富集图、MetaPhlAn3/2 物种对照。人工介入仍在 R1 正文说明。

**AP4｜核心句：CRC 案例的补充材料应连接物种和功能分析结果、折内特征选择及 out-of-fold 预测，使其生物学结果与分类评价能够被复核。**

英文主题句：Supplementary CRC results connect species and functional analyses with within-fold feature selection and out-of-fold predictions for reproducible evaluation.

支撑材料：合并原 B.2、F.2；PRJEB10878，74/54 分组、PCoA/PERMANOVA、差异菌与网络、交叉验证划分和预测表。核实特征与阈值选择所在折次。

**AP5｜核心句：环境案例的补充材料应把组装分箱、质量筛选和去冗余步骤与焦点基因组的丰度及功能注释对应起来，说明基因存在所支持的代谢潜力。**

英文主题句：Supplementary environmental results link assembly, quality filtering, and dereplication to focal-genome abundance and functional annotations.

支撑材料：合并原 B.3、F.3；PRJEB97175，六文库、372→153→75 筛选明细、十类群/11 MAG 映射、质量阈值与注释矩阵。遗传潜力的解释边界仍保留正文。

## A.3 Additional evaluation details｜补充评测细节

对应正文：E2–E4、R4–R9。

**AP6｜核心句：稳健性评测的完整提示词、模型配置和逐会话评分应对应到同一组预处理输入，使六任务完成率的分母和遗漏情况可核查。**

英文主题句：Robustness prompts, model configurations, and per-session scores are linked to shared preprocessed inputs so that task-completion counts and omissions can be verified.

支撑材料：合并原 C.1–C.3；记录 ASV 等输入与 shotgun 20% 读深、三档提示全文、3×3×3 运行设置、六任务评分及产物。正文仍给出完成定义。

**AP7｜核心句：输出一致性分析应完整说明条目对齐、重复平均、丰度过滤和检验方法，并用具体实例解释区域选择、特征对齐和归一化导致的差异。**

英文主题句：Output comparisons disclose alignment, replicate averaging, filtering, and statistical procedures, with examples of region-selection, feature-alignment, and normalization discrepancies.

支撑材料：合并原 D.1–D.3；保留同方法子集、≥5% 丰度条件及全量 Holm 校正结果，给出三类错误实例；不能将未检出差异视为等价。新的配对指标如未计算不列为已有结果。

**AP8｜核心句：运行协调消融应报告两种配置的共同条件、每次运行的输出与方法评分及调用和 token 记录，使其开销比较可重算。**

英文主题句：Execution-coordination ablations report shared conditions and per-session output, method-adherence, call, and token records so that overhead comparisons can be recomputed.

支撑材料：合并原 E.1 的条件说明与 E.2；三次重复/条件、九输出/八方法、token 提取口径与原始计数。主要均值和接近的完成表现仍留正文；不重复正文整张表。

**AP9｜核心句：运行中反馈实验应以进程状态、用户指令、计划修改和完成后续跑的事件顺序验证两个交互判据，并保留失败会话。**

英文主题句：Mid-run guidance is evaluated through the sequence of process status, user instruction, plan revision, and completion-triggered continuation, including failed sessions.

支撑材料：保留原 E.3；六次会话的事件时间线、完整 DESeq2/热图指令与成功/失败判据；分钟级任务和 n=3 边界仍在 R9。

## 材料如何放置

下表是材料分组，不要求每一行都生成新的图或表；优先整理已有材料，删除与正文重复的面板。图表编号在确定最终内容后统一分配。

| 位置 | 建议保留的附录材料 | 来源与当前状态 |
|---|---|---|
| A.1 | 精简的组件/版本/资源表；运行时扩展及事件处理说明 | 现有实现、原稿 Methods 和 patch manifest；需汇总版本 |
| A.2 | 每案例的方法与样本信息；正文未展示的生物学面板及关键结果表 | 原稿三案例 Methods、主图与补充材料；需核对结果来源 |
| A.3 稳健性 | 三档提示、逐会话评分、完整定量比较及失败实例 | 现有稳健性材料；新一致性指标尚未计算 |
| A.3 消融 | 逐运行计数、评分细则和交互时间线 | 原稿消融表及会话记录；需核对日志与提取口径 |
| 代码仓库 | 安装命令、完整技能文件、原始日志、脚本、产物索引和校验信息 | 在 A.1 给入口；不将这些文件逐项扩写成附录段落 |

文献能力比较表不是必需附录项；仅在它支撑正文的具体文献定位、且逐项来源核实后保留于 A.1。直接智能体基线、拆分组件消融和长任务压力测试属于可能需要补做的实验，不预先为未完成实验设置附录章节；正文 D2–D3 保留相应证据边界。

正文—附录对应：R1–R3 → A.2；R4–R6 → A.3 的 AP6–AP7；R7–R8 → AP8；R9 → AP9。正文主要数值只需报告一次，附录提供逐运行或逐条目明细。原七节收拢为：实现与复现合并；案例方法与生物学结果按案例合并；稳健性、输出比较和消融合并为补充评测。当前仍是大纲，完整正文的压缩字数尚不适用。
