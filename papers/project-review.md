# 项目与论文材料核查（2026-09-14）

本文件只记录当前仓库中可核查的事实和论文写作所需的证据缺口；云端 case-study 作业尚未核查。论文暂定名 **MicroBioAgent**，实现仓库名为 `openclaw-microbiome`。

## 可由源码确认的系统设计

- 插件对 OpenClaw 注册的工具只有 `mgx_create_job`（`openclaw.plugin.json`、`catalog/tools.yaml`、`src/index.ts`）。分析步骤由 OpenClaw agent 阅读 `skills/*/SKILL.md`，再通过原生 `exec` 调用 conda 工具；插件本身不是固定 DAG 或流水线引擎。
- `mgx_create_job` 使用稳定的 `sessionKey` 将一次会话绑定到一个作业，按需创建或复用 `stage/`、`analysis/`、`reproducibility/logs/` 和 `reproducibility/generated_scripts/`（`src/runtime/job.ts`）。无 `sessionKey` 时有环境变量及旧书签的兼容回退；论文若描述“一会话一作业”，应限定在正常提供 `sessionKey` 的 OpenClaw 上下文。
- 插件在启动时尝试同步用户配置的参考数据库路径到 agent 工作区的 `registry/references.yaml`（`src/index.ts`、`src/refs/sync.ts`）。`runtimes.yaml` 列出工具与 conda 环境；数据库实体、安装环境和挂载仍由部署方提供。
- 当前发货 **31 个 skill**：16S 8、shotgun 12、统计 3、公共数据 2、REST 注释 6。它们是可选步骤说明，不等于每个案例都运行了这些工具。
- `workspace/AGENTS.md` 和 `workspace/CODING.md` 规定先计划、确认后开始重计算、将输出限制在作业目录、长任务使用 `exec` 的退出通知。这是 agent 工作区的操作协议；“自动规划成功率”“恢复成功率”等仍需实验日志证明。长任务唤醒依赖版本固定的 OpenClaw 补丁包（`patches/openclaw-exec-session-wake/`）。

## 现有论文材料

| 文件 | 当前状态 |
|---|---|
| `papers/main.tex` | 英文论文框架；Results 中案例与可靠性实验大多还是占位文字，Fig. 1–5 目前为框图占位。 |
| `papers/outline.md` | 论文定位、章节与实验规划，属于设计方案，不是已完成实验结果。 |
| `papers/cases.md` | 三个案例及稳健性/消融的采集卡；作业 ID、数据集登录号、运行流程、耗时等仍为 TBD。 |
| `papers/figures/` | 已有 4 张案例 PNG 和详细图注，但 `main.tex` 尚未引用这些 PNG；图到云端原始作业、分析脚本和统计输出的对应关系未记录。 |
| `papers/refs.bib` | 已加入 Introduction 使用的真实软件文献；后续章节仍需按实际论断补齐引文。 |

## 写作时必须区分的证据层级

1. **实现能力**：源码证明提供了 session job、skill、runtime/reference registry 和长任务执行协议。
2. **案例实际执行**：需要云端每个 job 的命令、日志、输出、版本和人工干预记录，才能说“某案例运行了某技能”“端到端完成”。
3. **生物学和性能结果**：需要原始数据、统计脚本、表格与图的追溯链，才能写样本量、效应量、显著性、分类器 AUC、MAG 数量、耗时或成功率。

特别注意：`figures/figure_captions.md` 已写出 Case 1 的分组/重复数、Case 2 的样本数与交叉验证方案、Case 3 的 MAG 指标；`cases.md` 对应字段仍是 TBD。图注可以作为待验证线索，不能直接当作已核查的结果。Case 1 的现有两张图仅展示 16S 多样性和属富集，尚不能单独支撑文稿中的 MetaPhlAn 或遗传率表述。Case 2 图注提到 HUMAnN/KO 特征与嵌套交叉验证，需要确认它们与云端执行记录一致。Case 3 图注写了 CoverM 与 eggNOG，也需核对实际 MAG 流程和质量评估输出。

## 从云端逐案例取回的最小证据包

每个案例至少记录：公开数据 accession 与原研究引用、样本/分组表、`job_id` 和原始路径、用户提示词与计划/确认记录、执行过的 skill 顺序、每步命令和环境/数据库版本、起止时间与退出状态、人工干预和失败/跳过步骤、生成图表的脚本与输入表、最终图/表及校验和。对 CRC 分类器另需训练/测试划分、特征选择所在折次和基线；对 MAG 案例另需组装/分箱/去冗余/质量/丰度/功能注释的中间产物。敏感信息（密钥、患者标识、服务器凭据）不要拷进 `papers/`。

在这些证据到位前，不应把计划中的稳健性/消融实验写成已完成结果，也不应在摘要中填入未经核查的数值。
