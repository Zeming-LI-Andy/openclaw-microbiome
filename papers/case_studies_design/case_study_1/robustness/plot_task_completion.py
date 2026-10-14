#!/usr/bin/env python3
"""Completion of six robustness tasks, as a percentage of the three runs.

A run is complete when a numeric result exists. A figure alone does not count.
16S alpha: a per-sample Shannon vector of at least 30 samples.
16S beta: a square sample distance matrix of at least 30 samples.
16S taxonomic profiling: a sample-by-genus abundance table, at least 30 samples
and 5 genera. Shotgun species profiling uses the same rule at species level,
or at least 30 per-library MetaPhlAn profiles.
Differential abundance: a result table with taxon names and a p, q, log2FC,
coefficient, or LDA column. 16S is genus-level; shotgun is species-level.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
import score_robustness as sr
from audit_panel_alignment import require_matplotlib_panel_alignment
from plot_composition_da_distributions import (
    best_composition,
    canon_sample,
    orient_abundance,
    read_table,
)
from plot_model_distributions import LEVEL_ORDER, MODEL_LABEL, MODEL_ORDER

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
TASKS = (
    ("16s_alpha", "16S alpha diversity"),
    ("16s_beta", "16S beta diversity"),
    ("16s_taxonomy", "16S genus-level\ntaxonomic profiling"),
    ("16s_da", "16S differential abundance"),
    ("shotgun_taxonomy", "shotgun species-level\ntaxonomic profiling"),
    ("shotgun_da", "Shotgun differential abundance"),
)
LEVEL_LABEL = {"detailed": "Detailed", "medium": "Medium", "simple": "Simple"}


def genus_abundance(analysis: Path) -> tuple[bool, str]:
    matrix, source = best_composition(analysis, "genus")
    if matrix is not None and matrix.shape[0] >= 30 and matrix.shape[1] >= 5:
        return True, source
    for path in sr.walk_files(analysis):
        rel = str(path.relative_to(analysis)).lower()
        name = path.name.lower()
        if path.suffix.lower() not in {".tsv", ".csv", ".txt"}:
            continue
        if any(token in rel for token in ("shotgun", "metaphlan", "deseq", "maaslin", "lefse", "ancom")):
            continue
        if "genus" not in name:
            continue
        if not any(token in name for token in ("proportion", "table", "count", "relab", "composition", "abundance")):
            continue
        frame = read_table(path)
        if frame is None:
            continue
        parsed = orient_abundance(frame, "genus")
        if parsed is not None and parsed.shape[0] >= 30 and parsed.shape[1] >= 5:
            return True, str(path.relative_to(analysis))
    return False, ""


def species_abundance(analysis: Path) -> tuple[bool, str]:
    matrix, source = best_composition(analysis, "species")
    if matrix is not None and matrix.shape[0] >= 30 and matrix.shape[1] >= 5:
        return True, source
    for path in sr.walk_files(analysis):
        rel = str(path.relative_to(analysis)).lower()
        name = path.name.lower()
        if path.suffix.lower() not in {".tsv", ".csv", ".txt"}:
            continue
        if "16s" in rel and "shotgun" not in rel and "metaphlan" not in rel:
            continue
        if "species" not in name and not name.endswith("_profile.txt") and not name.endswith("_profile.tsv"):
            continue
        if any(token in name for token in ("deseq", "maaslin", "lefse", "ancom", "significant", "all_results")):
            continue
        if name.endswith("_profile.txt") or name.endswith("_profile.tsv"):
            continue
        frame = read_table(path)
        if frame is None:
            continue
        parsed = orient_abundance(frame, "species")
        if parsed is not None and parsed.shape[0] >= 30 and parsed.shape[1] >= 5:
            return True, str(path.relative_to(analysis))
    profiles = [
        path
        for path in sr.walk_files(analysis)
        if "metaphlan" in str(path).lower() and (path.name.lower().endswith("_profile.txt") or path.name.lower().endswith("_profile.tsv"))
    ]
    species_profiles = []
    for path in profiles:
        text = path.read_text(errors="replace")
        if "|s__" in text or "s__" in text:
            stem = path.name
            for suffix in ("_profile.txt", "_profile.tsv"):
                if stem.lower().endswith(suffix):
                    stem = stem[: -len(suffix)]
                    break
            sample = canon_sample(stem)
            if sample:
                species_profiles.append(sample)
    if len(set(species_profiles)) >= 30:
        parent = str(profiles[0].parent.relative_to(analysis))
        return True, parent + "/*_profile.*"
    return False, ""


def _header_keys(frame: pd.DataFrame) -> set[str]:
    return {"".join(ch for ch in str(col).lower() if ch.isalnum()) for col in frame.columns}


def _is_da_path(rel: str) -> bool:
    import re

    if any(token in rel for token in ("deseq", "maaslin", "lefse", "ancom", "diff", "daa", "differential", "wilcox", "welch")):
        return True
    return re.search(r"(^|[/_-])da([/_-]|$)", rel) is not None


def differential_table(analysis: Path, rank: str) -> tuple[bool, str]:
    stat_tokens = ("pvalue", "pval", "padj", "qvalue", "qval", "fdr", "log2fold", "log2fc", "coef", "lda", "lfc")
    for path in sr.walk_files(analysis):
        if path.suffix.lower() not in {".tsv", ".csv"}:
            continue
        rel = str(path.relative_to(analysis)).lower()
        name = path.name.lower()
        if any(token in rel for token in ("pathway", "picrust", "humann", "bowtie", "/features/", "distance-matrix", "dada2")):
            continue
        if not _is_da_path(rel):
            continue
        frame = read_table(path)
        if frame is None or len(frame) < 5:
            continue
        keys = _header_keys(frame)
        if not any(any(token in key for token in stat_tokens) for key in keys):
            continue
        shotgun = "shotgun" in rel or "metaphlan" in rel
        amplicon = "16s" in rel or "amplicon" in rel
        has_species = "species" in keys or "species" in name
        has_genus = "genus" in keys or "genus" in name
        has_asv = "asv" in keys or "otu" in keys
        if rank == "genus":
            if shotgun and not amplicon:
                continue
            if has_species and not has_genus and not has_asv and not amplicon:
                continue
            if not (has_genus or has_asv or amplicon or "genus" in rel):
                continue
            return True, str(path.relative_to(analysis))
        if amplicon and not shotgun:
            continue
        if has_asv and not shotgun:
            continue
        if has_genus and not has_species and "species" not in rel:
            continue
        if not (has_species or "species" in rel or shotgun):
            continue
        return True, str(path.relative_to(analysis))
    return False, ""


def score_session(analysis: Path) -> dict[str, tuple[int, str]]:
    shannon, shannon_source = sr.collect_shannon(analysis)
    alpha = int(shannon is not None and int(shannon.notna().sum()) >= 30)
    distances = sr.collect_distances(analysis)
    beta_source = ""
    beta = 0
    for _metric, (frame, source) in distances.items():
        if frame.shape[0] >= 30:
            beta = 1
            beta_source = source
            break
    genus_ok, genus_source = genus_abundance(analysis)
    species_ok, species_source = species_abundance(analysis)
    genus_da, genus_da_source = differential_table(analysis, "genus")
    species_da, species_da_source = differential_table(analysis, "species")
    return {
        "16s_alpha": (alpha, shannon_source if alpha else ""),
        "16s_beta": (beta, beta_source),
        "16s_taxonomy": (int(genus_ok), genus_source),
        "16s_da": (int(genus_da), genus_da_source),
        "shotgun_taxonomy": (int(species_ok), species_source),
        "shotgun_da": (int(species_da), species_da_source),
    }


def completion_table(jobs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in jobs.itertuples(index=False):
        print(f"score {row.session}", flush=True)
        found = score_session(sr.ROOT / row.job_id / "analysis")
        for task, _title in TASKS:
            done, source = found[task]
            rows.append(
                {
                    "session": row.session,
                    "replicate": row.replicate,
                    "level": row.level,
                    "model": row.model,
                    "task": task,
                    "complete": done,
                    "source": source,
                }
            )
    return pd.DataFrame.from_records(rows)


def summary_table(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for task, _title in TASKS:
        for model in MODEL_ORDER:
            for level in LEVEL_ORDER:
                part = detail[(detail["task"] == task) & (detail["model"] == model) & (detail["level"] == level)]
                n = int(part["complete"].sum())
                rows.append(
                    {
                        "task": task,
                        "model": model,
                        "level": level,
                        "n_complete": n,
                        "n_runs": int(len(part)),
                        "percent": 100.0 * n / len(part) if len(part) else np.nan,
                    }
                )
    return pd.DataFrame.from_records(rows)


def render_heatmap(axes, summary: pd.DataFrame) -> plt.Axes:
    """Draw the six completion heatmaps. Returns a colorbar axes created by the caller later."""
    cmap = plt.get_cmap("Blues")
    image = None
    for index, (task, title) in enumerate(TASKS):
        ax = axes[index // 3, index % 3]
        grid = np.zeros((len(MODEL_ORDER), len(LEVEL_ORDER)))
        counts = np.zeros_like(grid)
        for i, model in enumerate(MODEL_ORDER):
            for j, level in enumerate(LEVEL_ORDER):
                hit = summary[(summary["task"] == task) & (summary["model"] == model) & (summary["level"] == level)].iloc[0]
                grid[i, j] = hit.percent
                counts[i, j] = hit.n_complete
        image = ax.imshow(grid, cmap=cmap, vmin=0, vmax=100, aspect="auto", interpolation="nearest")
        ax.set_xticks(range(len(LEVEL_ORDER)))
        ax.set_xticklabels([LEVEL_LABEL[level] for level in LEVEL_ORDER])
        ax.set_yticks(range(len(MODEL_ORDER)))
        ax.set_yticklabels([MODEL_LABEL[model] for model in MODEL_ORDER] if index % 3 == 0 else [])
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#CBD5E1")
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                value = grid[i, j]
                color = "white" if value >= 55 else "#1F2937"
                ax.text(j, i, f"{value:.0f}%\n{int(counts[i, j])}/3", ha="center", va="center", fontsize=7, color=color)
        wrapped = title.replace(" differential ", "\ndifferential ")
        ax.set_title(wrapped, pad=4, fontweight="bold")
        if index // 3 == 1:
            ax.set_xlabel("Prompt")
        if index % 3 == 0:
            ax.set_ylabel("Model")
    return image


def draw(summary: pd.DataFrame) -> None:
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
            "axes.linewidth": 0.6,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
        }
    )
    fig, axes = plt.subplots(2, 3, figsize=(7.20, 4.15), constrained_layout=False)
    fig.subplots_adjust(left=0.15, right=0.90, top=0.90, bottom=0.11, wspace=0.28, hspace=0.62)
    render_heatmap(axes, summary)
    cax = fig.add_axes([0.915, 0.22, 0.016, 0.52])
    fig.colorbar(ScalarMappable(norm=Normalize(0, 100), cmap=plt.get_cmap("Blues")), cax=cax, label="Percentage of runs (%)")
    stem = FIGS / "task_completion_heatmap"
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
    jobs = pd.read_csv(sr.JOBS)
    detail = completion_table(jobs)
    summary = summary_table(detail)
    detail.to_csv(TABLES / "task_completion_by_session.tsv", sep="\t", index=False)
    summary.to_csv(TABLES / "task_completion_summary.tsv", sep="\t", index=False)
    draw(summary)
    print(summary.to_string(index=False), flush=True)
    missing = detail[detail["complete"] == 0]
    print("incomplete", flush=True)
    print(missing[["session", "task"]].to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
