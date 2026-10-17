#!/usr/bin/env python3
"""Compare model distributions within each fixed prompt.

Within one prompt, pool sample-level values from the three sessions of each
model and draw boxplots. Pairwise two-sided Mann–Whitney U tests are
Holm-adjusted inside each panel. Values are the same quantity in every box:

- 16S alpha: per-sample Shannon index, averaged across sessions
- 16S beta: one unordered sample pair's weighted UniFrac distance, averaged across sessions
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
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
import score_robustness as sr
from audit_panel_alignment import require_matplotlib_panel_alignment

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
MODEL_ORDER = ["glm-flash", "deepseek-flash", "deepseek-pro"]
MODEL_LABEL = {
    "glm-flash": "glm5.3-flash",
    "deepseek-flash": "deepseek-v4-flash",
    "deepseek-pro": "deepseek-v4-pro",
}
LEVEL_ORDER = ["detailed", "medium", "simple"]
LEVEL_LABEL = {"detailed": "Detailed", "medium": "Medium", "simple": "Simple"}
PALETTE = {
    "glm5.3-flash": "#B64342",
    "deepseek-v4-flash": "#42949E",
    "deepseek-v4-pro": "#0F4D92",
}
PAIRS = [
    ("glm-flash", "deepseek-flash"),
    ("glm-flash", "deepseek-pro"),
    ("deepseek-flash", "deepseek-pro"),
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


def holm(pvalues: list[float]) -> list[float]:
    m = len(pvalues)
    order = np.argsort(pvalues)
    adjusted = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        value = min(1.0, (m - rank) * float(pvalues[idx]))
        value = max(running, value)
        adjusted[idx] = value
        running = value
    return adjusted.tolist()


def pairwise_distances(frame: pd.DataFrame) -> pd.Series:
    """One finite distance per unordered sample pair. The diagonal is omitted."""
    values = frame.to_numpy(dtype=float)
    paired = np.stack([values, values.T], axis=0)
    sym = np.nanmean(paired, axis=0)
    labels = [str(label) for label in frame.index]
    out = {}
    for i, left in enumerate(labels):
        for offset, value in enumerate(sym[i, i + 1 :]):
            if not np.isfinite(value):
                continue
            right = labels[i + 1 + offset]
            if left == right:
                continue
            a, b = (left, right) if left <= right else (right, left)
            out[f"{a}|{b}"] = float(value)
    return pd.Series(out, dtype=float)


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    jobs = pd.read_csv(sr.JOBS)
    stored = {}
    for row in jobs.itertuples(index=False):
        analysis = sr.ROOT / row.job_id / "analysis"
        print(f"extract {row.session}", flush=True)
        shannon, shannon_source = sr.collect_shannon(analysis)
        distances = sr.collect_distances(analysis)
        stored[row.session] = {
            "row": row,
            "shannon": shannon,
            "shannon_source": shannon_source,
            "distances": distances,
        }
    records = []
    coverage = []
    for session, payload in stored.items():
        row = payload["row"]
        shannon = payload["shannon"]
        n_shannon_raw = 0 if shannon is None else int(shannon.shape[0])
        n_shannon_zero = 0 if shannon is None else int((shannon == 0).sum())
        if shannon is not None:
            kept = shannon[shannon > 0]
            for sample_id, value in kept.items():
                records.append(
                    {
                        "session": session,
                        "replicate": row.replicate,
                        "level": row.level,
                        "model": row.model,
                        "task": "16s_shannon",
                        "quantity": "shannon",
                        "sample_id": sample_id,
                        "value": float(value),
                        "source": payload["shannon_source"],
                    }
                )
        metric = "weighted_unifrac"
        beta_source = ""
        n_beta = 0
        if metric in payload["distances"]:
            series, beta_source = payload["distances"][metric]
            pairs = pairwise_distances(series)
            n_beta = int(pairs.shape[0])
            for pair_id, value in pairs.items():
                records.append(
                    {
                        "session": session,
                        "replicate": row.replicate,
                        "level": row.level,
                        "model": row.model,
                        "task": "16s_beta",
                        "quantity": metric,
                        "sample_id": pair_id,
                        "value": float(value),
                        "source": beta_source,
                    }
                )
        coverage.append(
            {
                "session": session,
                "level": row.level,
                "model": row.model,
                "replicate": row.replicate,
                "shannon_n_raw": n_shannon_raw,
                "shannon_n_zero_excluded": n_shannon_zero,
                "shannon_n": 0 if shannon is None else int((shannon > 0).sum()),
                "beta_metric": metric,
                "beta_n": n_beta,
                "beta_present": n_beta > 0,
            }
        )
    session_values = pd.DataFrame.from_records(records)
    return average_then_intersect(session_values, "sample_id"), pd.DataFrame.from_records(coverage)


def average_then_intersect(session_values: pd.DataFrame, unit_col: str) -> pd.DataFrame:
    """Average sessions of one model, then keep units shared by the models being compared."""
    if session_values.empty:
        return session_values
    averaged = (
        session_values.groupby(["level", "model", "task", "quantity", unit_col], as_index=False)
        .agg(value=("value", "mean"), n_sessions=("session", "nunique"))
    )
    kept = []
    for (level, task), part in averaged.groupby(["level", "task"], sort=False):
        present = [model for model in MODEL_ORDER if (part["model"] == model).any()]
        if len(present) < 2:
            continue
        shared = set.intersection(*(set(part.loc[part["model"] == model, unit_col]) for model in present))
        if not shared:
            continue
        print(f"{level} {task}: models={len(present)} shared_{unit_col}={len(shared)}", flush=True)
        kept.append(part.loc[part["model"].isin(present) & part[unit_col].isin(shared)])
    if not kept:
        return averaged.iloc[0:0]
    return pd.concat(kept, ignore_index=True)


def mannwhitney_table(values: pd.DataFrame) -> pd.DataFrame:
    rows = []
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
        usable_idx = [i for i, pvalue in enumerate(raw) if np.isfinite(pvalue)]
        adjusted = holm([raw[i] for i in usable_idx]) if usable_idx else []
        holm_p = [np.nan] * len(raw)
        for slot, value in zip(usable_idx, adjusted):
            holm_p[slot] = value
        for (left, right, a, b, stat, pvalue), p_holm in zip(bundles, holm_p):
            rows.append(
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
    return pd.DataFrame.from_records(rows)


def _fmt_p(value: float) -> str:
    if not np.isfinite(value):
        return "n.a."
    if value < 0.001:
        return f"{value:.1e}"
    return f"{value:.3f}"


def _color_boxes(ax: plt.Axes) -> None:
    labels = [tick.get_text() for tick in ax.get_xticklabels()]
    for patch, label in zip(ax.artists, labels):
        color = PALETTE.get(label, "#666666")
        patch.set_facecolor(color)
        patch.set_edgecolor(color)
        patch.set_alpha(0.85)
    for line in ax.lines:
        line.set_color("#222222")
        line.set_linewidth(0.6)


def plot_combined() -> None:
    """Stack the diversity and composition model comparisons into one figure."""
    from plot_composition_da_distributions import draw_grouped

    diversity_values = pd.read_csv(TABLES / "model_distribution_values.tsv", sep="\t")
    diversity_tests = pd.read_csv(TABLES / "model_distribution_tests.tsv", sep="\t")
    composition_values = pd.read_csv(TABLES / "composition_da_distribution_values.tsv", sep="\t")
    composition_tests = pd.read_csv(TABLES / "composition_da_distribution_tests.tsv", sep="\t")
    composition_tasks = {"16s_composition", "shotgun_composition"}
    draw_grouped(
        pd.concat(
            [
                diversity_values,
                composition_values.loc[composition_values["task"].isin(composition_tasks)],
            ],
            ignore_index=True,
        ),
        pd.concat(
            [
                diversity_tests,
                composition_tests.loc[composition_tests["task"].isin(composition_tasks)],
            ],
            ignore_index=True,
        ),
        [
            ("16s_shannon", "Shannon index", "16S alpha diversity"),
            ("16s_beta", "Pairwise weighted UniFrac distance", "16S beta diversity"),
            ("16s_composition", "Genus relative abundance", "16S genus-level taxonomic profiling"),
            ("shotgun_composition", "Species relative abundance", "shotgun species-level taxonomic profiling"),
        ],
        "model_distribution_diversity_composition",
        log_y=composition_tasks,
    )


def plot(values: pd.DataFrame, tests: pd.DataFrame) -> None:
    from plot_composition_da_distributions import draw_grouped

    draw_grouped(
        values,
        tests,
        [
            ("16s_shannon", "Shannon index", "16S alpha diversity"),
            ("16s_beta", "Pairwise weighted UniFrac distance", "16S beta diversity"),
        ],
        "model_distribution_diversity",
        log_y=False,
    )


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    values, coverage = extract()
    before = int(coverage["shannon_n_raw"].sum())
    after = int(coverage["shannon_n"].sum())
    excluded = int(coverage["shannon_n_zero_excluded"].sum())
    print(f"Shannon values before zero exclusion: {before}", flush=True)
    print(f"Shannon zeros excluded: {excluded}", flush=True)
    print(f"Shannon values after exclusion: {after}", flush=True)
    tests = mannwhitney_table(values)
    values.to_csv(TABLES / "model_distribution_values.tsv", sep="\t", index=False)
    coverage.to_csv(TABLES / "model_distribution_coverage.tsv", sep="\t", index=False)
    tests.to_csv(TABLES / "model_distribution_tests.tsv", sep="\t", index=False)
    plot(values, tests)
    print(tests.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
