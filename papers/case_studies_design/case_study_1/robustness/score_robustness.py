#!/usr/bin/env python3
"""Read Shannon vectors and distance matrices from Case 1 robustness sessions.

The figure scripts use these readers. Session scoring and the pairwise
concordance tables are not produced here.
"""

from __future__ import annotations

import zipfile
from io import StringIO
from pathlib import Path

import pandas as pd

ROOT = Path("/datahome/datasets/ericteam/cszmli/previous_results")
OUT = Path(
    "/datahome/datasets/ericteam/cszmli/openclaw-microbiome/papers/"
    "case_studies_design/case_study_1/robustness"
)
JOBS = OUT / "job_ids.csv"
SKIP_DIR_PARTS = {
    "bowtie2",
    "bt2",
    "bt2out",
    "mpa_db",
    "provenance",
    "dist",
    "node_modules",
}
TABLE_EXT = {".tsv", ".csv", ".txt"}


def canon_id(value: object) -> str:
    text = str(value).strip().strip('"').strip("'")
    text = text.replace(" ", "")
    return text.upper()


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

