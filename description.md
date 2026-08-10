# **16S / 宏基因组** 自动分析系统

## 分析能力

### 16S（QIIME 2）

| Skill | 作用 |
|-------|------|
| `16s-import` | 导入测序数据为 QIIME 2 artifact |
| `16s-denoise-dada2` | DADA2 去噪，生成 ASV / feature table |
| `16s-feature-summarize` | feature 与序列摘要、质控可视化 |
| `16s-taxonomy` | 预训练分类器赋分类（依赖 SILVA 等） |
| `16s-phylogeny` | 代表性序列系统发育树 |
| `16s-diversity` | $\alpha$ / $\beta$ 多样性 |
| `16s-export` | 导出表与序列（可选） |
| `16s-picrust2` | PICRUSt2 功能预测（可选） |

### Shotgun

| Skill | 作用 |
|-------|------|
| `shotgun-kneaddata` | 质控 / 宿主去污染（KneadData） |
| `shotgun-metaphlan` | MetaPhlAn 物种组成 |
| `shotgun-humann` | HUMAnN 通路 / 基因家族（可选） |
| `shotgun-gene-catalog` | Prodigal ORF → CD-HIT 非冗余基因/蛋白目录（可选） |
| `shotgun-eggnog` | EggNOG-mapper 基因功能注释（可选） |
| `shotgun-vfdb` | VFDB 毒力因子筛选（可选） |
| `shotgun-rgi` | CARD RGI 耐药基因（可选） |
| `shotgun-aviary` | Aviary 组装 / MAG 回收 / MAG 注释 / 多样本去冗余（可选） |

### 公共数据

| Skill | 作用 |
|-------|------|
| `sra-search` | SRA 元数据检索 |
| `ncbi-assembly-proteins` | 按物种下载 NCBI Assembly 蛋白 FASTA |

### 统计

| Skill | 作用 |
|-------|------|
| `stats-diversity` | 多样性统计 |
| `stats-differential-abundance` | 差异丰度 |
| `stats-enrichment` | 通路 / KO 等基因集富集 |

### 注释（REST / API）

| Skill | 作用 |
|-------|------|
| `annotation-kegg` | KEGG 同源基因 / 通路查询 |
| `annotation-uniprot` | UniProt |
| `annotation-gene-ontology` | Gene Ontology |
| `annotation-ncbi-gene` | NCBI Gene |
| `annotation-metacyc` | MetaCyc |
| `annotation-eggnog-api` | EggNOG API |

## 参考库

由用户 `~/.openclaw/microbiome-refs.yaml` 映射，同步为 `registry/references.yaml` 的 `path`。标准 id：

| 类别 | id | 说明 |
|:-----|:----------------------------------|:---------------------|
| 16S / SILVA | `silva_ssu_nr99_seqs` / `_tax` | SSURef NR99 全长序列与分类 |
| | `silva_v4_seqs` / `_tax` | V4（515F/806R） |
| | `silva_v34_seqs` / `_tax` | V3–V4（341F/806R） |
| Shotgun | `kneaddata_db_human_genome` | KneadData 人基因组（hg37dec） |
| | `metaphlan_bowtie2_db` | MetaPhlAn Bowtie2 DB |
| | `humann_chocophlan` | HUMAnN ChocoPhlAn |
| | `humann_uniref` | HUMAnN UniRef |
| | `humann_utility_mapping` | HUMAnN utility mapping |
| 注释 | `eggnog_mapper_data` | EggNOG-mapper 数据目录 |
| | `eggnog_bact_arch_dmnd` | EggNOG 细菌/古菌 Diamond DB |
| | `vfdb_dmnd` | VFDB Diamond DB |
| | `card_db` | CARD（RGI） |
| Aviary | `aviary_gtdb` | GTDB / GTDB-Tk |
| | `aviary_checkm2` | CheckM2 DB |
| | `aviary_eggnog` | Aviary 用 EggNOG |
| | `aviary_singlem` | SingleM metapackage |
| KEGG 本地 | `kegg_ko_link` | KO→pathway 对照表 |
| | `kegg_pathway_list` | pathway 列表（ko） |
