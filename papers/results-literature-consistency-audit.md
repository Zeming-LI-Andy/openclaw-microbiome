# main.tex 结果数值与原文结论一致性核查

核查日期：2026-10-30。核查对象：`papers/main.tex` 的三个案例结果，以及摘要中关于复现、稳健性和 token 节省的概括。

结论：多数展示数值能对应当前图和 Supplementary Data 1；需要优先修改的是复现程度和功能解释。另有消融实验数据版本冲突，无法直接判定正文与 CSV 哪一版应作为最终结果。本次只生成核查报告，未修改稿件。

## 1. 优先处理的问题

### 1.1 番茄案例：“完全恢复原文关联”超出当前数据支持

- 位置：`main.tex:357–359`，以及摘要 `main.tex:60–63`、Discussion 中的对应概括。
- 当前措辞：`fully recovering the published taxonomic associations`。
- 原文：两个物种均在 T1 的两个抗性品种中富集；T2C 共享富集的是 Sphingopyxis；T2 无共享富集。参见 [Yin et al., Results: Potentially inheritable biocontrol bacteria / Fig. 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC9753271/)。
- 当前补充数据：`case1_metaphlan_versions` 第 9–20 行记录的 MetaPhlAn2 结果中，T1 的 P. putida 在 HG64、HF12 中均达到 P < 0.05；Sphingopyxis 在 HG64 中 P = 0.0201，在 HF12 中 P = 0.0707。T2C 的 Sphingopyxis 在两个抗性品种中均 P = 0.0201。T2 的 HF12 中两个物种的方向均为 susceptible 较高，且不显著。
- 判断：可以写“检出了两个文献标志类群，并恢复了部分时间点的富集关联”。T1 的 Sphingopyxis 共享显著富集没有完全恢复。也不应把 Sphingopyxis unclassified 等同于原文经实验验证的 Sphingomonas sp. Cra20。

建议替换：

> Reprofiling with MetaPhlAn2 detected both reported marker taxa and recovered selected resistance-associated enrichments: P. putida in both resistant cultivars at T1 and Sphingopyxis unclassified in both at T2C. However, the T1 enrichment of Sphingopyxis unclassified in HF12 did not reach nominal significance (P = 0.071), indicating partial recovery of the published associations.

另一个解释限制：这里同时从 MetaPhlAn3 + MaAsLin3 变为 MetaPhlAn2 + LEfSe。对“检出”的变化可以讨论 profiler/database，但富集显著性的变化同时涉及检验方法，不能全部归因于软件版本。

### 1.2 番茄属水平富集：数目正确，但需要写明未校正 P 值

- 位置：`main.tex:344–348`、补充图 `fig:tomato-enrichment` 图注。
- 从 `case1_16s_differential` 按正系数、P < 0.05 重算，两个抗性品种共有的属分别为 T1 15、T2C 6、T2 7、T3C 8、T3 7；正文“6–15”正确。
- `results_summary_report/case_study_1.md` 明确说明此处使用 nominal P，且没有比较通过 BH q < 0.05。
- 判断：应说明这是探索性的未校正筛选。`consistently ... across individual sampling conditions` 也容易使读者误以为同一批属在所有时间点持续富集；实际共享属集合随时间点变化。

建议替换：

> At individual sampling conditions, 6–15 genera showed positive associations with both resistant cultivars at nominal, unadjusted P < 0.05; the shared taxa varied across conditions, and none of the comparisons passed BH-adjusted q < 0.05.

### 1.3 MAG：“三类均有基因”不足以证明完整通路

- 位置：`main.tex:485–490`。
- `case3_functional_annotations` 第 2–12 行及当前 Fig. 3d 一致：共 11 个 MAG；alkane terminal oxidation 有非零计数的为 9 个，其余两类为 11 个；三类同时有非零计数的为 9 个。正文计数正确。
- 但这张表提供每类注释基因的合计，没有提供每个必要反应是否齐全的证据。“pathways ... detected”及“complete hydrocarbon utilization”超过这一证据。
- 原文还使用了转录组、蛋白组和底物化学分析；当前基因组注释不能复现其活性证据。原文核心限制是未证明聚乙烯聚合物本体被降解，观察到的是部分烷烃及氧化衍生物的利用。参见 [Sandholm et al., Results / Discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753306/)。

建议替换：

> Genes assigned to alkane terminal oxidation were detected in nine of the 11 MAGs, and genes assigned to 2-ketone or oxidized-derivative metabolism and β-oxidation were detected in all 11. Nine MAGs contained annotations in all three categories, supporting metabolic potential related to these processes; pathway completeness and substrate utilization were not established by gene annotation alone.

摘要中的 `faithfully recapitulated the primary biological findings` 建议同步改为 `recovered selected biological patterns reported in the source studies`。这更符合本研究实际评价范围。

### 1.4 消融：正文与当前 CSV 的数据版本冲突

- 位置：摘要 `main.tex:52–54`，Results `main.tex:634–639`，Discussion `main.tex:746–747`，消融表。
- 正文与 `ablation/no-patch-token-report.md` 一致，但与当前 `ablation/token_usage.csv` 不一致。

| 指标 | 正文/文字报告 | 当前 token_usage.csv 重算 |
|---|---:|---:|
| full 平均 total tokens | 14,525,551 | 14,525,551 |
| no-patch 平均 total tokens | 35,080,864 | 22,658,254.67 |
| full 相对 no-patch 的平均 token 减少 | 58.59% | 35.89% |
| no-patch 平均 model calls | 286.33 | 189.33 |

- 因此，`over 50%` 在文字报告版本下成立，在当前 CSV 版本下不成立。正文采用的 2.4 倍也只对应文字报告版本。
- 还有实验条件冲突：`main.tex:609–610` 写初始计划确认后无用户消息；文字报告记载 no-patch 第 1 次有多次 continue，第 2 次有一次 Continue。当前 CSV 关联了新的 job ID，因此可能是替换实验后正文/报告未同步。
- 处理：按最终选定的三个 no-patch job ID 回查转录、计数范围及用户干预，统一 CSV、文字报告、正文和表格。当前证据不足以替用户选定版本，不应只把正文数值机械替换为 CSV。

## 2. 数值成立，但需要限制解释范围

### 2.1 CRC：主要标志菌方向与文献一致

- 位置：`main.tex:403–416`。
- 当前补充数据支持 8 个 CRC-enriched、2 个 control-enriched；列出的 P. micra、P. stomatis、F. nucleatum、S. moorei 为 CRC 较高，E. ventriosum 为 control 较高。与 [Yu et al., Fig. 1 / CRC-associated species](https://gut.bmj.com/content/gutjnl/66/1/70.full.pdf) 的方向一致。
- 16 条正相关边、P. micra 的 degree = 6、两条相关系数 0.4901 与 0.5297 均与补充数据相符。
- 原文网络使用 21 个 mOTU 及 |ρ| > 0.5；当前为 10 个物种、|ρ| ≥ 0.4 且 q < 0.05。因此可称定性恢复相关方向，不能称网络数值或结构被严格复现。ρ = 0.49 的边达不到原文的展示阈值。

### 2.2 CRC：分类器数值正确，属于本研究新分析

- 位置：`main.tex:418–429`。
- `case2_classifier_folds` 中 pooled AUROC 为 0.90165165 与 0.63213213，四个 sensitivity/specificity 为 0.8243、0.8889、0.4054、0.8704，均支持正文的舍入值。
- 原文核心是 20 个 gene markers、跨队列验证及 qPCR；当前是 HUMAnN UniRef90/KO、每折 15 个特征及嵌套交叉验证。不能把两个 AUROC 当作原文的数值复现或直接比较优劣。参见 [Yu et al., Biomarker discovery / validation](https://gut.bmj.com/content/gutjnl/early/2015/09/25/gutjnl-2015-309800.full.pdf?with-ds=yes)。
- `confirming ... superior diagnostic discrimination` 建议改为 `showing higher cross-validated discrimination for gene-family features in this cohort`。目前支持此队列内的比较，不支持普遍诊断优越性；也没有在已核查材料中看到 AUROC 差值的置信区间或正式差异检验。

### 2.3 MAG：分类和群落方向相符，数量与原文有明显差异

- 当前 75 个代表 MAG 的目录确认为 50 HQ + 25 MQ，cluster members 合计为 153；图 a 的六组回收数合计同为 153。372 个初始 bins 未在本次从原始输出独立重算。
- 原文报告 84 HQ + 46 MQ 个 dereplicated MAG；当前 50 + 25，不能称 MAG 回收数量严格复现。工具版本及去冗余定义不同，差异本身不等于结果错误。
- 当前主要丰度：S1 LMWPE 的 A. guillouiae 为 64.1328%，S1 C30 为 66.9342%；S1 C40 的 Aquipseudomonas 合计为 65.9220%，支持正文 64%、67%、66%。原文前两者为 55.8%、62.8%，属于优势类群方向相符、具体丰度不同。
- `all ten focal taxonomic groups` 有补充数据中的分类名称映射支持，但物种或属名映射不能直接证明恢复了原文的相同菌株/MAG；如需更强的 recovery 表述，应补原文 MAG 与当前 MAG 的 ANI/覆盖度对应。
- 正式图和工作簿支持 11 个功能注释 MAG；`results_summary_report/case_study_3.md` 仍是 10 个及旧基因计数，应更新旧摘要。

### 2.4 HQ 分类应说明采用的是哪些质量条件

- 位置：`main.tex:461–464` 及 HQ/MQ 图例。
- 当前目录只有完整度和污染度等字段；未提供 rRNA/tRNA 完整性判据。
- [MIMAG 标准 Table 1](https://www.nature.com/articles/nbt.3893) 的 high-quality draft 除 >90% completeness、<5% contamination 外，还有 rRNA/tRNA 要求。
- 若只按 CheckM2 完整度与污染度筛选，宜称 `MAGs meeting the high-completeness/low-contamination thresholds` 或明确 HQ 是本研究的操作性定义；现有材料不足以确认严格满足全部 MIMAG HQ 标准。

### 2.5 稳健性：不显著不等于逐项可复现

- 位置：摘要 `main.tex:65–66`、Results `main.tex:527–552`。
- 完成度 160/162 = 98.7654%，四舍五入 98.8% 正确。
- DESeq2 跨模型最小 Holm P = 0.058646，正文 ≥0.059 是正常舍入；详细/中等提示下的 16S P = 0.54、0.50、0.13，shotgun P = 0.58、0.24、0.064 均对应 TSV。
- 这些检验比较的是总体分布。相同分布可以伴随样本或物种对应关系的改变，P ≥ 0.05 也未证明等效；1770 个距离来自共享样本，不能当作相互独立的生物学重复。
- 因此，`highly reproducible ... estimates` 宜收紧为 `similar marginal distributions of diversity metrics and within-method differential-abundance effect sizes`。如要证明逐项一致性，可补按同一样本/物种配对的误差、方向一致率、相关性或等效性分析。

## 3. 已核对且基本一致的项目

| 项目 | 核对结果 |
|---|---|
| 总文库数 | sample_accessions 为 60 + 36 + 128 + 6 = 230 |
| CRC 病例/对照与分期 | 74/54、early 36、late 38，与原文设计一致 |
| 番茄 Shannon | 当前数据 P = 0.0021645、0.0043290，支持正文 0.002、0.004 |
| 番茄 PCoA | 当前图标注 PC1 56.3%、PC2 12.2%，与正文一致 |
| 番茄 MetaPhlAn3 P. putida group | T1 两品种 P = 0.01284、0.00917，支持正文 0.013、0.009 |
| CRC PERMANOVA | F = 2.3160 / P = 0.002；F = 1.6507 / P = 0.009，与正文一致 |
| CRC 差异物种与网络 | 8 + 2、16 条边、degree 6、ρ = 0.49/0.53，与补充数据一致 |
| CRC 分类器 | AUROC 0.902/0.632 及 sensitivity/specificity 舍入正确 |
| 去冗余 MAG | 75 = 50 HQ + 25 MQ；成员合计 153 |
| MAG 功能类别计数 | 9/11、11/11、11/11，以及三类均有基因的 9/11，正确 |
| 稳健性完成率 | 160/162，98.8%，正确 |

番茄的总体“接种后多样性降低、抗性品种较能维持多样性”与来源研究方向相符。但原文有品种/时间点例外，当前 T1 已有显著差异，不能推广成所有条件逐一相同。

## 4. 核查范围与证据限制

读取了当前 TeX、三张案例主图、正式 Supplementary Data 1、案例结果摘要、稳健性 TSV、消融 CSV/报告。番茄和 LMWPE 来源全文通过 Europe PMC fullTextXML 核读；CRC 出版方直连受 403 限制，相关段落通过出版方 PDF 的搜索索引及作者机构存档核对。

本次未重跑生物信息流程，未从全部原始 reads 或会话转录重新计算结果，未逐条审计所有方法和竞品文献。表中“一致”表示与当前支持材料一致，不等同于原始分析方法已通过独立验证。统计条件、数据版本和结论强度问题已在上文单列。
