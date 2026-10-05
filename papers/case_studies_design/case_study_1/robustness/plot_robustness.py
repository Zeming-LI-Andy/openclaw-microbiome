#!/usr/bin/env python3
"""Plot Case 1 robustness completion and within-cell concordance."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
from audit_panel_alignment import require_matplotlib_panel_alignment

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"

TASK_ORDER = ["16s_alpha", "16s_beta", "16s_da", "shotgun_da"]
TASK_LABEL = {
    "16s_alpha": "16S alpha diversity",
    "16s_beta": "16S beta diversity",
    "16s_da": "16S differential abundance",
    "shotgun_da": "Shotgun differential abundance",
}
MODEL_ORDER = ["glm-flash", "deepseek-flash", "deepseek-pro"]
MODEL_LABEL = {
    "glm-flash": "GLM-Flash",
    "deepseek-flash": "DeepSeek-Flash",
    "deepseek-pro": "DeepSeek-Pro",
}
LEVEL_ORDER = ["detailed", "medium", "simple"]
LEVEL_LABEL = {"detailed": "Detailed", "medium": "Medium", "simple": "Simple"}
PALETTE = {
    "GLM-Flash": "#B64342",
    "DeepSeek-Flash": "#42949E",
    "DeepSeek-Pro": "#0F4D92",
}

AGREEMENT = [
    ("16s_alpha", "16s_alpha_pearson_r", "Pearson r"),
    ("16s_beta", "16s_beta_mantel_r", "Mantel r"),
    ("16s_da", "16s_da_jaccard", "Jaccard index"),
    ("shotgun_da", "shotgun_da_jaccard", "Jaccard index"),
]
SECONDARY = [
    ("16s_alpha", "16s_alpha_mean_abs_diff", "Mean |Δ Shannon|"),
    ("16s_beta", "16s_beta_procrustes_disparity", "Procrustes disparity"),
    ("16s_da", "16s_da_effect_spearman_r", "Effect-size Spearman r"),
    ("shotgun_da", "shotgun_da_effect_spearman_r", "Effect-size Spearman r"),
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


def _label(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["Model"] = out["model"].map(MODEL_LABEL)
    out["Prompt"] = pd.Categorical(out["level"].map(LEVEL_LABEL), ["Detailed", "Medium", "Simple"], ordered=True)
    return out


def _panel_letter(ax: plt.Axes, letter: str) -> None:
    ax.text(
        -0.16,
        1.06,
        letter,
        transform=ax.transAxes,
        fontsize=8,
        fontweight="bold",
        va="bottom",
        ha="left",
        clip_on=False,
    )


def _save(fig: plt.Figure, stem: Path) -> None:
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
    fig.savefig(stem.with_suffix(".tiff"), dpi=600)
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)


def plot_completion(sessions: pd.DataFrame) -> None:
    long = sessions.melt(
        id_vars=["session", "model", "level", "replicate"],
        value_vars=TASK_ORDER,
        var_name="task",
        value_name="score",
    )
    long = _label(long)
    long.to_csv(TABLES / "completion_plot_data.tsv", sep="\t", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.9), sharex=True, sharey=True)
    for ax, task, letter in zip(axes.ravel(), TASK_ORDER, "abcd"):
        part = long[long["task"] == task]
        sns.barplot(
            data=part,
            x="Prompt",
            y="score",
            hue="Model",
            hue_order=list(PALETTE),
            palette=PALETTE,
            order=["Detailed", "Medium", "Simple"],
            ci=None,
            saturation=1,
            ax=ax,
        )
        sns.stripplot(
            data=part,
            x="Prompt",
            y="score",
            hue="Model",
            hue_order=list(PALETTE),
            order=["Detailed", "Medium", "Simple"],
            dodge=True,
            jitter=0.08,
            size=2.4,
            linewidth=0.3,
            edgecolor="white",
            palette=["#272727"] * 3,
            ax=ax,
        )
        ax.set_title(TASK_LABEL[task], pad=6)
        ax.set_xlabel("")
        ax.set_ylabel("Artifact score" if task in {"16s_alpha", "16s_da"} else "")
        ax.set_ylim(-0.05, 1.18)
        ax.set_yticks([0, 0.5, 1])
        _panel_letter(ax, letter)
        if ax.legend_ is not None:
            ax.legend_.remove()
    handles = [
        mpl.patches.Patch(facecolor=color, edgecolor="none", label=label)
        for label, color in PALETTE.items()
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.995))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.08, wspace=0.22, hspace=0.38)
    _save(fig, FIGS / "completion_artifact_score")


def _concordance_long(pairs: pd.DataFrame, spec: list[tuple[str, str, str]]) -> pd.DataFrame:
    frames = []
    for task, column, metric in spec:
        part = pairs[["model", "level", "replicate_a", "replicate_b", column]].copy()
        part = part.rename(columns={column: "value"})
        part["task"] = task
        part["metric"] = metric
        frames.append(part)
    long = _label(pd.concat(frames, ignore_index=True))
    n_before = int(len(long))
    long = long.loc[long["value"].notna()].copy()
    n_after = int(len(long))
    # Pairs without two usable artifacts are omitted from the boxplot.
    # Before/after counts: undefined concordance values are not plotted.
    print(f"concordance rows {n_before} -> {n_after} after dropping undefined pairs")
    return long


def plot_concordance(pairs: pd.DataFrame, spec: list[tuple[str, str, str]], stem: str, ylim, ylabel_by_task: bool) -> None:
    long = _concordance_long(pairs, spec)
    long.to_csv(TABLES / f"{stem}_plot_data.tsv", sep="\t", index=False)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.9), sharex=True)
    metrics = {task: metric for task, _, metric in spec}
    for ax, task, letter in zip(axes.ravel(), TASK_ORDER, "abcd"):
        part = long[long["task"] == task]
        if part.empty:
            ax.set_title(TASK_LABEL[task], pad=6)
            ax.text(0.5, 0.5, "No comparable pairs", transform=ax.transAxes, ha="center", va="center", fontsize=7)
            _panel_letter(ax, letter)
            continue
        sns.boxplot(
            data=part,
            x="Prompt",
            y="value",
            hue="Model",
            hue_order=list(PALETTE),
            palette=PALETTE,
            order=["Detailed", "Medium", "Simple"],
            fliersize=0,
            linewidth=0.6,
            saturation=1,
            ax=ax,
        )
        sns.stripplot(
            data=part,
            x="Prompt",
            y="value",
            hue="Model",
            hue_order=list(PALETTE),
            order=["Detailed", "Medium", "Simple"],
            dodge=True,
            jitter=0.08,
            size=2.6,
            linewidth=0.3,
            edgecolor="white",
            palette=["#272727"] * 3,
            ax=ax,
        )
        ax.set_title(TASK_LABEL[task], pad=6)
        ax.set_xlabel("")
        ax.set_ylabel(metrics[task] if ylabel_by_task or task in {"16s_alpha", "16s_da"} else "")
        if ylim is not None and task in {"16s_alpha", "16s_beta", "16s_da", "shotgun_da"} and stem == "concordance_agreement":
            ax.set_ylim(*ylim)
        if ax.legend_ is not None:
            ax.legend_.remove()
        _panel_letter(ax, letter)
    handles = [
        mpl.patches.Patch(facecolor=color, edgecolor="none", label=label)
        for label, color in PALETTE.items()
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.995))
    fig.subplots_adjust(left=0.10, right=0.985, top=0.86, bottom=0.08, wspace=0.32, hspace=0.38)
    _save(fig, FIGS / stem)


def main() -> None:
    _style()
    FIGS.mkdir(parents=True, exist_ok=True)
    sessions = pd.read_csv(TABLES / "completion_by_session.tsv", sep="\t")
    pairs = pd.read_csv(TABLES / "concordance_pairs.tsv", sep="\t")
    plot_completion(sessions)
    plot_concordance(pairs, AGREEMENT, "concordance_agreement", (0, 1.05), False)
    plot_concordance(pairs, SECONDARY, "concordance_secondary", None, True)


if __name__ == "__main__":
    main()
