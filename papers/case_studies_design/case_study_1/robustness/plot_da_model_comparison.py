#!/usr/bin/env python3
"""Compare models on DESeq2 log2 fold changes where every model used DESeq2.

Within one prompt, a taxon’s value is the median log2 fold change inside a
session table, then the mean across sessions that ran genus-level (16S) or
species-level (shotgun) DESeq2. A box contains only taxa present for all three
models. The brackets are pairwise two-sided Mann–Whitney U tests, Holm-adjusted
within that prompt. Taxa from one experiment are not independent replicates.

Shotgun medium has no method shared by all three models, so that group is not
drawn.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
import plot_composition_da_distributions as comp
import plot_da_prompt_comparison as da
import plot_model_distributions as models
from audit_panel_alignment import require_matplotlib_panel_alignment

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
PROMPTS = ("detailed", "medium")
PROMPT_LABEL = {"detailed": "Detailed", "medium": "Medium"}
BOX_WIDTH = 0.58
COMPARE = (
    ("16s", "detailed", "16S differential\nabundance, Detailed"),
    ("16s", "medium", "16S differential\nabundance, Medium"),
    ("shotgun", "detailed", "shotgun differential\nabundance, Detailed"),
)

# Shotgun DESeq2 only. Medium is omitted because the three models did not share a method.
SHOTGUN_DESEQ_SESSIONS = {
    "glm-flash": {
        "detailed": (
            "1-robustness-detailed-glm-flash",
            "3-robustness-detailed-glm-flash",
        ),
    },
    "deepseek-flash": {
        "detailed": (
            "1-robustness-detailed-deepseek-flash",
            "2-robustness-detailed-deepseek-flash",
        ),
    },
    "deepseek-pro": {
        "detailed": ("1-robustness-detailed-deepseek-pro",),
    },
}
PANELS = (
    ("16s", "genus", False, da.SIXTEEN_S_SESSIONS, "16S genus-level\ndifferential abundance"),
    ("shotgun", "species", True, SHOTGUN_DESEQ_SESSIONS, "shotgun species-level\ndifferential abundance"),
)


def _is_summary(path: Path) -> bool:
    name = path.name.lower()
    return any(token in name for token in ("all_comparison", "all-result", "all_result", "combined"))


def _session_effect(analysis: Path, rank: str, shotgun: bool) -> pd.Series:
    """One log2 fold change per taxon in one session."""
    tables = []
    summaries = []
    for path in comp.da_candidates(analysis):
        rel = str(path.relative_to(analysis)).lower()
        if "superseded" in rel or "annotated" in path.name.lower():
            continue
        is_shotgun = "shotgun" in rel or "metaphlan" in rel
        if shotgun != is_shotgun:
            continue
        if not da._is_deseq2(path, da._header(path)):
            continue
        collapsed = da._collapsed(path, rank, 0.5)
        if collapsed is None:
            continue
        tables.append(collapsed)
        if _is_summary(path):
            summaries.append(collapsed)
    if summaries:
        best = max(summaries, key=len)
        return best.set_index("taxon")["log2fc"]
    if not tables:
        return pd.Series(dtype=float)
    if len(tables) == 1:
        return tables[0].set_index("taxon")["log2fc"]
    combined = pd.concat(tables, ignore_index=True)
    return combined.groupby("taxon")["log2fc"].median()


def _model_series(session_map: dict, model: str, level: str, rank: str, shotgun: bool) -> tuple[pd.Series, int]:
    sessions = session_map.get(model, {}).get(level, ())
    jobs = da._jobs()
    parts = [_session_effect(da._analysis(jobs, session), rank, shotgun) for session in sessions]
    parts = [part for part in parts if len(part)]
    return da._mean_sessions(parts), len(parts)


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    value_rows = []
    coverage_rows = []
    for assay, rank, shotgun, session_map, _title in PANELS:
        for level in PROMPTS:
            by_model = {}
            n_sessions = {}
            for model in models.MODEL_ORDER:
                series, n_used = _model_series(session_map, model, level, rank, shotgun)
                by_model[model] = series
                n_sessions[model] = n_used
            present = [model for model in models.MODEL_ORDER if len(by_model[model])]
            shared = set.intersection(*(set(by_model[model].index) for model in present)) if len(present) == 3 else set()
            print(f"{assay} {level}: sessions={ {m: n_sessions[m] for m in models.MODEL_ORDER} } shared_taxa={len(shared)}", flush=True)
            for model in models.MODEL_ORDER:
                coverage_rows.append(
                    {
                        "assay": assay,
                        "level": level,
                        "model": model,
                        "method": "DESeq2" if n_sessions[model] else "",
                        "sessions_used": n_sessions[model],
                        "taxa_in_model": int(len(by_model[model])),
                        "taxa_shared": int(len(shared)),
                    }
                )
                if not shared:
                    continue
                for taxon, value in by_model[model].loc[sorted(shared)].items():
                    value_rows.append(
                        {
                            "task": assay,
                            "level": level,
                            "model": model,
                            "taxon": taxon,
                            "value": float(value),
                        }
                    )
    values = pd.DataFrame.from_records(value_rows)
    coverage = pd.DataFrame.from_records(coverage_rows)
    return values, coverage


def _style() -> None:
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


def _draw_panel(ax: plt.Axes, values: pd.DataFrame, tests: pd.DataFrame, task: str, level: str, title: str) -> None:
    sub = values[(values["task"] == task) & (values["level"] == level)]
    present = [model for model in models.MODEL_ORDER if (sub["model"] == model).any()]
    centers = []
    for model_i, model in enumerate(present):
        series = sub.loc[sub["model"] == model, "value"].to_numpy(dtype=float)
        centers.append(float(model_i))
        color = models.PALETTE[models.MODEL_LABEL[model]]
        ax.boxplot(
            [series],
            positions=[model_i],
            widths=BOX_WIDTH,
            patch_artist=True,
            showfliers=False,
            boxprops={"facecolor": color, "edgecolor": color, "linewidth": 0.6, "alpha": 0.85},
            whiskerprops={"color": "#222222", "linewidth": 0.6},
            capprops={"color": "#222222", "linewidth": 0.6},
            medianprops={"color": "#222222", "linewidth": 0.6},
        )
    ax.set_xlim(-0.55, max(len(present) - 1, 0) + 0.55)
    ax.set_xticks(range(len(present)))
    ax.set_xticklabels(
        [models.MODEL_LABEL[model] for model in present],
        rotation=55,
        rotation_mode="anchor",
        ha="right",
        va="top",
    )
    ax.tick_params(axis="x", length=0, pad=4)
    ax.set_title(title, pad=6)
    ax.yaxis.labelpad = 2
    if len(present) >= 2:
        panel_tests = tests[(tests["task"] == task) & (tests["level"] == level)]
        comp._add_significance_brackets(ax, present, panel_tests, centers)


def _share_16s_limits(axes) -> None:
    """Keep the two 16S panels on one y scale. Shotgun stays on its own."""
    lowers, uppers = [], []
    for ax in axes[:2]:
        y0, y1 = ax.get_ylim()
        lowers.append(min(y0, y1))
        uppers.append(max(y0, y1))
    for ax in axes[:2]:
        ax.set_ylim(min(lowers), max(uppers))


def draw(values: pd.DataFrame, tests: pd.DataFrame) -> None:
    _style()
    fig = plt.figure(figsize=(7.20, 3.40))
    grid = fig.add_gridspec(1, 3, left=0.115, right=0.988, top=0.86, bottom=0.22, wspace=0.28)
    axes = grid.subplots()
    for ax, (task, level, title) in zip(axes, COMPARE):
        _draw_panel(ax, values, tests, task, level, title)
    axes[0].set_ylabel("DESeq2 log2 fold change")
    fig.canvas.draw()
    for ax in axes:
        needed = max(comp._required_bracket_points(ax), 14.0)
        comp._ensure_bracket_headroom(ax, points=needed)
    _share_16s_limits(axes)
    fig.canvas.draw()
    for ax in axes:
        comp.place_brackets_above_data(ax)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    points_to_px = fig.dpi / 72.0
    label_box = axes[0].yaxis.label.get_window_extent(renderer)
    first_letter_x = (label_box.x0 - 10.0 * points_to_px) / fig.bbox.width
    letter_y = (axes[0].get_window_extent().y1 + 16.0 * points_to_px) / fig.bbox.height
    fig.text(first_letter_x, letter_y, "a", ha="left", va="bottom", fontsize=8, fontweight="bold")
    for ax, letter in zip(axes[1:], "bc"):
        box = ax.get_window_extent()
        fig.text((box.x0 - 8.0 * points_to_px) / fig.bbox.width, letter_y, letter, ha="left", va="bottom", fontsize=8, fontweight="bold")
    stem = FIGS / "model_deseq2_comparison"
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


def write_summary(coverage: pd.DataFrame) -> pd.DataFrame:
    """One row per model, in the same shape as the prompt-method summary."""
    analysis_name = {
        "16s": "16S rRNA gene, genus",
        "shotgun": "Shotgun metagenome, species",
    }
    records = []
    for assay in ("16s", "shotgun"):
        part = coverage.loc[coverage["assay"] == assay]
        for model in da.ROW_ORDER:
            cells = {}
            taxa = {}
            for level in PROMPTS:
                row = part.loc[(part["model"] == model) & (part["level"] == level)]
                n_used = int(row["sessions_used"].iloc[0]) if len(row) else 0
                shared = int(row["taxa_shared"].iloc[0]) if len(row) else 0
                cells[level] = f"{n_used}/3" if n_used else "—"
                taxa[level] = shared if n_used else "—"
            records.append(
                {
                    "analysis": analysis_name[assay],
                    "model": da.ROW_LABEL[model],
                    "method": "DESeq2",
                    "detailed_sessions": cells["detailed"],
                    "medium_sessions": cells["medium"],
                    "detailed_taxa": taxa["detailed"],
                    "medium_taxa": taxa["medium"],
                }
            )
    summary = pd.DataFrame.from_records(records)
    summary.to_csv(TABLES / "da_model_method_summary.tsv", sep="\t", index=False)
    return summary


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    values, coverage = extract()
    tests = models.mannwhitney_table(values) if len(values) else pd.DataFrame()
    values.to_csv(TABLES / "model_deseq2_comparison_values.tsv", sep="\t", index=False)
    coverage.to_csv(TABLES / "model_deseq2_comparison_coverage.tsv", sep="\t", index=False)
    tests.to_csv(TABLES / "model_deseq2_comparison_tests.tsv", sep="\t", index=False)
    print(write_summary(coverage).to_string(index=False), flush=True)
    draw(values, tests)
    print(coverage.to_string(index=False), flush=True)
    print(tests.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
