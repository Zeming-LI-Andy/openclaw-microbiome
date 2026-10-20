#!/usr/bin/env python3
"""Prompt-granularity comparisons for one model at a time.

Shannon uses one session-averaged index per shared sample. Beta uses the
session-averaged weighted UniFrac distance of one unordered sample pair
shared across prompts. Composition uses the session-mean relative abundance of one taxon in one
sample on the original-table scale. An abundance table is kept as stored,
and a count table is converted per sample before name filtering. Pairs
whose abundance is at least 5% in every prompt are kept. Mann–Whitney U tests compare those values, with Holm adjustment
within each task.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
import plot_composition_da_distributions as comp
import score_robustness as sr
from audit_panel_alignment import require_matplotlib_panel_alignment
from plot_model_distributions import LEVEL_LABEL, LEVEL_ORDER, holm

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
MODELS = (
    ("deepseek-pro", "deepseek_pro_by_prompt"),
    ("deepseek-flash", "deepseek_flash_by_prompt"),
    ("glm-flash", "glm_flash_by_prompt"),
)
PROMPT_COLOR = {
    "detailed": "#0072B2",
    "medium": "#E69F00",
    "simple": "#009E73",
}
PANELS = (
    ("16s_shannon", "Shannon index", "16S alpha diversity", False),
    ("16s_beta", "Weighted UniFrac distance", "16S beta diversity", False),
    ("16s_composition", "Genus relative abundance", "16S genus-level\ntaxonomic profiling", True),
    ("shotgun_composition", "Species relative abundance", "shotgun species-level\ntaxonomic profiling", True),
)


def diversity_by_prompt(model: str) -> dict[str, dict[str, np.ndarray]]:
    frame = pd.read_csv(TABLES / "model_distribution_values.tsv", sep="\t")
    frame = frame.loc[frame["model"] == model]
    out = {}
    for task in ("16s_shannon", "16s_beta"):
        parts = {}
        for level in LEVEL_ORDER:
            sub = frame.loc[(frame["task"] == task) & (frame["level"] == level)]
            parts[level] = sub.groupby("sample_id")["value"].mean()
        populated = [series for series in parts.values() if len(series)]
        shared = set.intersection(*(set(series.index) for series in populated)) if populated else set()
        out[task] = {
            level: series.loc[sorted(shared)].to_numpy(dtype=float)
            for level, series in parts.items()
            if len(series) and shared
        }
        print(f"{model} {task}: samples={len(shared)}", flush=True)
    return out


def composition_by_prompt(model: str) -> dict[str, dict[str, np.ndarray]]:
    jobs = pd.read_csv(sr.JOBS)
    jobs = jobs.loc[jobs["model"] == model]
    session_parts: dict[str, dict[str, list[pd.Series]]] = {
        task: {level: [] for level in LEVEL_ORDER} for task in ("16s_composition", "shotgun_composition")
    }
    for row in jobs.itertuples(index=False):
        analysis = sr.ROOT / row.job_id / "analysis"
        print(f"extract {row.session}", flush=True)
        for kind, task in (("genus", "16s_composition"), ("species", "shotgun_composition")):
            matrix, _source = comp.best_composition(analysis, kind)
            if matrix is None:
                continue
            session_parts[task][row.level].append(comp.compositional_session(matrix))
    out = {}
    for task, by_level in session_parts.items():
        averaged = {
            level: comp.mean_profiles(parts)
            for level, parts in by_level.items()
            if parts
        }
        ordered, kept = comp.shared_positive(comp.abundance_floor(averaged, comp.ABUNDANCE_FLOOR[task]))
        out[task] = kept
        print(f"{model} {task}: prompts={len(kept)} shared_sample_taxa={len(ordered)}", flush=True)
    return out


def prompt_tests(series: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    """Unpaired Mann–Whitney U on session-averaged values shared across prompts."""
    pairs = [("detailed", "medium"), ("detailed", "simple"), ("medium", "simple")]
    rows = []
    for task, _ylabel, _title, _log_y in PANELS:
        raw = []
        bundles = []
        for left, right in pairs:
            if left not in series.get(task, {}) or right not in series.get(task, {}):
                continue
            a = np.asarray(series[task][left], dtype=float)
            b = np.asarray(series[task][right], dtype=float)
            if len(a) < 5 or len(b) < 5:
                continue
            result = stats.mannwhitneyu(a, b, alternative="two-sided")
            raw.append(float(result.pvalue))
            bundles.append((left, right, a, b, float(result.statistic), float(result.pvalue)))
        for (left, right, a, b, stat, pvalue), p_holm in zip(bundles, holm(raw)):
            rows.append(
                {
                    "task": task,
                    "model_a": left,
                    "model_b": right,
                    "n_a": int(len(a)),
                    "n_b": int(len(b)),
                    "median_a": float(np.median(a)),
                    "median_b": float(np.median(b)),
                    "u_statistic": stat,
                    "p_raw": pvalue,
                    "p_holm": p_holm,
                }
            )
    return pd.DataFrame.from_records(rows)


def _draw_panels(
    axes,
    series: dict[str, dict[str, np.ndarray]],
    tests: pd.DataFrame,
    show_titles: bool,
    show_xlabels: bool,
    panels=PANELS,
    title_pad: float = 42,
    ylabel_for=None,
    box_width: float = 0.42,
    label_rotation: float = 35,
) -> None:
    for ax, (task, ylabel, title, log_y) in zip(axes, panels):
        present = [level for level in LEVEL_ORDER if len(series.get(task, {}).get(level, [])) > 0]
        for index, level in enumerate(present):
            ax.boxplot(
                [series[task][level]],
                positions=[index],
                widths=box_width,
                patch_artist=True,
                showfliers=False,
                boxprops={"facecolor": PROMPT_COLOR[level], "edgecolor": PROMPT_COLOR[level], "linewidth": 0.6, "alpha": 0.85},
                whiskerprops={"color": "#222222", "linewidth": 0.6},
                capprops={"color": "#222222", "linewidth": 0.6},
                medianprops={"color": "#222222", "linewidth": 0.6},
            )
        ax.set_xticks(range(len(present)))
        horizontal = label_rotation % 180 != 90
        ax.set_xticklabels(
            [LEVEL_LABEL[level] for level in present],
            rotation=label_rotation,
            rotation_mode="anchor",
            ha="right" if horizontal else "center",
            va="center" if horizontal else "top",
        )
        ax.tick_params(axis="x", labelbottom=show_xlabels, length=0, pad=18 if not horizontal else 8)
        ax.set_xlim(-0.55, max(len(present) - 1, 0) + 0.55)
        if len(present) >= 2:
            comp._add_significance_brackets(
                ax,
                present,
                tests.loc[tests["task"] == task],
                centers=[float(i) for i in range(len(present))],
            )
        ax.set_ylabel(ylabel if ylabel_for is None else ylabel_for(task, ylabel))
        ax.set_title(title if show_titles else "", pad=title_pad)
        if log_y:
            # abundance_floor already removed non-positive sample–taxon pairs.
            ax.set_yscale("log")
            ax.yaxis.set_major_formatter(
                mpl.ticker.FuncFormatter(lambda value, _pos: f"1e{int(round(np.log10(value)))}" if value > 0 else "")
            )
            ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
            if task in comp.ABUNDANCE_FLOOR:
                comp._frame_abundance_axis(ax, comp.ABUNDANCE_FLOOR[task])


def _match_column_limits(axes) -> None:
    """Give the three models one y scale within each task."""
    for col, (task, _ylabel, _title, log_y) in enumerate(PANELS):
        column = [axes[row, col] for row in range(axes.shape[0])]
        if log_y and task in comp.ABUNDANCE_FLOOR:
            ymins, ymaxs = [], []
            for ax in column:
                ymin, ymax = float(ax.dataLim.ymin), float(ax.dataLim.ymax)
                if np.isfinite(ymin) and ymin > 0:
                    ymins.append(ymin)
                if np.isfinite(ymax) and ymax > 0:
                    ymaxs.append(ymax)
            if not ymins or not ymaxs:
                continue
            floor = comp.ABUNDANCE_FLOOR[task]
            lo = 10 ** (np.log10(min(min(ymins), floor)) - 0.25)
            hi = 10 ** (np.log10(max(ymaxs)) + 0.30)
            ticks = [10.0 ** exp for exp in range(-4, 2) if lo < 10.0 ** exp < hi]
            for ax in column:
                ax.set_ylim(lo, hi)
                if ticks:
                    ax.set_yticks(ticks)
            continue
        bounds = [ax.get_ylim() for ax in column]
        lo = min(item[0] for item in bounds)
        hi = max(item[1] for item in bounds)
        for ax in column:
            ax.set_ylim(lo, hi)


def _seat_brackets(fig, axes) -> None:
    """Keep brackets just above the whiskers without a tall empty cap.

    Three-group panels need the full stack. A single comparison only needs
    the lower bracket, so those panels keep more of the frame for the boxes.
    """
    fig.canvas.draw()
    for ax in axes.ravel():
        needed = max(comp._required_bracket_points(ax), 14.0)
        comp._ensure_bracket_headroom(ax, points=needed)
    for col in range(len(PANELS)):
        column = [axes[row, col] for row in range(axes.shape[0])]
        lowers, uppers = [], []
        for ax in column:
            y0, y1 = ax.get_ylim()
            lowers.append(min(y0, y1))
            uppers.append(max(y0, y1))
        for ax in column:
            ax.set_ylim(min(lowers), max(uppers))
    fig.canvas.draw()
    for ax in axes.ravel():
        comp.place_brackets_above_data(ax)


def draw(series: dict[str, dict[str, np.ndarray]], tests: pd.DataFrame, stem_name: str) -> None:
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
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.6,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
        }
    )
    fig, axes = plt.subplots(1, 4, figsize=(7.20, 3.20), constrained_layout=False)
    fig.subplots_adjust(left=0.055, right=0.99, top=0.70, bottom=0.21, wspace=0.42)
    _draw_panels(axes, series, tests, show_titles=True, show_xlabels=True)
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


ROW_LABEL = {
    "deepseek-pro": "deepseek-v4-pro",
    "deepseek-flash": "deepseek-v4-flash",
    "glm-flash": "glm5.3-flash",
}
DA_PANELS = (
    ("16s_da", "DESeq2 log2 fold change", "16S differential\nabundance", False),
    ("shotgun_da", "log2 fold change", "shotgun differential\nabundance", False),
)


def _load_da(model: str):
    """Session-mean log2 fold changes already restricted to the plotted methods."""
    import plot_da_prompt_comparison as da

    series = {}
    frames = []
    sources = (
        ("16s_da", "16s_da_by_prompt_values.tsv", "16s_da_by_prompt_tests.tsv"),
        ("shotgun_da", "shotgun_da_by_prompt_values.tsv", "shotgun_da_by_prompt_tests.tsv"),
    )
    for task, values_name, tests_name in sources:
        frame = pd.read_csv(TABLES / values_name, sep="\t")
        frame = frame.loc[frame["model"] == model]
        by_level = {}
        for level, sub in frame.groupby("level"):
            by_level[str(level)] = sub.groupby("taxon")["log2fc"].mean()
        populated = [item for item in by_level.values() if len(item)]
        shared = set.intersection(*(set(item.index) for item in populated)) if populated else set()
        series[task] = {
            level: item.loc[sorted(shared)].to_numpy(dtype=float)
            for level, item in by_level.items()
            if len(item) and shared
        }
        panel_tests = pd.read_csv(TABLES / tests_name, sep="\t")
        panel_tests = panel_tests.loc[panel_tests["model"] == model].copy()
        panel_tests["task"] = task
        frames.append(panel_tests)
        print(f"{model} {task}: shared_taxa={len(shared)}", flush=True)
    shotgun_label = {
        key: f"{da.SHOTGUN_METHOD[key]} log2 fold change" for key in da.SHOTGUN_METHOD
    }
    return series, pd.concat(frames, ignore_index=True), shotgun_label[model]


def _align_ylabel_column(axes, renderer) -> None:
    """Line up one column of y-axis titles on the same right edge."""
    boxes = [ax.yaxis.label.get_window_extent(renderer) for ax in axes]
    target = min(box.x1 for box in boxes)
    for ax, box in zip(axes, boxes):
        x_pos, y_pos = ax.yaxis.label.get_position()
        new_x, _ = ax.transAxes.inverted().transform((x_pos + (target - box.x1), 0))
        ax.yaxis.set_label_coords(new_x, y_pos)


def draw_stacked(rows, stem_name: str) -> None:
    """Three models by six tasks, including differential abundance, in one grid."""
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
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.6,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
        }
    )
    fig = plt.figure(figsize=(7.20, 6.20))
    grid = fig.add_gridspec(len(rows), 6, left=0.125, right=0.968, top=0.90, bottom=0.125, wspace=0.74, hspace=0.18)
    axes = grid.subplots()
    panels = PANELS + DA_PANELS
    for row_i, (model, series, tests, da_series, da_tests, shotgun_ylabel) in enumerate(rows):
        merged = dict(series)
        merged.update(da_series)

        def ylabel_for(task, default, label=shotgun_ylabel):
            if task != "shotgun_da":
                return default
            if label.startswith("Mann-Whitney"):
                return "Mann-Whitney log2FC"
            return label

        _draw_panels(
            axes[row_i],
            merged,
            pd.concat([tests, da_tests], ignore_index=True),
            show_titles=row_i == 0,
            show_xlabels=row_i == len(rows) - 1,
            panels=panels,
            ylabel_for=ylabel_for,
            box_width=0.58,
            label_rotation=90,
        )
        if row_i == 0:
            for ax in axes[row_i]:
                ax.set_title(ax.get_title(), pad=8)
        for ax in axes[row_i]:
            ax.yaxis.labelpad = 1
    _match_column_limits(axes)
    _seat_brackets(fig, axes)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for col in range(axes.shape[1]):
        _align_ylabel_column([axes[row, col] for row in range(axes.shape[0])], renderer)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    points_to_px = fig.dpi / 72.0
    name_half_px = 0.5 * 7.0 * points_to_px
    name_gap_px = 12.0 * points_to_px
    name_left_px = []
    for row_i, (model, _series, _tests, _da_series, _da_tests, _shotgun_ylabel) in enumerate(rows):
        label_box = axes[row_i, 0].yaxis.label.get_window_extent(renderer)
        center_y = (label_box.y0 + label_box.y1) / 2.0
        center_x = label_box.x0 - name_gap_px - name_half_px
        name_left_px.append(center_x - name_half_px)
        anchor_x, anchor_y = fig.transFigure.inverted().transform((center_x, center_y))
        fig.text(
            anchor_x,
            anchor_y,
            ROW_LABEL[model],
            rotation=90,
            rotation_mode="anchor",
            va="center",
            ha="center",
            fontsize=7,
            fontweight="bold",
        )
    letter_x = (min(name_left_px) - 12.0 * points_to_px) / fig.bbox.width
    for row_i, letter in enumerate("abc"):
        top = axes[row_i, 0].get_window_extent().y1 + 4.0 * points_to_px
        fig.text(
            letter_x,
            top / fig.bbox.height,
            letter,
            ha="left",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )
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
    frames = []
    stacked = []
    for model, stem_name in MODELS:
        series = {}
        series.update(diversity_by_prompt(model))
        series.update(composition_by_prompt(model))
        tests = prompt_tests(series)
        tests.insert(0, "model", model)
        frames.append(tests)
        da_series, da_tests, shotgun_ylabel = _load_da(model)
        stacked.append((model, series, tests, da_series, da_tests, shotgun_ylabel))
        tests.to_csv(TABLES / f"{stem_name}_tests.tsv", sep="\t", index=False)
        draw(series, tests, stem_name)
    pd.concat(frames, ignore_index=True).to_csv(TABLES / "prompt_comparison_tests.tsv", sep="\t", index=False)
    draw_stacked(stacked, "by_prompt_models")


if __name__ == "__main__":
    main()
