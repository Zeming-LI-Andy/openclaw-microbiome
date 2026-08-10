import type { ReferenceCatalogEntry } from "./types.js";

/** Standard reference ids (descriptions/kinds only — no deploy paths). */
export const STANDARD_REFERENCE_CATALOG: Record<string, ReferenceCatalogEntry> = {
  silva_ssu_nr99_seqs: {
    description: "SILVA 138.2 SSURef NR99 full-length reference sequences (.qza)",
    kind: "file",
  },
  silva_ssu_nr99_tax: {
    description: "SILVA 138.2 SSURef NR99 taxonomy (.qza)",
    kind: "file",
  },
  silva_v4_seqs: {
    description: "SILVA 138.2 V4 (515F/806R) reference sequences (.qza)",
    kind: "file",
  },
  silva_v4_tax: {
    description: "SILVA 138.2 V4 (515F/806R) taxonomy (.qza)",
    kind: "file",
  },
  silva_v34_seqs: {
    description: "SILVA 138.2 V3-V4 (341F/806R) reference sequences (.qza)",
    kind: "file",
  },
  silva_v34_tax: {
    description: "SILVA 138.2 V3-V4 (341F/806R) taxonomy (.qza)",
    kind: "file",
  },
  kneaddata_db_human_genome: {
    description: "KneadData human genome Bowtie2 reference (hg37dec_v0.1)",
    kind: "directory",
  },
  metaphlan_bowtie2_db: {
    description: "MetaPhlAn Bowtie2 database directory",
    kind: "directory",
  },
  humann_chocophlan: {
    description: "HUMAnN ChocoPhlAn nucleotide database",
    kind: "directory",
  },
  humann_uniref: {
    description: "HUMAnN UniRef protein database",
    kind: "directory",
  },
  humann_utility_mapping: {
    description: "HUMAnN utility mapping database",
    kind: "directory",
  },
  eggnog_mapper_data: {
    description: "EggNOG mapper data directory (eggnog.db, diamond DB)",
    kind: "directory",
  },
  eggnog_bact_arch_dmnd: {
    description: "EggNOG bacteria/archaea Diamond database",
    kind: "file",
  },
  vfdb_dmnd: {
    description: "VFDB Diamond database",
    kind: "file",
  },
  card_db: {
    description: "CARD local DB for RGI",
    kind: "directory",
  },
  aviary_gtdb: {
    description: "GTDB for Aviary / GTDB-Tk",
    kind: "directory",
  },
  aviary_checkm2: {
    description: "CheckM2 database for Aviary",
    kind: "directory",
  },
  aviary_eggnog: {
    description: "EggNOG data directory for Aviary (set only for aviary runs)",
    kind: "directory",
  },
  aviary_singlem: {
    description: "SingleM metapackage for Aviary",
    kind: "directory",
  },
  kegg_ko_link: {
    description: "KEGG link ko→pathway table",
    kind: "file",
  },
  kegg_pathway_list: {
    description: "KEGG pathway list (ko)",
    kind: "file",
  },
};
