#!/usr/bin/env python3
"""Task completion and between-model outcome distributions.

Panel b includes diversity, composition, and the DESeq2 model comparisons.
Prompt-level comparisons are a separate figure, by_prompt_models.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
import plot_composition_da_distributions as comp
import plot_da_model_comparison as da_models
import plot_task_completion as heatmap
from audit_panel_alignment import require_matplotlib_panel_alignment
from plot_model_distributions import MODEL_LABEL, MODEL_ORDER, PALETTE

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
DISTRIBUTION_TASKS = [
    ("16s_shannon", "Shannon index", "16S alpha diversity"),
    ("16s_beta", "Pairwise weighted UniFrac distance", "16S beta diversity"),
    ("16s_composition", "Genus relative abundance", "16S genus-level taxonomic profiling"),
    ("shotgun_composition", "Species relative abundance", "shotgun species-level taxonomic profiling"),
]


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


def _align_ylabel_column(axes, renderer) -> None:
    """Line up one column of y-axis titles on the same right edge.

    The automatic anchor is in display pixels. Convert the aligned anchor to
    axes fractions so the shift stays correct when the figure is saved.
    """
    boxes = [ax.yaxis.label.get_window_extent(renderer) for ax in axes]
    target = min(box.x1 for box in boxes)
    for ax, box in zip(axes, boxes):
        x_pos, y_pos = ax.yaxis.label.get_position()
        new_x, _ = ax.transAxes.inverted().transform((x_pos + (target - box.x1), 0))
        ax.yaxis.set_label_coords(new_x, y_pos)


def _place_letter(fig: plt.Figure, ax: plt.Axes, letter: str, x_fig: float, lift_px: float) -> None:
    """Panel letter on one shared vertical line, just above the panel."""
    top = ax.get_window_extent().y1 + lift_px
    fig.text(
        x_fig,
        top / fig.bbox.height,
        letter,
        ha="left",
        va="bottom",
        fontsize=8,
        fontweight="bold",
    )


def _distribution_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    diversity_values = pd.read_csv(TABLES / "model_distribution_values.tsv", sep="\t")
    diversity_tests = pd.read_csv(TABLES / "model_distribution_tests.tsv", sep="\t")
    composition_values = pd.read_csv(TABLES / "composition_da_distribution_values.tsv", sep="\t")
    composition_tests = pd.read_csv(TABLES / "composition_da_distribution_tests.tsv", sep="\t")
    composition_tasks = {"16s_composition", "shotgun_composition"}
    values = pd.concat(
        [diversity_values, composition_values.loc[composition_values["task"].isin(composition_tasks)]],
        ignore_index=True,
    )
    tests = pd.concat(
        [diversity_tests, composition_tests.loc[composition_tests["task"].isin(composition_tasks)]],
        ignore_index=True,
    )
    return values, tests


def draw() -> None:
    _style()
    summary = pd.read_csv(TABLES / "task_completion_summary.tsv", sep="\t")
    values, tests = _distribution_frames()
    da_values = pd.read_csv(TABLES / "model_deseq2_comparison_values.tsv", sep="\t")
    da_tests = pd.read_csv(TABLES / "model_deseq2_comparison_tests.tsv", sep="\t")

    # Heatmap on top. Panel b is the model comparison: diversity, composition, then DESeq2.
    fig = plt.figure(figsize=(7.20, 11.55))
    heat_gs = fig.add_gridspec(2, 3, left=0.185, right=0.90, bottom=0.718, top=0.960, wspace=0.34, hspace=0.52)
    dist_gs = fig.add_gridspec(2, 2, left=0.155, right=0.985, bottom=0.318, top=0.631, wspace=0.38, hspace=0.34)
    da_gs = fig.add_gridspec(1, 3, left=0.155, right=0.985, bottom=0.086, top=0.256, wspace=0.28)
    heat_axes = heat_gs.subplots()
    dist_axes = dist_gs.subplots().ravel()
    da_axes = da_gs.subplots()

    heatmap.render_heatmap(heat_axes, summary)
    heat_right = heat_axes[0, 2].get_position()
    heat_low = heat_axes[1, 2].get_position()
    cax = fig.add_axes([heat_right.x1 + 0.018, heat_low.y0, 0.014, heat_right.y1 - heat_low.y0])
    fig.colorbar(
        ScalarMappable(norm=Normalize(0, 100), cmap=plt.get_cmap("Blues")),
        cax=cax,
        label="Percentage of runs (%)",
    )
    for spine in cax.spines.values():
        spine.set_visible(True)

    comp.draw_grouped(
        values,
        tests,
        DISTRIBUTION_TASKS,
        "model_distribution_diversity_composition",
        log_y={"16s_composition", "shotgun_composition"},
        axes=dist_axes,
        panel_letters=False,
        legend=False,
        save=False,
    )
    for ax in dist_axes:
        ax.set_title(ax.get_title(), pad=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    dist_top = max(ax.get_position().y1 for ax in dist_axes[:2])
    handles = [
        Patch(facecolor=PALETTE[MODEL_LABEL[model]], edgecolor=PALETTE[MODEL_LABEL[model]], label=MODEL_LABEL[model])
        for model in MODEL_ORDER
    ]
    legend_y = dist_top + 36.0 / (fig.get_size_inches()[1] * 72.0)
    fig.legend(
        handles=handles,
        loc="center",
        ncol=3,
        bbox_to_anchor=(0.56, legend_y),
        frameon=False,
        handlelength=1.2,
        columnspacing=1.2,
    )

    for ax, (task, level, title) in zip(da_axes, da_models.COMPARE):
        da_models._draw_panel(ax, da_values, da_tests, task, level, title)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    da_axes[0].set_ylabel("DESeq2 log2 fold change")

    fig.canvas.draw()
    for ax in dist_axes:
        comp._ensure_bracket_headroom(ax)
    for ax in da_axes:
        needed = max(comp._required_bracket_points(ax), 14.0)
        comp._ensure_bracket_headroom(ax, points=needed)
    da_models._share_16s_limits(da_axes)
    fig.canvas.draw()
    for ax in list(dist_axes) + list(da_axes):
        comp.place_brackets_above_data(ax)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    _align_ylabel_column([dist_axes[0], dist_axes[2]], renderer)
    _align_ylabel_column([dist_axes[1], dist_axes[3]], renderer)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    points_to_px = fig.dpi / 72.0
    left_edges = []
    for ax in (heat_axes[0, 0], heat_axes[1, 0]):
        left_edges.append(ax.yaxis.label.get_window_extent(renderer).x0)
        for label in ax.get_yticklabels():
            if label.get_text():
                left_edges.append(label.get_window_extent(renderer).x0)
    for ax in (dist_axes[0], dist_axes[2]):
        left_edges.append(ax.yaxis.label.get_window_extent(renderer).x0)
    letter_x = (min(left_edges) - 14.0 * points_to_px) / fig.bbox.width
    _place_letter(fig, heat_axes[0, 0], "a", letter_x, 4)
    _place_letter(fig, dist_axes[0], "b", letter_x, 4)

    stem = FIGS / "case1_completion_models"
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


if __name__ == "__main__":
    draw()
