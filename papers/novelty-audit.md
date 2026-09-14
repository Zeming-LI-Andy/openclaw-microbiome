# 创新性主张核查（2026-09-14）

本项目与 BGI MetaClaw **独立开发**（作者确认）。论文应以 **MicroBioAgent：可本地执行的微生物组分析智能体** 介绍工作；OpenClaw 是实现细节，不作 Introduction 的主语。下列判断区分“源码支持”“案例已证明”“尚需验证”；云端作业尚未审查。

## 技能覆盖的准确边界

仓库有 31 个 skill：16S 8、shotgun 12、统计 3、公共数据 2、REST 注释 6。它们按分析路径覆盖：

| 层级 | 仓库中的能力 | 不应写成 |
|---|---|---|
| 16S/amplicon | QIIME 2 导入、DADA2、ASV 汇总、分类、系统发育、多样性、导出；PICRUSt2 **预测**功能 | 直接测量群落基因或代谢物 |
| 有参 shotgun | KneadData、MetaPhlAn、HUMAnN；统计、多样性、富集 | 所有 case 均使用每项技能 |
| 无参/组装 shotgun | Aviary 组装、MAG 恢复/注释/去冗余；基因目录、EggNOG、Bakta | 不依赖数据库：MAG 的质量、分类、功能注释仍需 GTDB/CheckM2/EggNOG 等参考资源 |
| 基因组/功能扩展 | RGI/CARD、VFDB、gapseq 代谢通路与模型、gutSMASH/antiSMASH 生物合成基因簇；KEGG/GO/UniProt/MetaCyc/NCBI/EggNOG REST 查询 | 已检测、定量或结构鉴定“初级/次级代谢产物”；这是**代谢潜力/BGC 预测**，不是 metabolomics |

“无参考数据库宏基因组学”建议写作 **assembly-based/de novo metagenomics**，避免误指完全不使用参考数据库。“目前最全”需先定义比较对象、功能维度与验证标准；[MetaClaw 的公开技能目录](https://github.com/BGI-AI-models/MetaClaw)也含 amplicon、shotgun、metabolomics、ML、BGC/ARG 等模块，不能单凭 skill 数量宣称领域第一。

## 三个候选贡献的证据边界

1. **跨三条分析路径的本地端到端执行**：这是可优先主张的系统能力。源码提供 step-level skills 和宿主 conda 运行方式。需用云端作业核查每例从什么输入开始、哪些步骤由 agent 实际执行、产物是否通过独立检查；尤其 MAG 组装与恢复。与 [MetaClaw v2](https://www.biorxiv.org/content/10.64898/2026.07.21.739769v2) 的差别应陈述为本地原始数据上游执行、agent 逐步骤调度与不同的部署约束，而非“此前没有跨类型分析智能体”。
2. **本地优先的数据处理**：宿主 conda 与本地数据库允许原始 reads 不经 FlowHub 等外部计算平台；Docker 也可在本机运行。但代码并未强制离线推理或禁止外传。`annotation-*`、SRA 等技能会调用网络服务；OpenClaw 可配置远端模型提供商。应表述为“支持本地部署并可将原始读段保留在本地”，只有验证本地模型/断网配置及数据流后才能写“完全离线”“确保数据不外泄”。可做网络出口审计作为论文证据。
3. **人在环中与长任务续接**：`workspace/AGENTS.md` 规定先确认计划、逐步执行和持续更新状态；`workspace/CODING.md` 规定长命令以 timed-yield `exec` 运行，取得 `sessionId` 后调用 `sessions_yield`。版本固定的 OpenClaw 补丁不仅修复命令完成后的唤醒，也修改模型可见的 `exec`/`sessions_yield` 提示和完成事件的同会话续接。在 CLI 仍于后台运行、模型已让出回合时，用户可向同一会话发消息，智能体可据此调整后续步骤或检查/控制当前进程；命令结束又触发另一条续接路径。这是本项目值得重点评估的**长周期分析中途反馈闭环**，而非人工审批机制的首创。HITL 并非其他 Bio-agent 没有：[M3A 预印本](https://www.biorxiv.org/content/10.64898/2026.06.04.729919v1.full)明确评估 HITL、HOTL、自主三种模式；[BioAgents](https://www.nature.com/articles/s41598-025-25919-z)讨论人类反馈但并未证明相同运行机制。论文中应提供消息、计划修订、进程控制、退出事件和后续步骤的同会话日志。

关于**用户在长任务仍运行时插入反馈并重排后续步骤**的进一步核查、OpenClaw steering 对照及验证方案，见 `papers/feedback-intervention-audit.md`。

## 另外值得争取的贡献

- **按步骤自适应的执行边界**：不像注册完整上游 FlowHub 流程，agent 按 skill 逐步运行、检查产物、根据有效中间结果只重跑失败阶段（`workspace/CODING.md`）。这是设计差异；要用扰动实验比较固定路径与自适应路径的成功率、重算量和人工介入。
- **从群落组成到基因组代谢潜力的多尺度分析图谱**：ASV、物种、基因家族、通路、MAG、BGC 可在一个技能目录中衔接。但“整合分析”需要样本和 MAG 层面的可追溯链接与实际案例支持；只有功能目录时应说“覆盖”而非“整合”。
- **面向长任务的双路径会话连续性**：timed-yield `exec` 与 `sessions_yield` 让智能体在 CLI 运行期间退出当前回合，给用户消息开启新回合的窗口；退出通知又使作业完成时自动续接。可设计受控的中途改参、停止/重跑及消息与完成事件竞态测试，量化反馈采纳延迟、任务完成、重复执行、孤儿进程、作业路径一致性。
- **部署可移植性与参考库约束**：runtime/reference registries 把工具环境与用户路径分离，缺失引用时要求停止而非猜测。可在两种主机/路径布局上复现实验，并以路径错误率/迁移时间验证；目前只是设计主张。
- **可复核的评估材料**：若公开 prompts、输入清单、skill 轨迹、版本、日志、期望产物与自动评分脚本，可以把三案例提升为可复用 benchmark。参考 [BioAgent Bench](https://arxiv.org/abs/2601.21800) 与 [BixBench3](https://arxiv.org/abs/2608.25286) 的产物检查方法。需要先取得云端作业与数据许可。

## 推荐的主张顺序

**主贡献**：在本地原始数据上，由一个领域智能体按步骤执行并核查 16S、有参 shotgun 和组装/MAG 三类微生物组分析。**机制贡献**：本地运行时与参考库解析、会话作业隔离、长任务完成后续接、人工确认与异常介入。**实证贡献**：以三例及预先定义的产物检查、重复/扰动/消融验证覆盖与可靠性。代谢、BGC、ARG 等作为扩展能力，按云端实际运行情况分为“已演示”和“已实现但未验证”。
