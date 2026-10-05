#!/usr/bin/env python3
"""Score Case 1 robustness sessions for artifact completion and repeatability.

Completion is an artifact score in {0, 0.5, 1} for four tasks. Concordance is
computed within each model x prompt cell (three independent sessions):

- 16S alpha: Pearson correlation of per-sample Shannon diversity
- 16S beta: Mantel correlation of a shared distance matrix
  (weighted UniFrac, otherwise Bray-Curtis, otherwise unweighted UniFrac)
- 16S and shotgun differential abundance: Jaccard overlap of
  resistance-associated calls (adjusted P < 0.05 when available, else P < 0.05)
"""

from __future__ import annotations

import itertools
import re
import zipfile
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path("/datahome/datasets/ericteam/cszmli/previous_results")
OUT = Path(
    "/datahome/datasets/ericteam/cszmli/openclaw-microbiome/papers/"
    "case_studies_design/case_study_1/robustness"
)
JOBS = OUT / "job_ids.csv"

TASKS = [
    "16s_alpha",
    "16s_beta",
    "16s_da",
    "shotgun_da",
]
TASK_LABEL = {
    "16s_alpha": "16S alpha diversity",
    "16s_beta": "16S beta diversity",
    "16s_da": "16S differential abundance",
    "shotgun_da": "Shotgun differential abundance",
}
BETA_PRIORITY = ("weighted_unifrac", "bray_curtis", "unweighted_unifrac")
MIN_SAMPLES = 30
Q_CUTOFF = 0.05
P_CUTOFF = 0.05
SKIP_DIR_PARTS = {
    "bowtie2",
    "bt2",
    "bt2out",
    "mpa_db",
    "provenance",
    "dist",
    "node_modules",
}
IMAGE_EXT = {".png", ".pdf", ".svg"}
TABLE_EXT = {".tsv", ".csv", ".txt"}
RESIST_RE = re.compile(r"hg64|hf12|resist", re.I)
TIME_RE = re.compile(r"T3C|T2C|T3|T2|T1")
RANK_RE = re.compile(r"^[a-z]__")


def canon_id(value: object) -> str:
    text = str(value).strip().strip('"').strip("'")
    text = text.replace(" ", "")
    return text.upper()


def clean_taxon(token: str) -> str:
    text = token.strip().strip('"').strip("'")
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = RANK_RE.sub("", text)
    text = text.replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9._+-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_.")
    return text.lower()


def norm_taxon(raw: object, kind: str) -> str:
    text = str(raw).strip()
    if not text or text.lower() in {"nan", "none", "na"}:
        return ""
    if kind == "16s":
        match = re.search(r"g__([^;|]+)", text)
        if match:
            return clean_taxon(match.group(1))
    else:
        match = re.search(r"s__([^;|]+)", text)
        if match:
            return clean_taxon(match.group(1))
    parts = re.split(r"[|;]", text)
    return clean_taxon(parts[-1])


def rel_parts(path: Path, job_root: Path) -> str:
    try:
        return str(path.relative_to(job_root)).replace("\\", "/")
    except ValueError:
        return str(path)


def walk_files(analysis: Path):
    for dirpath, dirnames, filenames in os_walk(analysis):
        dirnames[:] = [
            name
            for name in dirnames
            if name.lower() not in SKIP_DIR_PARTS
            and "retired" not in name.lower()
            and "superseded" not in name.lower()
        ]
        for name in filenames:
            yield Path(dirpath) / name


def os_walk(path: Path):
    import os

    return os.walk(path)


def read_text_table(path: Path) -> pd.DataFrame | None:
    try:
        blob = path.read_bytes()[:8000]
    except OSError:
        return None
    if b"\x00" in blob:
        return None
    sample = blob.decode("utf-8", errors="replace")
    if sample.count("\t") >= sample.count(","):
        sep = "\t"
    else:
        sep = ","
    try:
        frame = pd.read_csv(path, sep=sep, dtype=str, low_memory=False)
    except Exception:
        return None
    frame.columns = [str(col).strip().strip('"') for col in frame.columns]
    return frame


def qza_data_bytes(path: Path, suffix: str) -> bytes | None:
    if path.stat().st_size > 80_000_000:
        return None
    try:
        with zipfile.ZipFile(path) as archive:
            names = [
                name
                for name in archive.namelist()
                if "/data/" in name
                and "provenance" not in name
                and name.endswith(suffix)
            ]
            if not names:
                return None
            names.sort(key=len)
            return archive.read(names[0])
    except (OSError, zipfile.BadZipFile, KeyError):
        return None


def parse_shannon_frame(frame: pd.DataFrame) -> pd.Series | None:
    if frame is None or frame.empty:
        return None
    columns = {col.lower(): col for col in frame.columns}
    value_col = None
    for key, original in columns.items():
        if "shannon" in key:
            value_col = original
            break
    if value_col is None and frame.shape[1] == 1:
        value_col = frame.columns[0]
    if value_col is None:
        return None
    id_col = None
    for cand in ("sample_id", "sample-id", "sampleid", "sample", "#sampleid"):
        if cand in columns:
            id_col = columns[cand]
            break
    if id_col is None:
        unnamed = [col for col in frame.columns if col.lower().startswith("unnamed")]
        if unnamed and value_col != unnamed[0]:
            id_col = unnamed[0]
        elif frame.index.dtype == object:
            series = pd.to_numeric(frame[value_col], errors="coerce")
            series.index = [canon_id(idx) for idx in frame.index]
            series = series[~series.index.duplicated(keep="first")].dropna()
            return series if len(series) >= 10 else None
    if id_col is None:
        return None
    values = pd.to_numeric(frame[value_col], errors="coerce")
    ids = frame[id_col].map(canon_id)
    series = pd.Series(values.to_numpy(), index=ids)
    series = series[~series.index.isin({"", "NAN", "NONE"})]
    series = series[~series.index.duplicated(keep="first")].dropna()
    return series if len(series) >= 10 else None


def shannon_from_text(path: Path) -> pd.Series | None:
    frame = read_text_table(path)
    if frame is None:
        return None
    # QIIME2 alpha export keeps the sample id as the index column, which
    # pandas names "Unnamed: 0" when the header cell is blank.
    return parse_shannon_frame(frame)


def shannon_from_qza(path: Path) -> pd.Series | None:
    payload = qza_data_bytes(path, ".tsv")
    if payload is None:
        return None
    try:
        frame = pd.read_csv(StringIO(payload.decode("utf-8", errors="replace")), sep="\t", dtype=str)
    except Exception:
        return None
    return parse_shannon_frame(frame)


def looks_like_shannon_path(path: Path) -> bool:
    text = str(path).lower()
    if any(bad in text for bad in ("retired", "superseded", "faith", "observed", "evenness")):
        if "shannon" not in path.name.lower():
            return False
    name = path.name.lower()
    return "shannon" in name or name in {"alpha-diversity.tsv"}


def collect_shannon(analysis: Path) -> tuple[pd.Series | None, str]:
    best: pd.Series | None = None
    best_source = ""
    candidates: list[tuple[int, int, pd.Series, str]] = []
    for path in walk_files(analysis):
        if not looks_like_shannon_path(path):
            continue
        series = None
        if path.suffix.lower() == ".qza" and "shannon" in path.name.lower():
            series = shannon_from_qza(path)
        elif path.suffix.lower() in TABLE_EXT and path.stat().st_size < 5_000_000:
            series = shannon_from_text(path)
        if series is None or series.empty:
            continue
        # Prefer a full 60-sample vector, then larger vectors, then exported
        # tables over archived artifacts.
        penalty = 0 if path.suffix.lower() != ".qza" else 1
        distance = abs(len(series) - 60)
        candidates.append((distance, penalty, series, rel_parts(path, analysis.parent)))
    if not candidates:
        return best, best_source
    candidates.sort(key=lambda item: (item[0], item[1], -len(item[2])))
    _, _, best, best_source = candidates[0]
    return best, best_source


def read_distance_text(text: str) -> pd.DataFrame | None:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    if "\t" not in lines[0] and lines[0].strip().isdigit():
        lines = lines[1:]
    try:
        frame = pd.read_csv(StringIO("\n".join(lines)), sep="\t", index_col=0)
    except Exception:
        return None
    frame = frame.apply(pd.to_numeric, errors="coerce")
    frame = frame.dropna(axis=0, how="all").dropna(axis=1, how="all")
    if frame.shape[0] < 10 or frame.shape[0] != frame.shape[1]:
        return None
    frame.index = [canon_id(idx) for idx in frame.index]
    frame.columns = [canon_id(col) for col in frame.columns]
    shared = [idx for idx in frame.index if idx in set(frame.columns)]
    if len(shared) < 10:
        return None
    frame = frame.loc[shared, shared]
    frame = frame[~frame.index.duplicated(keep="first")]
    frame = frame.loc[:, ~frame.columns.duplicated(keep="first")]
    shared = [idx for idx in frame.index if idx in set(frame.columns)]
    frame = frame.loc[shared, shared]
    if frame.shape[0] < 10:
        return None
    return frame


def metric_from_path(path: Path) -> str | None:
    text = str(path).lower()
    if "unweighted" in text and "unifrac" in text:
        return "unweighted_unifrac"
    if "weighted" in text and "unifrac" in text:
        return "weighted_unifrac"
    if "bray" in text:
        return "bray_curtis"
    if "jaccard" in text:
        return "jaccard"
    return None


def collect_distances(analysis: Path) -> dict[str, tuple[pd.DataFrame, str]]:
    found: dict[str, tuple[int, int, pd.DataFrame, str]] = {}
    for path in walk_files(analysis):
        metric = metric_from_path(path)
        if metric is None or metric == "jaccard":
            continue
        if any(bad in str(path).lower() for bad in ("retired", "superseded")):
            continue
        frame = None
        if path.suffix.lower() == ".qza":
            payload = qza_data_bytes(path, "distance-matrix.tsv")
            if payload is None:
                continue
            frame = read_distance_text(payload.decode("utf-8", errors="replace"))
        elif path.suffix.lower() in TABLE_EXT and path.stat().st_size < 20_000_000:
            if "distance" not in path.name.lower() and "unifrac" not in path.name.lower() and "bray" not in path.name.lower():
                continue
            try:
                frame = read_distance_text(path.read_text(errors="replace"))
            except OSError:
                frame = None
        if frame is None:
            continue
        penalty = 0 if path.suffix.lower() != ".qza" else 1
        rank = (abs(frame.shape[0] - 60), penalty)
        current = found.get(metric)
        if current is None or rank < (current[0], current[1]):
            found[metric] = (rank[0], rank[1], frame, rel_parts(path, analysis.parent))
    return {metric: (payload[2], payload[3]) for metric, payload in found.items()}


def lower(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


TAXON_KEYS = {
    "taxon",
    "taxa",
    "feature",
    "genus",
    "species",
    "label",
    "otu",
    "asv",
    "organism",
}
Q_KEYS = {"padj", "qvalindividual", "qvalue", "qval", "fdr", "adjp", "p_adj"}
P_KEYS = {"pvalue", "pvalindividual", "pval", "p", "pvalueindividual"}
EFFECT_KEYS = {
    "log2foldchange",
    "log2fc",
    "log2fcapprox",
    "coef",
    "lfc",
    "effect",
    "effectsize",
}
TIME_KEYS = {"timepoint", "time", "tp"}
CONTRAST_KEYS = {
    "comparison",
    "contrast",
    "focal",
    "value",
    "metadata",
    "name",
    "group",
    "class",
    "direction",
    "coefname",
}


def column_map(frame: pd.DataFrame) -> dict[str, str]:
    mapping = {}
    for col in frame.columns:
        key = lower(col)
        mapping[key] = col
    return mapping


def pick_col(mapping: dict[str, str], options: set[str]) -> str | None:
    for key, original in mapping.items():
        if key in options:
            return original
    for key, original in mapping.items():
        if any(opt in key for opt in options if len(opt) > 3):
            return original
    return None


def is_da_path(path: Path) -> bool:
    text = str(path).lower()
    name = path.name.lower()
    if any(bad in text for bad in ("retired", "superseded", "/features/", "data_norm", "data_transformed", "filtered_data")):
        return False
    if any(bad in name for bad in ("count", "samplesx", "feature-table", "feature_table", "otu_table", "asv_table", "relabund")):
        return False
    if path.suffix.lower() not in TABLE_EXT | {".csv"}:
        return False
    try:
        if path.stat().st_size > 8_000_000 and "result" not in name:
            return False
    except OSError:
        return False
    keys = ("diff", "deseq", "maaslin", "ancom", "lefse", "significant", "/da", "_da", "-da")
    return any(key in text for key in keys)


def omics_of(path: Path, frame: pd.DataFrame | None = None) -> str | None:
    text = str(path).lower()
    if "pathway" in text or "picrust" in text or "humann" in text:
        return None
    if "16s" in text or "amplicon" in text:
        return "16s"
    if "shotgun" in text or "shot_" in text or "metaphlan" in text:
        return "shotgun"
    if "genus" in text and "species" not in text:
        return "16s"
    if re.search(r"(^|[_/-])species([_./-]|$)", text):
        return "shotgun"
    if frame is not None:
        names = " ".join(frame.columns).lower()
        if "genus" in names and "species" not in names:
            return "16s"
        if "species" in names:
            return "shotgun"
    return None


def bundle_key(path: Path) -> str:
    parent = path.parent
    parent_name = parent.name.lower()
    contrast_folder = bool(
        re.search(r"(^|[_\-])t[123]c?($|[_\-])", parent_name)
        or re.search(r"tp\d", parent_name)
        or re.search(r"vs[_\-]", parent_name)
        or parent_name in {"t1", "t2", "t2c", "t3", "t3c"}
    )
    if contrast_folder:
        return str(parent.parent)
    return str(parent)


def resistance_text(row: pd.Series, columns: list[str]) -> str:
    chunks = []
    for col in columns:
        if col in row.index:
            value = str(row[col])
            if value and value.lower() != "nan":
                chunks.append(value)
    return " ".join(chunks)


def extract_timepoint(row: pd.Series, time_col: str | None, contrast: str) -> str:
    if time_col and time_col in row.index:
        value = str(row[time_col]).strip()
        match = TIME_RE.search(value)
        if match:
            return match.group(0)
        if value and value.lower() not in {"nan", "none", "na"}:
            return value
    match = TIME_RE.search(contrast)
    return match.group(0) if match else "global"


def resolve_timepoint(raw: object, extra: object) -> str:
    for text in (str(raw), str(extra)):
        match = TIME_RE.search(text)
        if match:
            return match.group(0)
    raw_text = str(raw).strip()
    if raw_text and raw_text.lower() not in {"nan", "none", "na"}:
        return raw_text
    return "global"


def extract_focal(contrast: str) -> str:
    text = contrast.lower()
    focals = []
    if "hg64" in text:
        focals.append("hg64")
    if "hf12" in text:
        focals.append("hf12")
    if "resist" in text and not focals:
        focals.append("resistant")
    return "+".join(focals)


def parse_da_frame(frame: pd.DataFrame, kind: str, significant_file: bool, hint: str = "") -> pd.DataFrame | None:
    mapping = column_map(frame)
    if kind == "shotgun":
        taxon_order = ("species", "feature", "taxon", "taxa", "label", "organism")
    else:
        taxon_order = ("genus", "feature", "taxon", "taxa", "label", "otu", "asv", "organism")
    taxon_col = None
    for key in taxon_order:
        if key in mapping:
            taxon_col = mapping[key]
            break
    if taxon_col is None:
        return None
    q_col = pick_col(mapping, Q_KEYS)
    p_col = pick_col(mapping, P_KEYS)
    effect_col = pick_col(mapping, EFFECT_KEYS)
    time_col = pick_col(mapping, TIME_KEYS)
    contrast_cols = []
    for key, original in mapping.items():
        if key in {"genus", "species", "taxon", "taxa", "feature", "label", "otu", "asv", "organism"}:
            continue
        if key in CONTRAST_KEYS or any(
            token in key for token in ("focal", "contrast", "comparison", "phenotype", "cultivar", "enriched", "direction")
        ):
            contrast_cols.append(original)
    # `name` in MaAsLin is the coefficient name; keep it. A generic Name column
    # that duplicates the taxon is harmless because resistance matching is textual.
    model_col = mapping.get("model")
    work = frame
    if model_col:
        model_text = work[model_col].fillna("").astype(str)
        if model_text.str.contains("abundance", case=False, na=False).any():
            work = work.loc[model_text.str.contains("abundance", case=False, na=False)].copy()
        else:
            work = work.copy()
    else:
        work = work.copy()
    contrast_cols = list(dict.fromkeys(contrast_cols))
    if contrast_cols:
        contrast = work[contrast_cols[0]].fillna("").astype(str)
        for col in contrast_cols[1:]:
            contrast = contrast + " " + work[col].fillna("").astype(str)
    else:
        contrast = pd.Series("", index=work.index)
    keep = contrast.str.contains(r"hg64|hf12|resist", case=False, na=False)
    if not bool(keep.any()) and hint and RESIST_RE.search(hint):
        contrast = (contrast + " " + hint).str.strip()
        keep = contrast.str.contains(r"hg64|hf12|resist", case=False, na=False)
    work = work.loc[keep]
    contrast = contrast.loc[keep]
    if work.empty:
        return None
    taxa = [norm_taxon(value, kind) for value in work[taxon_col].tolist()]
    if "name" in mapping:
        coef_name = work[mapping["name"]].fillna("").astype(str)
    else:
        coef_name = contrast
    interaction = contrast.str.contains(":") | coef_name.str.contains(":")
    q_val = pd.to_numeric(work[q_col], errors="coerce") if q_col else pd.Series(np.nan, index=work.index)
    p_val = pd.to_numeric(work[p_col], errors="coerce") if p_col else pd.Series(np.nan, index=work.index)
    use_q = bool(q_val.notna().mean() >= 0.2)
    if significant_file:
        called = pd.Series(True, index=work.index)
        has_stat = q_val.notna() | p_val.notna()
        called = called.where(~has_stat, False)
    else:
        called = pd.Series(False, index=work.index)
    if use_q:
        called = called | (q_val < Q_CUTOFF)
    else:
        called = called | (p_val < P_CUTOFF)
        called = called | (~p_val.notna() & (q_val < Q_CUTOFF))
    effect = pd.to_numeric(work[effect_col], errors="coerce") if effect_col else pd.Series(np.nan, index=work.index)
    if time_col:
        time_src = work[time_col].fillna("").astype(str)
    else:
        time_src = pd.Series("", index=work.index)
    timepoint = [resolve_timepoint(raw, extra) for raw, extra in zip(time_src.tolist(), contrast.tolist())]
    parsed = pd.DataFrame(
        {
            "taxon": taxa,
            "timepoint": timepoint,
            "focal": [extract_focal(value) for value in contrast.tolist()],
            "interaction": interaction.to_numpy(),
            "called": called.fillna(False).to_numpy(dtype=bool),
            "effect": effect.to_numpy(),
            "q": q_val.to_numpy(),
            "p": p_val.to_numpy(),
        }
    )
    parsed = parsed[~parsed["taxon"].isin({"", "unassigned", "unclassified", "incertae_sedis"})]
    if parsed.empty:
        return None
    main = parsed[~parsed["interaction"]]
    if len(main):
        parsed = main
    return parsed


def _blocked_da(path: Path) -> bool:
    text = str(path).lower()
    return any(token in text for token in ("pathway", "picrust", "humann", "welch", "wilcox", "marker", "biomarker", "upset"))


def _level_penalty(path: Path, kind: str) -> int:
    text = str(path).lower()
    if kind == "16s":
        if "asv" in text or "otu" in text:
            return -2
        if "species" in text and "genus" not in text:
            return -1
        if "genus" in text:
            return 2
        return 0
    if "species" in text and "genus" not in text:
        return 2
    if "genus" in text and "species" not in text:
        return -2
    return 0


def _column_kind(frame: pd.DataFrame) -> str | None:
    columns = {lower(col) for col in frame.columns}
    if "genus" in columns and "species" not in columns:
        return "16s"
    if "species" in columns and "genus" not in columns:
        return "shotgun"
    if ("asv" in columns or "otu" in columns) and "species" not in columns:
        return "16s"
    return None


def _hash_fraction(frame: pd.DataFrame) -> float:
    if frame is None or frame.empty:
        return 0.0
    taxa = frame["taxon"].astype(str)
    hashes = taxa.str.fullmatch(r"[0-9a-f]{16,}", case=False)
    return float(hashes.mean())


def _choose_da_files(paths: list[Path], kind: str) -> tuple[list[Path], bool]:
    paths = [
        path
        for path in paths
        if not _blocked_da(path) and "annotated" not in path.name.lower() and path.stat().st_size > 30
    ]
    if not paths:
        return [], False
    preferred = [path for path in paths if _level_penalty(path, kind) > 0]
    if not preferred:
        preferred = [path for path in paths if _level_penalty(path, kind) >= 0]
    pool = preferred or paths

    def is_combined(path: Path) -> bool:
        name = path.name.lower()
        parent = path.parent.name.lower()
        # MaAsLin writes all_results.tsv inside each contrast directory.
        if name == "all_results.tsv" and re.search(r"vs[_\-]|tp\d|(^|[_\-])t[123]c?($|[_\-])", parent):
            return False
        return any(
            token in name
            for token in (
                "all_result",
                "all-result",
                "_all_results",
                "all_comparisons",
                "results_combined",
                "de_all",
                "da_genus_all",
                "da_species_all",
                "deseq-all",
                "deseq_all",
                "combined",
            )
        )

    combined = [path for path in pool if is_combined(path)]
    if combined:
        # Keep a single combined table so per-contrast files are not double counted.
        combined.sort(key=lambda path: (_level_penalty(path, kind), path.stat().st_size), reverse=True)
        return combined[:1], False
    per_contrast = [
        path
        for path in pool
        if RESIST_RE.search(path.name)
        or re.search(r"vs[_-]", path.name, re.I)
        or RESIST_RE.search(path.parent.name)
        or re.search(r"vs[_-]", path.parent.name, re.I)
    ]
    if per_contrast:
        full_tables = [
            path
            for path in per_contrast
            if path.name.lower() in {"all_results.tsv", "all_results.csv"} or "full" in path.name.lower()
        ]
        return (full_tables or per_contrast), False
    significant = [path for path in pool if "significant" in path.name.lower() or re.search(r"(^|_)sig(_|\.)", path.name.lower())]
    if significant:
        return significant, True
    return pool, False


def collect_da(analysis: Path, kind: str) -> tuple[pd.DataFrame | None, str]:
    grouped: dict[str, list[Path]] = {}
    for path in walk_files(analysis):
        if not is_da_path(path):
            continue
        if path.stat().st_size > 40_000_000 or _blocked_da(path):
            continue
        detected = omics_of(path)
        if detected not in {kind, None}:
            continue
        if kind == "shotgun" and re.search(r"(^|[_\-/])(asv|otu)([_\-./]|$)", str(path).lower()):
            continue
        grouped.setdefault(bundle_key(path), []).append(path)

    best_frame = None
    best_source = ""
    best_rank = None
    for directory, paths in grouped.items():
        chosen, significant_file = _choose_da_files(paths, kind)
        frames = []
        used = []
        penalties = []
        for path in chosen:
            frame = read_text_table(path)
            if frame is None:
                continue
            detected = omics_of(path)
            if detected not in {kind, None}:
                continue
            if kind == "shotgun" and _column_kind(frame) == "16s":
                continue
            if kind == "16s" and _column_kind(frame) == "shotgun":
                continue
            parsed = parse_da_frame(
                frame,
                kind,
                significant_file and "all_result" not in path.name.lower(),
                hint=path.stem,
            )
            if parsed is None or parsed.empty:
                continue
            if kind == "shotgun" and _hash_fraction(parsed) > 0.5:
                continue
            frames.append(parsed)
            used.append(path.name)
            penalties.append(_level_penalty(path, kind))
        if not frames:
            continue
        parsed = pd.concat(frames, ignore_index=True)
        n_called = int(parsed["called"].sum())
        n_time = int(parsed["timepoint"].nunique())
        summary_like = any(token in directory.lower() for token in ("summary", "cross_omics", "integration"))
        rank = (
            0 if _hash_fraction(parsed) > 0.5 else 1,
            int(np.median(penalties)) if penalties else 0,
            0 if summary_like else 1,
            n_time,
            n_called > 0,
            n_called,
        )
        if best_rank is None or rank > best_rank:
            best_rank = rank
            best_frame = parsed
            try:
                best_source = str(Path(directory).relative_to(analysis)) + f" [{', '.join(used)}]"
            except ValueError:
                best_source = f"{directory} [{', '.join(used)}]"
    return best_frame, best_source


def has_partial(analysis: Path, task: str) -> str:
    for path in walk_files(analysis):
        if path.suffix.lower() not in IMAGE_EXT and path.suffix.lower() != ".qzv":
            continue
        text = str(path).lower()
        if any(bad in text for bad in ("retired", "superseded", "/dist/")):
            continue
        name = path.name.lower()
        if task == "16s_alpha" and "shannon" in name:
            return rel_parts(path, analysis.parent)
        beta_hit = any(key in text for key in ("pcoa", "permanova", "unifrac", "bray"))
        if task == "16s_beta" and beta_hit and ("16s" in text or "diversity" in text):
            if "shotgun" in text and "16s" not in text:
                continue
            return rel_parts(path, analysis.parent)
        if task == "16s_da" and any(key in text for key in ("volcano", "heatmap", "maaslin", "deseq", "ancom", "lefse")) and "shotgun" not in text:
            return rel_parts(path, analysis.parent)
        if task == "shotgun_da" and "shotgun" in text and any(key in text for key in ("volcano", "heatmap", "da", "deseq", "maaslin", "diff")):
            return rel_parts(path, analysis.parent)
    return ""


def call_set(frame: pd.DataFrame | None, timed: bool = False) -> set[str]:
    if frame is None or frame.empty:
        return set()
    called = frame[frame["called"]]
    if timed:
        return {f"{row.timepoint}|{row.taxon}" for row in called.itertuples(index=False)}
    return {row.taxon for row in called.itertuples(index=False)}


def effect_map(frame: pd.DataFrame | None) -> dict[str, float]:
    """Median signed effect per taxon across resistance contrasts."""
    if frame is None or frame.empty:
        return {}
    grouped: dict[str, list[float]] = {}
    for row in frame.itertuples(index=False):
        if not np.isfinite(row.effect):
            continue
        grouped.setdefault(row.taxon, []).append(float(row.effect))
    return {key: float(np.median(values)) for key, values in grouped.items()}


def _hash_ids(names: set[str]) -> bool:
    if not names:
        return False
    hashed = sum(bool(re.fullmatch(r"[0-9a-f]{16,}", name)) for name in names)
    return hashed / len(names) > 0.5


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def align_vectors(left: pd.Series, right: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    shared = sorted(set(left.index) & set(right.index))
    if len(shared) < MIN_SAMPLES:
        return np.array([]), np.array([])
    return left.loc[shared].to_numpy(float), right.loc[shared].to_numpy(float)


def align_matrices(left: pd.DataFrame, right: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    shared = sorted(set(left.index) & set(right.index))
    if len(shared) < MIN_SAMPLES:
        return np.array([]), np.array([])
    return left.loc[shared, shared].to_numpy(float), right.loc[shared, shared].to_numpy(float)


def upper_values(matrix: np.ndarray) -> np.ndarray:
    idx = np.triu_indices(matrix.shape[0], k=1)
    return matrix[idx]


def mantel_r(left: np.ndarray, right: np.ndarray) -> float:
    a = upper_values(left)
    b = upper_values(right)
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 30 or np.nanstd(a[mask]) == 0 or np.nanstd(b[mask]) == 0:
        return np.nan
    corr, _ = stats.pearsonr(a[mask], b[mask])
    return float(corr)


def procrustes_disparity(left: np.ndarray, right: np.ndarray) -> float:
    """Classical PCoA (2 axes) followed by Procrustes disparity."""
    coords = []
    for matrix in (left, right):
        n = matrix.shape[0]
        centering = np.eye(n) - np.ones((n, n)) / n
        gram = -0.5 * centering @ (matrix ** 2) @ centering
        gram = (gram + gram.T) / 2
        vals, vecs = np.linalg.eigh(gram)
        order = np.argsort(vals)[::-1]
        vals = vals[order]
        vecs = vecs[:, order]
        keep = vals > 1e-10
        if keep.sum() < 2:
            return np.nan
        coords.append(vecs[:, :2] * np.sqrt(vals[:2]))
    _, _, disparity = _procrustes(coords[0], coords[1])
    return float(disparity)


def _procrustes(data1: np.ndarray, data2: np.ndarray):
    from scipy.spatial import procrustes

    return procrustes(data1, data2)


def score_job(row: pd.Series) -> dict:
    analysis = ROOT / row.job_id / "analysis"
    result = {
        "session": row.session,
        "replicate": int(row.replicate),
        "level": row.level,
        "model": row.model,
        "job_id": row.job_id,
        "analysis_present": analysis.exists(),
    }
    shannon, shannon_src = (None, "")
    distances: dict[str, tuple[pd.DataFrame, str]] = {}
    da_frames: dict[str, pd.DataFrame | None] = {"16s": None, "shotgun": None}
    da_src = {"16s": "", "shotgun": ""}
    if analysis.exists():
        shannon, shannon_src = collect_shannon(analysis)
        distances = collect_distances(analysis)
        for kind in ("16s", "shotgun"):
            da_frames[kind], da_src[kind] = collect_da(analysis, kind)

    alpha_n = 0 if shannon is None else int(len(shannon))
    if shannon is not None and alpha_n >= MIN_SAMPLES:
        alpha_score, alpha_why = 1.0, shannon_src
    else:
        partial = has_partial(analysis, "16s_alpha") if analysis.exists() else ""
        alpha_score, alpha_why = (0.5, partial) if partial else (0.0, "")

    beta_metrics = [metric for metric in BETA_PRIORITY if metric in distances and distances[metric][0].shape[0] >= MIN_SAMPLES]
    if beta_metrics:
        beta_score = 1.0
        beta_why = "; ".join(f"{metric}:{distances[metric][1]}" for metric in beta_metrics)
    else:
        partial = has_partial(analysis, "16s_beta") if analysis.exists() else ""
        beta_score, beta_why = (0.5, partial) if partial else (0.0, "")

    def da_score(kind: str, task: str) -> tuple[float, str, int]:
        frame = da_frames[kind]
        if frame is not None and len(frame) >= 5:
            return 1.0, da_src[kind], int(frame["called"].sum())
        partial = has_partial(analysis, task) if analysis.exists() else ""
        if partial:
            return 0.5, partial, 0
        return 0.0, "", 0

    s16, why16, n16 = da_score("16s", "16s_da")
    ssg, whysg, nsg = da_score("shotgun", "shotgun_da")

    result.update(
        {
            "16s_alpha": alpha_score,
            "16s_alpha_source": alpha_why,
            "16s_alpha_n": alpha_n,
            "16s_beta": beta_score,
            "16s_beta_source": beta_why,
            "16s_beta_metrics": ",".join(beta_metrics),
            "16s_da": s16,
            "16s_da_source": why16,
            "16s_da_n_calls": n16,
            "shotgun_da": ssg,
            "shotgun_da_source": whysg,
            "shotgun_da_n_calls": nsg,
        }
    )
    result["_shannon"] = shannon
    result["_distances"] = distances
    result["_da"] = da_frames
    return result


def pairwise_rows(records: list[dict]) -> list[dict]:
    rows = []
    frame = pd.DataFrame([{k: v for k, v in rec.items() if not k.startswith("_")} for rec in records])
    by_key = {(rec["model"], rec["level"], rec["replicate"]): rec for rec in records}
    for (model, level), group in frame.groupby(["model", "level"], sort=False):
        reps = sorted(group["replicate"].tolist())
        for left_rep, right_rep in itertools.combinations(reps, 2):
            left = by_key[(model, level, left_rep)]
            right = by_key[(model, level, right_rep)]
            row = {
                "model": model,
                "level": level,
                "replicate_a": left_rep,
                "replicate_b": right_rep,
                "session_a": left["session"],
                "session_b": right["session"],
            }
            # Alpha
            if left["16s_alpha"] == 1 and right["16s_alpha"] == 1:
                a, b = align_vectors(left["_shannon"], right["_shannon"])
                row["16s_alpha_n"] = int(len(a))
                if len(a) >= MIN_SAMPLES and np.std(a) > 0 and np.std(b) > 0:
                    corr, _ = stats.pearsonr(a, b)
                    row["16s_alpha_pearson_r"] = float(corr)
                    row["16s_alpha_mean_abs_diff"] = float(np.mean(np.abs(a - b)))
                else:
                    row["16s_alpha_pearson_r"] = np.nan
                    row["16s_alpha_mean_abs_diff"] = np.nan
            else:
                row["16s_alpha_n"] = 0
                row["16s_alpha_pearson_r"] = np.nan
                row["16s_alpha_mean_abs_diff"] = np.nan

            # Beta
            shared_metric = next(
                (metric for metric in BETA_PRIORITY if metric in left["_distances"] and metric in right["_distances"]),
                "",
            )
            row["16s_beta_metric"] = shared_metric
            if shared_metric and left["16s_beta"] == 1 and right["16s_beta"] == 1:
                mat_a, mat_b = align_matrices(left["_distances"][shared_metric][0], right["_distances"][shared_metric][0])
                row["16s_beta_n"] = int(mat_a.shape[0]) if mat_a.size else 0
                row["16s_beta_mantel_r"] = mantel_r(mat_a, mat_b) if mat_a.size else np.nan
                try:
                    row["16s_beta_procrustes_disparity"] = (
                        procrustes_disparity(mat_a, mat_b) if mat_a.size else np.nan
                    )
                except Exception:
                    row["16s_beta_procrustes_disparity"] = np.nan
            else:
                row["16s_beta_n"] = 0
                row["16s_beta_mantel_r"] = np.nan
                row["16s_beta_procrustes_disparity"] = np.nan

            for kind, prefix in (("16s", "16s_da"), ("shotgun", "shotgun_da")):
                if left[prefix] == 1 and right[prefix] == 1:
                    calls_a = call_set(left["_da"][kind])
                    calls_b = call_set(right["_da"][kind])
                    timed_a = call_set(left["_da"][kind], timed=True)
                    timed_b = call_set(right["_da"][kind], timed=True)
                    row[f"{prefix}_n_calls_a"] = len(calls_a)
                    row[f"{prefix}_n_calls_b"] = len(calls_b)
                    if _hash_ids(calls_a) != _hash_ids(calls_b):
                        row[f"{prefix}_jaccard"] = np.nan
                    else:
                        row[f"{prefix}_jaccard"] = np.nan if (not calls_a and not calls_b) else jaccard(calls_a, calls_b)
                    row[f"{prefix}_jaccard_timepoint"] = (
                        np.nan if (not timed_a and not timed_b) else jaccard(timed_a, timed_b)
                    )
                    effects_a = effect_map(left["_da"][kind])
                    effects_b = effect_map(right["_da"][kind])
                    shared_fx = sorted(set(effects_a) & set(effects_b))
                    row[f"{prefix}_n_shared_effects"] = len(shared_fx)
                    if len(shared_fx) >= 8:
                        xa = np.array([effects_a[key] for key in shared_fx])
                        xb = np.array([effects_b[key] for key in shared_fx])
                        if np.std(xa) > 0 and np.std(xb) > 0:
                            corr, _ = stats.spearmanr(xa, xb)
                            row[f"{prefix}_effect_spearman_r"] = float(corr)
                        else:
                            row[f"{prefix}_effect_spearman_r"] = np.nan
                    else:
                        row[f"{prefix}_effect_spearman_r"] = np.nan
                else:
                    row[f"{prefix}_n_calls_a"] = np.nan
                    row[f"{prefix}_n_calls_b"] = np.nan
                    row[f"{prefix}_jaccard"] = np.nan
                    row[f"{prefix}_jaccard_timepoint"] = np.nan
                    row[f"{prefix}_n_shared_effects"] = 0
                    row[f"{prefix}_effect_spearman_r"] = np.nan
            rows.append(row)
    return rows


def summarize_completion(session_df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for (model, level), group in session_df.groupby(["model", "level"], sort=False):
        for task in TASKS:
            values = group[task].astype(float)
            records.append(
                {
                    "model": model,
                    "level": level,
                    "task": task,
                    "n_sessions": int(len(values)),
                    "n_complete": int((values == 1).sum()),
                    "n_partial": int((values == 0.5).sum()),
                    "n_absent": int((values == 0).sum()),
                    "mean_artifact_score": float(values.mean()),
                }
            )
    return pd.DataFrame.from_records(records)


def summarize_concordance(pair_df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        ("16s_alpha", "pearson_r", "16s_alpha_pearson_r"),
        ("16s_beta", "mantel_r", "16s_beta_mantel_r"),
        ("16s_beta", "procrustes_disparity", "16s_beta_procrustes_disparity"),
        ("16s_da", "jaccard", "16s_da_jaccard"),
        ("16s_da", "jaccard_timepoint", "16s_da_jaccard_timepoint"),
        ("16s_da", "effect_spearman_r", "16s_da_effect_spearman_r"),
        ("shotgun_da", "jaccard", "shotgun_da_jaccard"),
        ("shotgun_da", "jaccard_timepoint", "shotgun_da_jaccard_timepoint"),
        ("shotgun_da", "effect_spearman_r", "shotgun_da_effect_spearman_r"),
    ]
    records = []
    for (model, level), group in pair_df.groupby(["model", "level"], sort=False):
        for task, metric, column in metrics:
            values = pd.to_numeric(group[column], errors="coerce").dropna()
            records.append(
                {
                    "model": model,
                    "level": level,
                    "task": task,
                    "metric": metric,
                    "n_pairs": int(len(values)),
                    "median": float(values.median()) if len(values) else np.nan,
                    "min": float(values.min()) if len(values) else np.nan,
                    "max": float(values.max()) if len(values) else np.nan,
                }
            )
    return pd.DataFrame.from_records(records)


def main() -> None:
    jobs = pd.read_csv(JOBS)
    records = []
    for row in jobs.itertuples(index=False):
        print(f"scoring {row.session}", flush=True)
        records.append(score_job(row))
    pairs = pairwise_rows(records)
    public = pd.DataFrame([{k: v for k, v in rec.items() if not k.startswith("_")} for rec in records])
    pair_df = pd.DataFrame(pairs)
    completion = summarize_completion(public)
    concordance = summarize_concordance(pair_df)

    table_dir = OUT / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    public.to_csv(table_dir / "completion_by_session.tsv", sep="\t", index=False)
    completion.to_csv(table_dir / "completion_summary.tsv", sep="\t", index=False)
    pair_df.to_csv(table_dir / "concordance_pairs.tsv", sep="\t", index=False)
    concordance.to_csv(table_dir / "concordance_summary.tsv", sep="\t", index=False)

    print("COMPLETION")
    print(
        public.groupby(["model", "level"])[TASKS]
        .mean()
        .round(2)
        .to_string()
    )
    print("\nCONCORDANCE MEDIANS")
    print(
        concordance.pivot_table(index=["task", "metric"], columns=["model", "level"], values="median")
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    main()
