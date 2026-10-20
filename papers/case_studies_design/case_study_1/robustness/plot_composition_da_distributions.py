#!/usr/bin/env python3
"""Distribution comparisons for composition and differential abundance.

Composition value: relative abundance of one genus (16S) or one species
(shotgun) in one sample, taken from the original table. An abundance table
is used as stored. A count table is converted once, per sample, before
taxon names are filtered. A taxon missing from a session that has the
sample enters the average as 0. A sample–taxon pair is kept only when that
session-mean relative abundance is at least 5% in every compared group.
Differential-abundance value: raw log2FC for taxa shared across models.
Coefficients and LDA scores are not used.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
import score_robustness as sr
from audit_panel_alignment import require_matplotlib_panel_alignment
from plot_model_distributions import (
    LEVEL_LABEL,
    LEVEL_ORDER,
    MODEL_LABEL,
    MODEL_ORDER,
    PALETTE,
    PAIRS,
    _fmt_p,
    _style,
    holm,
)

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
P_FLOOR = 1e-300


def canon_sample(value: object) -> str:
    text = str(value).upper().split("_SRR")[0]
    text = "".join(ch for ch in text if ch.isalnum())
    import re

    match = re.match(r"([A-Z]+\d*)T(\dC?)RS(\d+)$", text)
    if match:
        return f"{match.group(1)}-T{match.group(2)}-RS{match.group(3)}"
    match = re.match(r"([A-Z]+\d*)RS(\d+)T(\dC?)$", text)
    if match:
        return f"{match.group(1)}-T{match.group(3)}-RS{match.group(2)}"
    return ""


def clean_genus(value: object) -> str:
    import re

    text = str(value).strip()
    match = re.search(r"g__([^;|]+)", text)
    if match:
        text = match.group(1)
    else:
        parts = [part for part in re.split(r"[|;]", text) if part and part not in {"nan", "None"}]
        text = parts[-1] if parts else ""
        text = re.sub(r"^[a-zA-Z]__", "", text)
    text = text.strip().lower().replace(" ", "_")
    if text in {"", "nan", "none", "unclassified", "uncultured", "incertae_sedis", "__"}:
        return ""
    if text.startswith("s__") or "t__" in text:
        return ""
    return text


def clean_species(value: object) -> str:
    import re

    text = str(value).strip()
    match = re.search(r"s__([^;|]+)", text)
    if match:
        text = match.group(1)
    elif re.search(r"(^|[|])[a-z]__", text) and "s__" not in text:
        return ""
    text = text.strip().lower().replace(" ", "_")
    if text in {"", "nan", "none", "unclassified", "uncultured"} or text.endswith("_sp"):
        return ""
    if len(text) < 5 or text in {"bacteria", "archaea"}:
        return ""
    return text


def read_table(path: Path) -> pd.DataFrame | None:
    try:
        if path.stat().st_size > 40_000_000:
            return None
        sep = "," if path.suffix.lower() == ".csv" else "\t"
        skip = []
        with path.open("r", errors="replace") as handle:
            for index, line in enumerate(handle):
                if index > 30:
                    break
                stripped = line.lstrip()
                if stripped.startswith("#OTU") or stripped.startswith("#OTUID"):
                    break
                if stripped.startswith("#"):
                    skip.append(index)
                    continue
                break
        frame = pd.read_csv(path, sep=sep, dtype=str, skiprows=skip or None)
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeError):
        return None
    if frame.shape[1] < 2 or frame.shape[0] < 1:
        return None
    first = str(frame.columns[0])
    if first.startswith("#"):
        frame = frame.rename(columns={frame.columns[0]: first.lstrip("#").strip()})
    return frame


def as_relative_abundance(matrix: pd.DataFrame) -> pd.DataFrame:
    """Return each sample's share of its original table.

    One decision covers the whole table, and it is made before taxon names
    are filtered. A merged table has one row per sample, so a count table is
    divided by that sample's own total. A percent table is divided by 100.
    An abundance table that already sums to about 1 is unchanged.
    """
    numeric = matrix.apply(pd.to_numeric, errors="coerce").fillna(0.0).clip(lower=0)
    sums = numeric.sum(axis=1)
    positive = sums[sums > 0]
    if positive.empty:
        return numeric
    median_sum = float(positive.median())
    maximum = float(numeric.to_numpy().max())
    if median_sum <= 1.5:
        return numeric
    if maximum <= 100 and 50 <= median_sum <= 150:
        return numeric / 100.0
    return numeric.div(sums.where(sums > 0), axis=0).fillna(0.0)


def orient_abundance(frame: pd.DataFrame, kind: str) -> pd.DataFrame | None:
    cleaner = clean_genus if kind == "genus" else clean_species
    working = frame.copy()
    first = working.columns[0]
    if str(first).startswith("Unnamed") or str(first) in {"", "clade", "clade_name", "genus", "species", "taxon"}:
        working = working.set_index(first)
    elif working.index.dtype == object:
        pass
    else:
        working = working.set_index(first)
    column_samples = [canon_sample(col) for col in working.columns]
    index_samples = [canon_sample(idx) for idx in working.index]
    if sum(bool(item) for item in column_samples) >= 30:
        renamed = working.copy()
        renamed.columns = column_samples
        renamed = renamed.loc[:, [col for col in renamed.columns if col]]
        renamed = renamed.T
        sample_axis = "columns_were_samples"
    elif sum(bool(item) for item in index_samples) >= 30:
        renamed = working.copy()
        renamed.index = index_samples
        renamed = renamed.loc[[idx for idx in renamed.index if idx]]
        sample_axis = "index_were_samples"
    else:
        return None
    renamed.index = renamed.index.astype(str)
    renamed = renamed[~renamed.index.duplicated(keep="first")]
    proportions = as_relative_abundance(renamed)
    proportions.columns = [cleaner(col) or "__other__" for col in proportions.columns]
    proportions = proportions.groupby(proportions.columns, axis=1).sum()
    if "__other__" in proportions.columns:
        proportions = proportions.drop(columns=["__other__"])
    if proportions.shape[1] < 1 or proportions.shape[0] < 30:
        return None
    return proportions


def composition_candidates(analysis: Path, kind: str) -> list[Path]:
    found = []
    for path in sr.walk_files(analysis):
        if path.suffix.lower() not in {".tsv", ".csv", ".txt"}:
            continue
        rel = str(path.relative_to(analysis)).lower()
        if any(bad in rel for bad in ("deseq", "maaslin", "lefse", "ancom", "significant", "pathway", "by_cultivar", "by_timepoint", "/features/", "phylum", "class", "order", "family")):
            continue
        if "diff" in rel and not any(token in path.name.lower() for token in ("count", "relab", "composition", "abundance", "proportion", "genus_table")):
            continue
        if kind == "genus":
            if any(bad in rel for bad in ("shotgun", "metaphlan", "species")):
                continue
            if "genus" not in rel:
                continue
        else:
            if "16s" in rel or "genus" in rel:
                continue
            if "species" not in rel and "merged_abundance" not in rel:
                continue
        if not any(key in rel for key in ("relab", "relative", "relabund", "composition", "count", "merged_abundance", "proportion", "genus_table")):
            continue
        found.append(path)
    return found


def best_composition(analysis: Path, kind: str) -> tuple[pd.DataFrame | None, str]:
    best = None
    source = ""
    best_key = None
    for path in composition_candidates(analysis, kind):
        frame = read_table(path)
        if frame is None:
            continue
        matrix = orient_abundance(frame, kind)
        if matrix is None:
            continue
        key = (abs(matrix.shape[0] - (60 if kind == "genus" else 36)), -matrix.shape[1])
        if best_key is None or key < best_key:
            best_key = key
            best = matrix
            source = str(path.relative_to(analysis))
    if best is not None:
        return best, source
    if kind == "genus":
        collapsed, source = collapse_asv_genus(analysis)
        if collapsed is not None:
            return collapsed, source
        return genus_level_biom(analysis)
    return merge_metaphlan_profiles(analysis)


def collapse_asv_genus(analysis: Path) -> tuple[pd.DataFrame | None, str]:
    import h5py

    taxonomy = None
    tax_source = ""
    for path in sr.walk_files(analysis):
        rel = str(path.relative_to(analysis)).lower()
        if path.suffix.lower() not in {".tsv", ".txt"}:
            continue
        if "taxonomy.tsv" not in rel or "silva" in rel or "ref_" in rel:
            continue
        frame = read_table(path)
        if frame is None or frame.shape[0] < 1000:
            continue
        taxonomy = frame
        tax_source = str(path.relative_to(analysis))
        break
    if taxonomy is None:
        return None, ""
    columns = {str(col).lower(): col for col in taxonomy.columns}
    id_col = columns.get("feature id", taxonomy.columns[0])
    tax_col = columns.get("taxon", taxonomy.columns[1] if taxonomy.shape[1] > 1 else taxonomy.columns[0])
    genus_of = {}
    for feature_id, taxon in zip(taxonomy[id_col], taxonomy[tax_col]):
        genus = clean_genus(taxon)
        if genus:
            genus_of[str(feature_id)] = genus
    biom_path = None
    asv_text = None
    for path in sr.walk_files(analysis):
        rel = str(path.relative_to(analysis)).lower()
        if path.name == "feature-table.biom" and "16s" in rel:
            biom_path = path
            break
        if path.suffix.lower() == ".tsv" and "asv_table" in path.name.lower() and path.stat().st_size < 40_000_000:
            asv_text = path
    totals: dict[tuple[str, str], float] = {}
    sample_sum: dict[str, float] = {}
    source = ""
    if biom_path is not None:
        with h5py.File(biom_path, "r") as handle:
            observations = [item.decode() if isinstance(item, bytes) else str(item) for item in handle["observation/ids"][:]]
            samples = [item.decode() if isinstance(item, bytes) else str(item) for item in handle["sample/ids"][:]]
            data = handle["observation/matrix/data"][:]
            indices = handle["observation/matrix/indices"][:]
            indptr = handle["observation/matrix/indptr"][:]
        for row_i, asv in enumerate(observations):
            genus = genus_of.get(asv, "")
            start, end = int(indptr[row_i]), int(indptr[row_i + 1])
            for cursor in range(start, end):
                sample = canon_sample(samples[int(indices[cursor])])
                if not sample:
                    continue
                amount = float(data[cursor])
                sample_sum[sample] = sample_sum.get(sample, 0.0) + amount
                if genus and amount:
                    totals[(sample, genus)] = totals.get((sample, genus), 0.0) + amount
        source = f"{biom_path.relative_to(analysis)} + {tax_source}"
    elif asv_text is not None:
        frame = read_table(asv_text)
        if frame is None:
            return None, ""
        raw = frame.copy()
        id_name = raw.columns[0]
        if "otu" in str(id_name).lower() or str(raw.iloc[0, 0]).startswith("#") or not canon_sample(raw.columns[1] if len(raw.columns) > 1 else ""):
            if str(raw.columns[0]).startswith("#") or "otu" in str(raw.columns[0]).lower() or not canon_sample(str(raw.columns[1])):
                pass
        # Standard QIIME export: first column ASV, remaining columns samples.
        asv_ids = raw.iloc[:, 0].astype(str)
        sample_ids = [canon_sample(col) for col in raw.columns[1:]]
        values = raw.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        for row_i, asv in enumerate(asv_ids):
            genus = genus_of.get(asv, "")
            for col_i, sample in enumerate(sample_ids):
                if not sample:
                    continue
                amount = float(values.iat[row_i, col_i])
                if not amount:
                    continue
                sample_sum[sample] = sample_sum.get(sample, 0.0) + amount
                if genus:
                    totals[(sample, genus)] = totals.get((sample, genus), 0.0) + amount
        source = f"{asv_text.relative_to(analysis)} + {tax_source}"
    else:
        return None, ""
    if not totals:
        return None, ""
    records = pd.Series(totals).unstack(fill_value=0.0)
    for sample, denom in sample_sum.items():
        if sample in records.index and denom > 0:
            records.loc[sample] = records.loc[sample] / denom
    if records.shape[0] < 30 or records.shape[1] < 1:
        return None, ""
    return records, source


def _profile_records(path: Path) -> list[tuple[str, float]]:
    records = []
    for line in path.read_text(errors="replace").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            amount = float(parts[2])
        except ValueError:
            continue
        records.append((parts[0], amount))
    return records


def _species_from_profile(path: Path) -> list[tuple[str, float]]:
    """Species values from one sample file, on the file's own scale.

    UNKNOWN is ignored when deciding the scale, because some profiles store
    that line as a percentage and the clade lines as proportions. A percent
    file is divided by 100. A count file is divided by the sum of its own
    species rows. Species that fail the name filter are removed afterwards.
    """
    rows = _profile_records(path)
    taxonomic = [
        amount
        for clade, amount in rows
        if amount > 0 and clade.strip().upper() not in {"UNKNOWN", "UNCLASSIFIED"}
    ]
    maximum = max(taxonomic) if taxonomic else 0.0
    species_rows: list[tuple[str, float]] = []
    for clade, amount in rows:
        if amount <= 0 or "|s__" not in clade or "|t__" in clade:
            continue
        species_rows.append((clean_species(clade), amount))
    if not species_rows:
        return []
    if maximum > 100:
        denom = sum(amount for _name, amount in species_rows)
        if denom <= 0:
            return []
        return [(name, amount / denom) for name, amount in species_rows if name]
    if maximum > 1.5:
        return [(name, amount / 100.0) for name, amount in species_rows if name]
    return [(name, amount) for name, amount in species_rows if name]


def merge_metaphlan_profiles(analysis: Path) -> tuple[pd.DataFrame | None, str]:
    profiles = [
        path
        for path in sr.walk_files(analysis)
        if "metaphlan" in str(path.relative_to(analysis)).lower() and path.name.lower().endswith("_profile.txt")
    ]
    if len(profiles) < 30:
        return None, ""
    totals: dict[tuple[str, str], float] = {}
    for path in profiles:
        sample = canon_sample(path.name[: -len("_profile.txt")])
        if not sample:
            continue
        for species, amount in _species_from_profile(path):
            totals[(sample, species)] = totals.get((sample, species), 0.0) + amount
    if not totals:
        return None, ""
    records = pd.Series(totals).unstack(fill_value=0.0)
    if records.shape[0] < 30 or records.shape[1] < 1:
        return None, ""
    source = str(profiles[0].parent.relative_to(analysis)) + "/*_profile.txt"
    return records, source


def genus_level_biom(analysis: Path) -> tuple[pd.DataFrame | None, str]:
    import h5py

    best = None
    source = ""
    best_key = None
    for path in sr.walk_files(analysis):
        rel = str(path.relative_to(analysis)).lower()
        if path.suffix.lower() != ".biom" or "16s" not in rel:
            continue
        try:
            with h5py.File(path, "r") as handle:
                observations = [item.decode() if isinstance(item, bytes) else str(item) for item in handle["observation/ids"][:]]
                if not any("g__" in item for item in observations[:30]):
                    continue
                samples = [item.decode() if isinstance(item, bytes) else str(item) for item in handle["sample/ids"][:]]
                data = handle["observation/matrix/data"][:]
                indices = handle["observation/matrix/indices"][:]
                indptr = handle["observation/matrix/indptr"][:]
        except (OSError, KeyError):
            continue
        totals: dict[tuple[str, str], float] = {}
        sample_sum: dict[str, float] = {}
        for row_i, label in enumerate(observations):
            genus = clean_genus(label)
            start, end = int(indptr[row_i]), int(indptr[row_i + 1])
            for cursor in range(start, end):
                sample = canon_sample(samples[int(indices[cursor])])
                if not sample:
                    continue
                amount = float(data[cursor])
                sample_sum[sample] = sample_sum.get(sample, 0.0) + amount
                if genus and amount:
                    totals[(sample, genus)] = totals.get((sample, genus), 0.0) + amount
        if not totals:
            continue
        records = pd.Series(totals).unstack(fill_value=0.0)
        for sample, denom in sample_sum.items():
            if sample in records.index and denom > 0:
                records.loc[sample] = records.loc[sample] / denom
        if records.shape[0] < 30 or records.shape[1] < 1:
            continue
        key = (abs(records.shape[0] - 60), -records.shape[1])
        if best_key is None or key < best_key:
            best_key = key
            best = records
            source = str(path.relative_to(analysis))
    if best is None:
        return None, ""
    return best, source


def column_lookup(frame: pd.DataFrame) -> dict[str, str]:
    return {"".join(ch for ch in str(col).lower() if ch.isalnum()): col for col in frame.columns}


def pick(mapping: dict[str, str], options: tuple[str, ...]) -> str | None:
    for option in options:
        if option in mapping:
            return mapping[option]
    return None


def resistance_mask(frame: pd.DataFrame, path: Path) -> pd.Series:
    mapping = column_lookup(frame)
    fields = [
        mapping[key]
        for key in ("metadata", "value", "name", "comparison", "contrast", "focal", "focalcultivar", "enrichedin", "direction")
        if key in mapping
    ]
    if not fields:
        return pd.Series(True, index=frame.index)
    text = frame[fields].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
    text = text + " " + path.name.lower()
    keep = text.str.contains(r"resist|pheno|hg64|hf12|suscept", regex=True)
    return keep


def parse_lfc_table(path: Path) -> pd.DataFrame | None:
    frame = read_table(path)
    if frame is None:
        return None
    mapping = column_lookup(frame)
    lfc_col = None
    for key in ("log2foldchange", "log2fc", "log2fcapprox"):
        if key in mapping:
            lfc_col = mapping[key]
            break
    if lfc_col is None:
        for key, original in mapping.items():
            if "se" in key or "stderr" in key or "pvalue" in key:
                continue
            if key.startswith("log2fc") or key.startswith("log2fold") or key == "lfc" or key.startswith("lfcvs"):
                lfc_col = original
                break
    if lfc_col is None:
        return None
    taxon_col = pick(mapping, ("genus", "species", "taxon", "feature", "label"))
    if taxon_col is None:
        return None
    work = frame.loc[resistance_mask(frame, path)].copy()
    if "model" in mapping:
        model = work[mapping["model"]].fillna("").astype(str).str.lower()
        if model.str.contains("abund").any():
            work = work.loc[model.str.contains("abund")]
    if work.empty:
        return None
    effects = pd.to_numeric(work[lfc_col], errors="coerce")
    names = work[taxon_col].astype(str)
    genus = names.map(clean_genus)
    species = names.map(clean_species)
    rel = str(path).lower()
    if "species" in path.name.lower() or "shotgun" in rel or "metaphlan" in rel:
        rank = "species"
        taxa = species
    elif "genus" in path.name.lower() or "16s" in rel:
        rank = "genus"
        taxa = genus
    else:
        genus_n = int((genus.to_numpy() != "").sum())
        species_n = int((species.to_numpy() != "").sum())
        rank = "species" if species_n > genus_n else "genus"
        taxa = species if rank == "species" else genus
    effect_array = effects.to_numpy(dtype=float)
    finite = np.isfinite(effect_array)
    parsed = pd.DataFrame({"taxon": taxa.to_numpy(), "log2fc": effect_array, "rank": rank})
    parsed = parsed.iloc[np.flatnonzero((parsed["taxon"].to_numpy() != "") & finite)]
    if parsed.empty:
        return None
    parsed["finite_fraction"] = float(np.mean(finite))
    return parsed


def best_lfc(analysis: Path, rank: str) -> tuple[pd.DataFrame | None, str, str]:
    best = None
    source = ""
    note = ""
    best_n = 0
    for path in da_candidates(analysis):
        if "annotated" in path.name.lower():
            continue
        parsed = parse_lfc_table(path)
        if parsed is None:
            continue
        parsed = parsed.loc[parsed["rank"] == rank]
        if parsed.empty:
            continue
        hash_like = parsed["taxon"].str.fullmatch(r"[0-9a-f]{16,}").mean()
        if hash_like > 0.2:
            continue
        fraction = float(parsed["finite_fraction"].iloc[0])
        if fraction < 0.5:
            continue
        collapsed = parsed.groupby("taxon", as_index=False)["log2fc"].median()
        n_taxa = int(len(collapsed))
        if n_taxa > best_n:
            best_n = n_taxa
            best = collapsed
            source = str(path.relative_to(analysis))
            note = f"taxa={n_taxa}; rows_in_file={len(parsed)}"
    if best is None:
        return None, "", "no log2FC table"
    return best, source, note


def da_candidates(analysis: Path) -> list[Path]:
    found = []
    for path in sr.walk_files(analysis):
        if path.suffix.lower() not in {".tsv", ".csv"}:
            continue
        rel = str(path.relative_to(analysis)).lower()
        name = path.name.lower()
        if any(bad in rel for bad in ("/features/", "pathway", "picrust", "humann", "relab", "bowtie")):
            continue
        if any(bad in name for bad in ("core_bio", "biomarker", "upset", "concordance", "summary_count")):
            continue
        if not any(key in rel for key in ("deseq", "maaslin", "lefse", "ancom", "diffab", "differential", "daa", "16s-da", "16s_da", "shotgun-da", "shotgun_da", "16s-de", "shotgun-de")):
            continue
        if any(token in name for token in ("significant", "sig_", "_sig", "top")) and "all" not in name:
            continue
        found.append(path)
    return found


def session_sample_taxon(matrix: pd.DataFrame) -> pd.Series:
    """One relative abundance per sample–taxon pair in a single session."""
    stacked = matrix.stack(dropna=True)
    values = pd.to_numeric(stacked, errors="coerce")
    finite = np.isfinite(values.to_numpy(dtype=float))
    values = values.loc[finite]
    values.index = pd.MultiIndex.from_tuples(
        [(str(sample_id), str(taxon)) for sample_id, taxon in values.index],
        names=["sample_id", "taxon"],
    )
    return values.groupby(level=["sample_id", "taxon"]).sum()


def mean_across_sessions(parts: list[pd.Series]) -> pd.Series:
    """Average sessions that reported each sample–taxon pair. Do not zero-fill gaps."""
    reported = [part for part in parts if part is not None and len(part)]
    if not reported:
        return pd.Series(dtype=float)
    return pd.concat(reported, axis=1).mean(axis=1, skipna=True)


ABUNDANCE_FLOOR = {
    "16s_composition": 5e-2,
    "shotgun_composition": 5e-2,
}


def abundance_floor(groups: dict[str, pd.Series], floor: float) -> dict[str, pd.Series]:
    """Keep pairs whose session-mean relative abundance reaches the floor."""
    kept = {}
    for key, series in groups.items():
        if series is None or not len(series):
            continue
        passed = series[series.to_numpy(dtype=float) >= floor]
        if len(passed):
            kept[key] = passed
    return kept


def compositional_session(matrix: pd.DataFrame) -> pd.Series:
    """Relative abundance per sample–taxon pair from the original table.

    Name filtering has already removed unnamed taxa. The remaining values are
    not scaled to 1.
    """
    stacked = session_sample_taxon(matrix).clip(lower=0)
    if not len(stacked):
        return stacked
    return stacked[stacked > 0]


def mean_profiles(parts: list[pd.Series]) -> pd.Series:
    """Session-mean composition. A taxon missing from a session that has the sample is 0."""
    by_sample: dict[str, list[pd.Series]] = {}
    for part in parts:
        if part is None or not len(part):
            continue
        for sample_id, sub in part.groupby(level="sample_id"):
            by_sample.setdefault(str(sample_id), []).append(sub.droplevel("sample_id"))
    records = []
    for sample_id, sessions in by_sample.items():
        taxa = sorted(set().union(*(set(series.index) for series in sessions)))
        mat = np.zeros((len(sessions), len(taxa)), dtype=float)
        for row_i, series in enumerate(sessions):
            mat[row_i] = series.reindex(taxa).fillna(0.0).to_numpy(dtype=float)
        for taxon, value in zip(taxa, mat.mean(axis=0)):
            if value > 0:
                records.append((sample_id, taxon, float(value)))
    if not records:
        return pd.Series(dtype=float)
    index = pd.MultiIndex.from_tuples([(sample_id, taxon) for sample_id, taxon, _value in records], names=["sample_id", "taxon"])
    return pd.Series([value for _sample_id, _taxon, value in records], index=index)


def shared_positive(groups: dict[str, pd.Series]) -> tuple[list, dict[str, np.ndarray]]:
    """Keep pairs that are non-positive in no group, so a log axis stays defined."""
    present = {key: series for key, series in groups.items() if len(series)}
    if len(present) < 2:
        return [], {}
    shared = None
    for series in present.values():
        positive = series.index[series.to_numpy(dtype=float) > 0]
        keys = set(positive.tolist())
        shared = keys if shared is None else shared & keys
    if not shared:
        return [], {key: np.array([], dtype=float) for key in present}
    ordered = sorted(shared)
    index = pd.MultiIndex.from_tuples(ordered, names=["sample_id", "taxon"])
    return ordered, {key: series.reindex(index).to_numpy(dtype=float) for key, series in present.items()}


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    jobs = pd.read_csv(sr.JOBS)
    rows = []
    coverage = []
    da_store = {}
    comp_store = {}
    for row in jobs.itertuples(index=False):
        analysis = sr.ROOT / row.job_id / "analysis"
        print(f"extract {row.session}", flush=True)
        for kind, task in (("genus", "16s_composition"), ("species", "shotgun_composition")):
            matrix, source = best_composition(analysis, kind)
            n_taxa = 0 if matrix is None else int(matrix.shape[1])
            n_samples = 0 if matrix is None else int(matrix.shape[0])
            comp_store[(row.session, task)] = matrix
            coverage.append(
                {
                    "session": row.session,
                    "level": row.level,
                    "model": row.model,
                    "task": task,
                    "n": n_taxa,
                    "source": source,
                    "note": f"samples={n_samples}",
                }
            )
        for rank, task in (("genus", "16s_da"), ("species", "shotgun_da")):
            table, source, note = best_lfc(analysis, rank)
            da_store[(row.session, task)] = table
            coverage.append(
                {
                    "session": row.session,
                    "level": row.level,
                    "model": row.model,
                    "task": task,
                    "n": 0 if table is None else int(table["taxon"].nunique()),
                    "source": source,
                    "note": note,
                }
            )
    for level in LEVEL_ORDER:
        level_sessions = list(jobs.loc[jobs["level"] == level, "session"])
        for task in ("16s_composition", "shotgun_composition"):
            present = [session for session in level_sessions if comp_store.get((session, task)) is not None]
            if len(present) < 2:
                continue
            by_model: dict[str, list[pd.Series]] = {model: [] for model in MODEL_ORDER}
            for session in present:
                model = jobs.loc[jobs["session"] == session, "model"].iloc[0]
                by_model[model].append(compositional_session(comp_store[(session, task)]))
            model_means = {
                model: mean_profiles(parts)
                for model, parts in by_model.items()
                if parts
            }
            ordered, kept = shared_positive(abundance_floor(model_means, ABUNDANCE_FLOOR[task]))
            print(
                f"{level} {task}: models={len(kept)} shared_sample_taxa={len(ordered)} sessions={len(present)}",
                flush=True,
            )
            if len(ordered) < 1:
                continue
            for model, values in kept.items():
                for (sample_id, taxon), value in zip(ordered, values):
                    rows.append(
                        {
                            "session": "",
                            "replicate": "",
                            "level": level,
                            "model": model,
                            "task": task,
                            "unit": f"{sample_id}|{taxon}",
                            "value": float(value),
                            "source": "",
                        }
                    )
        for task in ("16s_da", "shotgun_da"):
            present = []
            for session in level_sessions:
                table = da_store.get((session, task))
                if table is not None and table["taxon"].nunique() >= 1:
                    present.append(session)
            if len(present) < 2:
                continue
            session_means = {}
            for session in present:
                table = da_store[(session, task)]
                grouped = table.groupby("taxon")["log2fc"].mean()
                session_means[session] = {
                    taxon: float(value)
                    for taxon, value in grouped.items()
                    if np.isfinite(value)
                }
            model_values = {model: {} for model in MODEL_ORDER}
            for session, mapping in session_means.items():
                model = jobs.loc[jobs["session"] == session, "model"].iloc[0]
                for taxon, value in mapping.items():
                    model_values[model].setdefault(taxon, []).append(value)
            model_means = {
                model: {taxon: float(np.mean(vals)) for taxon, vals in bucket.items()}
                for model, bucket in model_values.items()
                if bucket
            }
            present_models = [model for model in MODEL_ORDER if model in model_means]
            if len(present_models) < 2:
                continue
            shared = set.intersection(*(set(model_means[model]) for model in present_models))
            print(f"{level} {task}: models={len(present_models)} shared_taxa={len(shared)} sessions={len(present)}", flush=True)
            if len(shared) < 1:
                continue
            for model in present_models:
                for taxon in sorted(shared):
                    rows.append(
                        {
                            "session": "",
                            "replicate": "",
                            "level": level,
                            "model": model,
                            "task": task,
                            "unit": taxon,
                            "value": float(model_means[model][taxon]),
                            "source": "",
                        }
                    )
    return pd.DataFrame.from_records(rows), pd.DataFrame.from_records(coverage)


def mannwhitney_table(values: pd.DataFrame) -> pd.DataFrame:
    from scipy import stats

    records = []
    for (task, level), group in values.groupby(["task", "level"], sort=False):
        raw = []
        bundles = []
        for left, right in PAIRS:
            a = group.loc[group["model"] == left, "value"].to_numpy(dtype=float)
            b = group.loc[group["model"] == right, "value"].to_numpy(dtype=float)
            if len(a) < 5 or len(b) < 5:
                pvalue = np.nan
                stat = np.nan
            else:
                result = stats.mannwhitneyu(a, b, alternative="two-sided")
                pvalue = float(result.pvalue)
                stat = float(result.statistic)
            raw.append(pvalue)
            bundles.append((left, right, a, b, stat, pvalue))
        usable = [i for i, pvalue in enumerate(raw) if np.isfinite(pvalue)]
        adjusted = holm([raw[i] for i in usable]) if usable else []
        holm_p = [np.nan] * len(raw)
        for slot, value in zip(usable, adjusted):
            holm_p[slot] = value
        for (left, right, a, b, stat, pvalue), p_holm in zip(bundles, holm_p):
            records.append(
                {
                    "task": task,
                    "level": level,
                    "model_a": left,
                    "model_b": right,
                    "n_a": int(len(a)),
                    "n_b": int(len(b)),
                    "median_a": float(np.median(a)) if len(a) else np.nan,
                    "median_b": float(np.median(b)) if len(b) else np.nan,
                    "u_statistic": stat,
                    "p_raw": pvalue,
                    "p_holm": p_holm,
                }
            )
    return pd.DataFrame.from_records(records)


def _fmt_bracket_p(value: float) -> str:
    """Holm-adjusted p as n.s. or asterisks: * <0.05, ** <0.01, *** <0.001."""
    if not np.isfinite(value):
        return "n.a."
    if value >= 0.05:
        return "n.s."
    if value >= 0.01:
        return "*"
    if value >= 0.001:
        return "**"
    return "***"


def _points_above_spine(ax: plt.Axes, y_pt: float):
    """Data x, with y measured in points above the top spine."""
    base = mpl.transforms.blended_transform_factory(ax.transData, ax.transAxes)
    shift = mpl.transforms.ScaledTranslation(0, y_pt / 72.0, ax.figure.dpi_scale_trans)
    return base + shift



def _pair_p(panel_tests: pd.DataFrame, left: str, right: str) -> float:
    row = panel_tests[(panel_tests["model_a"] == left) & (panel_tests["model_b"] == right)]
    if row.empty:
        row = panel_tests[(panel_tests["model_a"] == right) & (panel_tests["model_b"] == left)]
    if row.empty:
        return np.nan
    return float(row["p_holm"].iloc[0])


def _add_bracket(ax: plt.Axes, x0: float, x1: float, y_pt: float, label: str) -> None:
    leg = 2.6
    height_pt = ax.get_position().height * ax.figure.get_size_inches()[1] * 72.0
    drop = leg / height_pt
    ax.add_line(
        mpl.lines.Line2D(
            [x0, x0, x1, x1],
            [1 - drop, 1, 1, 1 - drop],
            transform=_points_above_spine(ax, y_pt),
            color="#222222",
            linewidth=0.6,
            clip_on=False,
            solid_capstyle="butt",
            zorder=5,
            gid="sig-bracket",
        )
    )
    ax.text(
        (x0 + x1) / 2.0,
        1,
        label,
        transform=_points_above_spine(ax, y_pt + 0.8),
        ha="center",
        va="bottom",
        fontsize=7,
        color="#222222",
        clip_on=False,
        zorder=6,
        gid="sig-bracket",
    )


def _add_significance_brackets(ax: plt.Axes, present: list[str], panel_tests: pd.DataFrame, centers: list[float] | None = None) -> None:
    if centers is None:
        ticks = [float(pos) for pos in ax.get_xticks()]
        if len(ticks) < len(present):
            ticks = [float(i) for i in range(len(present))]
    else:
        ticks = centers
    adjacent_y = [3.2, 16.4]
    high_y = 28.4
    for i in range(len(present) - 1):
        _add_bracket(
            ax,
            ticks[i],
            ticks[i + 1],
            adjacent_y[min(i, len(adjacent_y) - 1)],
            _fmt_bracket_p(_pair_p(panel_tests, present[i], present[i + 1])),
        )
    if len(present) >= 3:
        _add_bracket(
            ax,
            ticks[0],
            ticks[len(present) - 1],
            high_y,
            _fmt_bracket_p(_pair_p(panel_tests, present[0], present[len(present) - 1])),
        )
    calls = getattr(ax, "_bracket_calls", None)
    if calls is None:
        calls = []
        ax._bracket_calls = calls
    calls.append((list(present), panel_tests, list(ticks)))


def _y_plus_points(ax: plt.Axes, y_value: float, points: float) -> float:
    """Data y that sits `points` above `y_value` at the current scale and limits."""
    _, displayed = ax.transData.transform((0.0, y_value))
    _, shifted = ax.transData.inverted().transform((0.0, displayed + points * ax.figure.dpi / 72.0))
    return float(shifted)


def _whisker_top(ax: plt.Axes) -> float:
    tops = []
    for line in ax.lines:
        if line.get_gid() == "sig-bracket":
            continue
        y_values = np.asarray(line.get_ydata(), dtype=float)
        y_values = y_values[np.isfinite(y_values)]
        if y_values.size:
            tops.append(float(y_values.max()))
    return max(tops) if tops else np.nan


def _ensure_bracket_headroom(ax: plt.Axes, points: float = 42.0) -> None:
    """Keep the whisker top far enough below the upper spine for the brackets."""
    top = _whisker_top(ax)
    if not np.isfinite(top) or (top <= 0 and ax.get_yscale() == "log"):
        return
    height_px = float(ax.get_window_extent().height)
    needed_px = points * ax.figure.dpi / 72.0
    if height_px <= needed_px + 8:
        return
    y0, y1 = ax.get_ylim()
    if ax.get_yscale() == "log":
        anchor, low, high = np.log10(top), np.log10(min(y0, y1)), np.log10(max(y0, y1))
    else:
        anchor, low, high = top, min(y0, y1), max(y0, y1)
    updated = (anchor * height_px - needed_px * low) / (height_px - needed_px)
    if updated <= high:
        return
    if ax.get_yscale() == "log":
        updated = 10.0 ** updated
    if y1 >= y0:
        ax.set_ylim(y0, updated)
    else:
        ax.set_ylim(updated, y0)


def _span_top(ax: plt.Axes, x0: float, x1: float) -> float:
    """Highest whisker between two box centers."""
    lo, hi = min(x0, x1) - 0.28, max(x0, x1) + 0.28
    tops = []
    for line in ax.lines:
        if line.get_gid() == "sig-bracket":
            continue
        x_values = np.asarray(line.get_xdata(), dtype=float)
        y_values = np.asarray(line.get_ydata(), dtype=float)
        keep = np.isfinite(x_values) & np.isfinite(y_values) & (x_values >= lo) & (x_values <= hi)
        if np.any(keep):
            tops.append(float(y_values[keep].max()))
    return max(tops) if tops else np.nan


def _display_y(ax: plt.Axes, y_value: float) -> float:
    return float(ax.transData.transform((0.0, y_value))[1])


def _bracket_jobs(ax: plt.Axes) -> list:
    """Bracket geometry in points above each comparison's own whiskers.

    Adjacent brackets stay on the 7 pt and 18 pt steps. When a taller box pulls
    those two steps onto each other, the upper bracket is opened to 16 pt.
    """
    specs = getattr(ax, "_bracket_calls", None) or []
    scale = ax.figure.dpi / 72.0
    jobs = []
    for present, panel_tests, ticks in specs:
        bars = []
        for i in range(len(present) - 1):
            top = _span_top(ax, ticks[i], ticks[i + 1])
            if not np.isfinite(top):
                continue
            base = 7.0 if i == 0 else 18.0
            anchor = _display_y(ax, top)
            bar = anchor + base * scale
            if bars and bar < bars[-1] + 9.0 * scale:
                bar = bars[-1] + 16.0 * scale
            bar = max(bar, anchor + 7.0 * scale)
            bars.append(bar)
            jobs.append(
                (
                    ticks[i],
                    ticks[i + 1],
                    top,
                    (bar - anchor) / scale,
                    _fmt_bracket_p(_pair_p(panel_tests, present[i], present[i + 1])),
                )
            )
        if len(present) >= 3:
            top = _span_top(ax, ticks[0], ticks[len(present) - 1])
            if not np.isfinite(top):
                continue
            anchor = _display_y(ax, top)
            bar = anchor + 29.0 * scale
            if bars and bar < max(bars) + 9.0 * scale:
                bar = max(bars) + 16.0 * scale
            jobs.append(
                (
                    ticks[0],
                    ticks[len(present) - 1],
                    top,
                    (bar - anchor) / scale,
                    _fmt_bracket_p(_pair_p(panel_tests, present[0], present[len(present) - 1])),
                )
            )
    return jobs


def _required_bracket_points(ax: plt.Axes) -> float:
    """Headroom, in points above the highest whisker, that fits every bracket label."""
    jobs = _bracket_jobs(ax)
    whisker = _whisker_top(ax)
    if not jobs or not np.isfinite(whisker):
        return 0.0
    scale = ax.figure.dpi / 72.0
    whisker_y = _display_y(ax, whisker)
    highest = max(_display_y(ax, top) + y_pt * scale for _x0, _x1, top, y_pt, _label in jobs)
    return (highest - whisker_y) / scale + 9.0


def place_brackets_above_data(ax: plt.Axes) -> None:
    """Redraw every group's significance brackets just above that group's whiskers."""
    specs = getattr(ax, "_bracket_calls", None)
    if not specs:
        return
    for artist in list(ax.lines) + list(ax.texts):
        if artist.get_gid() == "sig-bracket":
            artist.remove()
    needed = _required_bracket_points(ax)
    if needed > 42.0:
        _ensure_bracket_headroom(ax, points=needed)
    for x0, x1, top, y_pt, label in _bracket_jobs(ax):
        _add_bracket_above_data(ax, x0, x1, top, y_pt, label)


def _add_bracket_above_data(ax: plt.Axes, x0: float, x1: float, y_value: float, y_pt: float, label: str) -> None:
    leg = 2.4
    y_bar = _y_plus_points(ax, y_value, y_pt)
    y_leg = _y_plus_points(ax, y_value, y_pt - leg)
    ax.add_line(
        mpl.lines.Line2D(
            [x0, x0, x1, x1],
            [y_leg, y_bar, y_bar, y_leg],
            color="#222222",
            linewidth=0.6,
            clip_on=False,
            solid_capstyle="butt",
            zorder=5,
            gid="sig-bracket",
        )
    )
    ax.text(
        (x0 + x1) / 2.0,
        _y_plus_points(ax, y_value, y_pt + 0.6),
        label,
        ha="center",
        va="bottom",
        fontsize=7,
        color="#222222",
        clip_on=False,
        zorder=6,
        gid="sig-bracket",
    )


def _color_boxes(ax: plt.Axes, present: list[str]) -> None:
    for patch, model in zip(ax.artists, present):
        color = PALETTE[MODEL_LABEL[model]]
        patch.set_facecolor(color)
        patch.set_edgecolor(color)
        patch.set_alpha(0.85)
    for line in ax.lines:
        line.set_color("#222222")
        line.set_linewidth(0.6)


def draw(values: pd.DataFrame, tests: pd.DataFrame, tasks: list[tuple[str, str]], footnotes: tuple[str, ...], stem_name: str, ylims: tuple | None = None, log_y: bool = False, brackets: bool = False) -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.labelsize": 7,
            "axes.titlesize": 7,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.6,
            "legend.frameon": False,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
        }
    )
    fig, axes = plt.subplots(2, 3, figsize=(7.20, 6.15 if brackets else 5.60), sharey="row", constrained_layout=False)
    if brackets:
        fig.subplots_adjust(left=0.11, right=0.985, top=0.78, bottom=0.055, wspace=0.28, hspace=1.02)
    else:
        fig.subplots_adjust(left=0.11, right=0.985, top=0.86, bottom=0.13, wspace=0.28, hspace=0.48)
    letters = [["a", "b", "c"], ["d", "e", "f"]]
    for row_i, (task, ylabel) in enumerate(tasks):
        for col_i, level in enumerate(LEVEL_ORDER):
            ax = axes[row_i, col_i]
            sub = values[(values["task"] == task) & (values["level"] == level)].copy()
            present = [model for model in MODEL_ORDER if (sub["model"] == model).any()]
            counts = [int((sub["model"] == model).sum()) for model in MODEL_ORDER]
            if present:
                sub["model_label"] = sub["model"].map(MODEL_LABEL)
                sns.boxplot(
                    data=sub,
                    x="model_label",
                    y="value",
                    order=[MODEL_LABEL[model] for model in present],
                    ax=ax,
                    width=0.62,
                    fliersize=1.5,
                    linewidth=0.6,
                    color="white",
                    showfliers=not (ylims is not None and ylims[row_i] is not None),
                )
                _color_boxes(ax, present)
            else:
                ax.text(0.5, 0.5, "No comparable values", transform=ax.transAxes, ha="center", va="center", fontsize=7)
            panel_tests = tests[(tests["task"] == task) & (tests["level"] == level)]
            heading = LEVEL_LABEL[level] if row_i == 0 else ylabel
            if brackets:
                if len(present) >= 2:
                    _add_significance_brackets(ax, present, panel_tests)
                if row_i == 0:
                    ax.set_title(LEVEL_LABEL[level], pad=30)
                else:
                    ax.set_title("")
            else:
                p_text = "  ".join(_fmt_p(p) for p in panel_tests["p_holm"]) if len(panel_tests) else ""
                ax.set_title(f"{heading}\n{p_text}", pad=3)
            ax.set_xlabel("")
            ax.set_ylabel(ylabel if col_i == 0 else "")
            if present:
                ax.set_xticklabels([str(counts[MODEL_ORDER.index(model)]) for model in present])
            ax.tick_params(axis="x", length=0)
            if log_y:
                ax.set_yscale("log")
                ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda value, _pos: f"1e{int(round(np.log10(value)))}" if value > 0 else ""))
                ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
            if ylims is not None and ylims[row_i] is not None:
                ax.set_ylim(*ylims[row_i])
            ax.text(0.02, 0.98, letters[row_i][col_i], transform=ax.transAxes, ha="left", va="top", fontsize=8, fontweight="bold")
    handles = [
        Patch(facecolor=PALETTE[MODEL_LABEL[model]], edgecolor=PALETTE[MODEL_LABEL[model]], label=MODEL_LABEL[model])
        for model in MODEL_ORDER
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, bbox_to_anchor=(0.54, 0.985), frameon=False, handlelength=1.2, columnspacing=1.2)
    notes = [note for note in footnotes if note]
    if len(notes) == 1:
        fig.text(0.11, 0.018, notes[0], ha="left", va="bottom", fontsize=7)
    elif len(notes) >= 2:
        fig.text(0.11, 0.048, notes[0], ha="left", va="bottom", fontsize=7)
        fig.text(0.11, 0.012, notes[1], ha="left", va="bottom", fontsize=7)
    stem = FIGS / stem_name
    require_matplotlib_panel_alignment(
        fig,
        json_out=str(stem.with_suffix(".alignment.json")),
        overlay_svg=str(stem.with_suffix(".alignment.svg")),
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        strict=True,
    )
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    fig.savefig(stem.with_suffix(".tiff"), dpi=600)
    plt.close(fig)


def _frame_abundance_axis(ax: plt.Axes, floor: float) -> None:
    """Keep log ticks on the whisker range, starting just below the abundance floor."""
    ymin = float(ax.dataLim.ymin)
    ymax = float(ax.dataLim.ymax)
    if not np.isfinite(ymin) or not np.isfinite(ymax) or ymin <= 0 or ymax <= 0:
        return
    lo = 10 ** (np.log10(min(ymin, floor)) - 0.25)
    hi = 10 ** (np.log10(ymax) + 0.30)
    ax.set_ylim(lo, hi)
    ticks = [10.0 ** exp for exp in range(-4, 2) if lo < 10.0 ** exp < hi]
    if ticks:
        ax.set_yticks(ticks)


def _uses_log(task: str, log_y: bool | set[str]) -> bool:
    if isinstance(log_y, bool):
        return log_y
    return task in log_y


def draw_grouped(
    values: pd.DataFrame,
    tests: pd.DataFrame,
    tasks: list[tuple[str, str, str]],
    stem_name: str,
    log_y: bool | set[str] = True,
    axes=None,
    panel_letters: bool = True,
    legend: bool = True,
    save: bool = True,
) -> None:
    """One panel per quantity. Prompt names sit on x; models are adjacent boxes."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.labelsize": 7,
            "axes.titlesize": 7,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.6,
            "legend.frameon": False,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
        }
    )
    group_pitch = 1.10
    within = [-0.30, 0.0, 0.30]
    box_width = 0.16
    n_panels = len(tasks)
    grid = n_panels == 4
    owns_figure = axes is None
    if not owns_figure:
        axes = list(np.ravel(axes))
        fig = axes[0].figure
    elif n_panels == 2:
        fig, axes = plt.subplots(2, 1, figsize=(6.20, 5.50), sharex=False, constrained_layout=False)
        fig.subplots_adjust(left=0.145, right=0.985, top=0.80, bottom=0.07, hspace=0.62)
    elif grid:
        fig, axes = plt.subplots(2, 2, figsize=(7.20, 6.10), sharex=False, constrained_layout=False)
        fig.subplots_adjust(left=0.11, right=0.985, top=0.84, bottom=0.055, wspace=0.32, hspace=0.68)
        axes = axes.ravel()
    else:
        axes_in = 1.38
        gap_in = 0.90
        top_in = 1.08
        bottom_in = 0.40
        fig_h = top_in + bottom_in + n_panels * axes_in + (n_panels - 1) * gap_in
        fig, axes = plt.subplots(n_panels, 1, figsize=(7.20, fig_h), sharex=False, constrained_layout=False)
        fig.subplots_adjust(
            left=0.11,
            right=0.985,
            top=1.0 - top_in / fig_h,
            bottom=bottom_in / fig_h,
            hspace=gap_in / axes_in,
        )
    if n_panels == 1:
        axes = [axes]
    letters = [chr(ord("a") + i) for i in range(n_panels)]
    for row_i, (task, ylabel, title) in enumerate(tasks):
        ax = axes[row_i]
        sub = values[values["task"] == task].copy()
        if sub.empty:
            ax.text(0.5, 0.5, "No comparable values", transform=ax.transAxes, ha="center", va="center", fontsize=7)
        else:
            for index, level in enumerate(LEVEL_ORDER):
                for model_i, model in enumerate(MODEL_ORDER):
                    series = sub.loc[(sub["level"] == level) & (sub["model"] == model), "value"].to_numpy(dtype=float)
                    if len(series) == 0:
                        continue
                    color = PALETTE[MODEL_LABEL[model]]
                    ax.boxplot(
                        [series],
                        positions=[index * group_pitch + within[model_i]],
                        widths=box_width,
                        patch_artist=True,
                        showfliers=False,
                        boxprops={"facecolor": color, "edgecolor": color, "linewidth": 0.6, "alpha": 0.85},
                        whiskerprops={"color": "#222222", "linewidth": 0.6},
                        capprops={"color": "#222222", "linewidth": 0.6},
                        medianprops={"color": "#222222", "linewidth": 0.6},
                    )
                present = [model for model in MODEL_ORDER if ((sub["level"] == level) & (sub["model"] == model)).any()]
                if len(present) < 2:
                    continue
                centers = [index * group_pitch + within[MODEL_ORDER.index(model)] for model in present]
                panel_tests = tests[(tests["task"] == task) & (tests["level"] == level)]
                _add_significance_brackets(ax, present, panel_tests, centers)
            ax.set_xticks([index * group_pitch for index in range(len(LEVEL_ORDER))])
            ax.set_xticklabels([LEVEL_LABEL[level] for level in LEVEL_ORDER])
            ax.set_xlim(-0.62, (len(LEVEL_ORDER) - 1) * group_pitch + 0.62)
        ax.set_xlabel("")
        ax.set_ylabel(ylabel)
        ax.set_title(title, pad=42)
        ax.tick_params(axis="x", which="both", labelbottom=True, length=0)
        if _uses_log(task, log_y):
            # abundance_floor already removed non-positive sample–taxon pairs.
            ax.set_yscale("log")
            ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda value, _pos: f"1e{int(round(np.log10(value)))}" if value > 0 else ""))
            ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
            if task in ABUNDANCE_FLOOR:
                _frame_abundance_axis(ax, ABUNDANCE_FLOOR[task])
        if panel_letters:
            ax.text(0.01, 0.98, letters[row_i], transform=ax.transAxes, ha="left", va="top", fontsize=8, fontweight="bold")
    if legend:
        handles = [
            Patch(facecolor=PALETTE[MODEL_LABEL[model]], edgecolor=PALETTE[MODEL_LABEL[model]], label=MODEL_LABEL[model])
            for model in MODEL_ORDER
        ]
        fig.legend(handles=handles, loc="upper center", ncol=3, bbox_to_anchor=(0.55, 0.985), frameon=False, handlelength=1.2, columnspacing=1.2)
    if not save:
        return
    stem = FIGS / stem_name
    require_matplotlib_panel_alignment(
        fig,
        json_out=str(stem.with_suffix(".alignment.json")),
        overlay_svg=str(stem.with_suffix(".alignment.svg")),
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        strict=True,
    )
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    fig.savefig(stem.with_suffix(".tiff"), dpi=600)
    plt.close(fig)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    values, coverage = extract()
    tests = mannwhitney_table(values)
    values.to_csv(TABLES / "composition_da_distribution_values.tsv", sep="\t", index=False)
    coverage.to_csv(TABLES / "composition_da_distribution_coverage.tsv", sep="\t", index=False)
    tests.to_csv(TABLES / "composition_da_distribution_tests.tsv", sep="\t", index=False)
    draw_grouped(
        values,
        tests,
        [
            ("16s_composition", "Genus relative abundance", "16S genus-level taxonomic profiling"),
            ("shotgun_composition", "Species relative abundance", "shotgun species-level taxonomic profiling"),
        ],
        "model_distribution_composition",
    )
    draw(
        values,
        tests,
        [("16s_da", "16S genus log2FC"), ("shotgun_da", "Shotgun species log2FC")],
        (
            "One session-averaged log2FC per genus or species shared across models.",
            "Holm p, left to right: glm5.3-flash vs deepseek-v4-flash; glm5.3-flash vs deepseek-v4-pro; deepseek-v4-flash vs deepseek-v4-pro.",
        ),
        "model_distribution_da",
    )
    print(coverage.to_string(index=False), flush=True)
    print(tests.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
