#!/usr/bin/env python3
"""Prompt comparison of differential-abundance effect sizes.

Separate from by_prompt_models.png. Each figure has one row per model and
compares Detailed with Medium only. A point is one taxon present under both
prompts. Within a prompt, a taxon’s value is the median log2 fold change
inside a result table, then the mean across sessions that ran the chosen
method. Simple-prompt sessions are excluded.

16S uses genus-level DESeq2 log2FoldChange for every model. Shotgun cannot:
GLM-Flash uses DESeq2, DeepSeek-Flash uses the log2FC reported with
Mann-Whitney, and DeepSeek-Pro uses the log2FC reported with Wilcoxon.
Those three log2FC definitions are not the same quantity.

The bracket is one two-sided Mann-Whitney U test on the two taxon-level
distributions. Taxa from one experiment are not independent replicates.
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

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
ROW_ORDER = ("deepseek-pro", "deepseek-flash", "glm-flash")
ROW_LABEL = {
    "deepseek-pro": "DeepSeek-Pro",
    "deepseek-flash": "DeepSeek-Flash",
    "glm-flash": "GLM-Flash",
}
PROMPT_ORDER = ("detailed", "medium")
PROMPT_LABEL = {"detailed": "Detailed", "medium": "Medium"}
PROMPT_COLOR = {"detailed": "#0072B2", "medium": "#E69F00"}

# Sessions that ran the method used for that model and prompt. ASV-only
# DESeq2 sessions are omitted so they are not mixed into the genus comparison.
SIXTEEN_S_SESSIONS = {
    "glm-flash": {
        "detailed": (
            "1-robustness-detailed-glm-flash",
            "2-robustness-detailed-glm-flash",
            "3-robustness-detailed-glm-flash",
        ),
        "medium": ("2-robustness-medium-glm-flash",),
    },
    "deepseek-flash": {
        "detailed": (
            "1-robustness-detailed-deepseek-flash",
            "2-robustness-detailed-deepseek-flash",
        ),
        "medium": (
            "1-robustness-medium-deepseek-flash",
            "3-robustness-medium-deepseek-flash",
        ),
    },
    "deepseek-pro": {
        "detailed": ("1-robustness-detailed-deepseek-pro",),
        "medium": ("2-robustness-medium-deepseek-pro",),
    },
}
SHOTGUN_SESSIONS = {
    "glm-flash": {
        "detailed": (
            "1-robustness-detailed-glm-flash",
            "3-robustness-detailed-glm-flash",
        ),
        "medium": ("2-robustness-medium-glm-flash",),
    },
    "deepseek-flash": {
        "detailed": ("3-robustness-detailed-deepseek-flash",),
        "medium": ("3-robustness-medium-deepseek-flash",),
    },
    "deepseek-pro": {
        "detailed": ("2-robustness-detailed-deepseek-pro",),
        "medium": ("2-robustness-medium-deepseek-pro",),
    },
}
SHOTGUN_METHOD = {
    "glm-flash": "DESeq2",
    "deepseek-flash": "Mann-Whitney",
    "deepseek-pro": "Wilcoxon",
}
SIXTEEN_S_METHOD = {model: "DESeq2" for model in ROW_ORDER}


def _jobs() -> pd.DataFrame:
    return pd.read_csv(sr.JOBS)


def _analysis(jobs: pd.DataFrame, session: str) -> Path:
    job_id = jobs.loc[jobs["session"] == session, "job_id"].iloc[0]
    return sr.ROOT / job_id / "analysis"


def _header(path: Path) -> str:
    try:
        return path.open(errors="replace").readline()
    except OSError:
        return ""


def _is_deseq2(path: Path, header: str) -> bool:
    folded = header.lower().replace(" ", "").replace("_", "")
    return "deseq" in str(path).lower() or "log2foldchange" in folded or ("lfcse" in folded and "basemean" in folded)


def _collapsed(path: Path, rank: str, min_finite_fraction: float) -> pd.DataFrame | None:
    parsed = comp.parse_lfc_table(path)
    if parsed is None:
        return None
    parsed = parsed.loc[parsed["rank"] == rank]
    if parsed.empty:
        return None
    hash_like = parsed["taxon"].str.fullmatch(r"[0-9a-f]{16,}").mean()
    if hash_like > 0.2:
        return None
    if float(parsed["finite_fraction"].iloc[0]) < min_finite_fraction:
        return None
    collapsed = parsed.groupby("taxon", as_index=False)["log2fc"].median()
    collapsed["source"] = str(path)
    return collapsed


def _has_rank_statistic(header: str) -> bool:
    columns = [item.strip().lower() for item in header.replace(",", "\t").split("\t")]
    return "u" in columns or "statistic_u" in columns or "p_mwu" in columns


def _best_deseq(analysis: Path, rank: str, shotgun: bool) -> pd.Series:
    best = None
    best_n = 0
    for path in comp.da_candidates(analysis):
        rel = str(path.relative_to(analysis)).lower()
        if "superseded" in rel or "annotated" in path.name.lower():
            continue
        is_shotgun = "shotgun" in rel or "metaphlan" in rel
        if shotgun != is_shotgun:
            continue
        if not _is_deseq2(path, _header(path)):
            continue
        collapsed = _collapsed(path, rank, 0.5)
        if collapsed is None or len(collapsed) <= best_n:
            continue
        best_n = len(collapsed)
        best = collapsed
    if best is None:
        return pd.Series(dtype=float)
    return best.set_index("taxon")["log2fc"]


def _mann_whitney_species(analysis: Path) -> pd.Series:
    frames = []
    for path in comp.da_candidates(analysis):
        rel = str(path.relative_to(analysis)).lower()
        if "superseded" in rel or "genus" in rel or "welch" in rel:
            continue
        if "shotgun" not in rel:
            continue
        if not _has_rank_statistic(_header(path)):
            continue
        collapsed = _collapsed(path, "species", 0.0)
        if collapsed is not None:
            frames.append(collapsed)
    if not frames:
        return pd.Series(dtype=float)
    combined = pd.concat(frames, ignore_index=True)
    return combined.groupby("taxon")["log2fc"].median()


def _wilcoxon_species(analysis: Path) -> pd.Series:
    chosen = []
    for path in comp.da_candidates(analysis):
        rel = str(path.relative_to(analysis)).lower()
        name = path.name.lower()
        if "shotgun" not in rel or "genus" in rel or "candidate" in name:
            continue
        if not _has_rank_statistic(_header(path)):
            continue
        if "all" not in name and "wilcox" not in name:
            continue
        collapsed = _collapsed(path, "species", 0.0)
        if collapsed is not None:
            chosen.append(collapsed)
    if not chosen:
        return pd.Series(dtype=float)
    best = max(chosen, key=len)
    return best.set_index("taxon")["log2fc"]


def _mean_sessions(series_list: list[pd.Series]) -> pd.Series:
    present = [series for series in series_list if series is not None and len(series)]
    if not present:
        return pd.Series(dtype=float)
    return pd.concat(present, axis=1).mean(axis=1, skipna=True)


def _shared_prompts(by_level: dict[str, pd.Series]) -> dict[str, np.ndarray]:
    detailed = by_level.get("detailed", pd.Series(dtype=float))
    medium = by_level.get("medium", pd.Series(dtype=float))
    if not len(detailed) or not len(medium):
        return {}
    shared = sorted(set(detailed.index) & set(medium.index))
    if not shared:
        return {}
    return {
        "detailed": detailed.loc[shared].to_numpy(dtype=float),
        "medium": medium.loc[shared].to_numpy(dtype=float),
    }


def _prompt_test(values: dict[str, np.ndarray]) -> pd.DataFrame:
    left = values.get("detailed", np.array([]))
    right = values.get("medium", np.array([]))
    if len(left) < 5 or len(right) < 5:
        pvalue = np.nan
        stat = np.nan
    else:
        result = stats.mannwhitneyu(left, right, alternative="two-sided")
        pvalue = float(result.pvalue)
        stat = float(result.statistic)
    return pd.DataFrame(
        [
            {
                "model_a": "detailed",
                "model_b": "medium",
                "n_a": int(len(left)),
                "n_b": int(len(right)),
                "median_a": float(np.median(left)) if len(left) else np.nan,
                "median_b": float(np.median(right)) if len(right) else np.nan,
                "u_statistic": stat,
                "p_raw": pvalue,
                "p_holm": pvalue,
            }
        ]
    )


def _extract_16s(jobs: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    panels = {}
    records = []
    for model in ROW_ORDER:
        by_level = {}
        for level, sessions in SIXTEEN_S_SESSIONS[model].items():
            parts = []
            for session in sessions:
                series = _best_deseq(_analysis(jobs, session), "genus", shotgun=False)
                print(f"16s {session}: taxa={len(series)}", flush=True)
                if len(series):
                    parts.append(series)
                    for taxon, value in series.items():
                        records.append({"model": model, "level": level, "session": session, "taxon": taxon, "log2fc": float(value)})
            by_level[level] = _mean_sessions(parts)
        panels[model] = _shared_prompts(by_level)
        print(f"16s {model}: shared_genera={len(panels[model].get('detailed', []))}", flush=True)
    return panels, pd.DataFrame.from_records(records)


def _shotgun_series(model: str, analysis: Path) -> pd.Series:
    if model == "glm-flash":
        return _best_deseq(analysis, "species", shotgun=True)
    if model == "deepseek-flash":
        return _mann_whitney_species(analysis)
    return _wilcoxon_species(analysis)


def _extract_shotgun(jobs: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    panels = {}
    records = []
    for model in ROW_ORDER:
        by_level = {}
        for level, sessions in SHOTGUN_SESSIONS[model].items():
            parts = []
            for session in sessions:
                series = _shotgun_series(model, _analysis(jobs, session))
                print(f"shotgun {session}: taxa={len(series)}", flush=True)
                if len(series):
                    parts.append(series)
                    for taxon, value in series.items():
                        records.append({"model": model, "level": level, "session": session, "taxon": taxon, "log2fc": float(value)})
            by_level[level] = _mean_sessions(parts)
        panels[model] = _shared_prompts(by_level)
        print(f"shotgun {model}: shared_species={len(panels[model].get('detailed', []))}", flush=True)
    return panels, pd.DataFrame.from_records(records)


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
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.6,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def _draw(panels: dict, ylabels: dict[str, str], title: str, stem_name: str) -> None:
    _style()
    fig, axes = plt.subplots(3, 1, figsize=(3.50, 5.50), sharex=True)
    fig.subplots_adjust(left=0.30, right=0.97, top=0.90, bottom=0.08, hspace=0.42)
    tests = []
    for ax, model in zip(axes, ROW_ORDER):
        values = panels[model]
        present = [level for level in PROMPT_ORDER if len(values.get(level, [])) > 0]
        for index, level in enumerate(present):
            ax.boxplot(
                [values[level]],
                positions=[index],
                widths=0.42,
                patch_artist=True,
                showfliers=False,
                boxprops={"facecolor": PROMPT_COLOR[level], "edgecolor": PROMPT_COLOR[level], "linewidth": 0.6, "alpha": 0.85},
                whiskerprops={"color": "#222222", "linewidth": 0.6},
                capprops={"color": "#222222", "linewidth": 0.6},
                medianprops={"color": "#222222", "linewidth": 0.6},
            )
        ax.set_xlim(-0.55, 1.55)
        ax.set_xticks([0, 1])
        ax.set_xticklabels([PROMPT_LABEL[level] for level in PROMPT_ORDER])
        ax.tick_params(axis="x", labelbottom=ax is axes[-1], length=0)
        ax.set_ylabel(ylabels[model])
        panel_test = _prompt_test(values)
        panel_test.insert(0, "model", model)
        tests.append(panel_test)
        if len(present) == 2:
            comp._add_significance_brackets(ax, present, panel_test, centers=[0.0, 1.0])
        position = ax.get_position()
        fig.text(
            0.02,
            position.y0 + position.height / 2.0,
            ROW_LABEL[model],
            rotation=90,
            rotation_mode="anchor",
            va="center",
            ha="left",
            fontsize=7,
            fontweight="bold",
        )
    axes[0].set_title(title, pad=8)
    fig.canvas.draw()
    for ax in axes:
        comp._ensure_bracket_headroom(ax, points=22)
        comp.place_brackets_above_data(ax)
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
    pd.concat(tests, ignore_index=True).to_csv(TABLES / f"{stem_name}_tests.tsv", sep="\t", index=False)


def _session_cell(rows: pd.DataFrame, model: str, level: str) -> str:
    """Replicates that entered the mean, as n/3."""
    sub = rows.loc[(rows["model"] == model) & (rows["level"] == level)]
    n_sessions = sub["session"].nunique()
    return f"{n_sessions}/3"


def _method_summary(analysis: str, methods: dict[str, str], rows: pd.DataFrame, panels: dict) -> pd.DataFrame:
    """One supplementary-table row per model: method and sessions averaged."""
    records = []
    for model in ROW_ORDER:
        records.append(
            {
                "analysis": analysis,
                "model": ROW_LABEL[model],
                "method": "Mann-Whitney U" if methods[model] == "Mann-Whitney" else methods[model],
                "detailed_sessions": _session_cell(rows, model, "detailed"),
                "medium_sessions": _session_cell(rows, model, "medium"),
                "taxa_compared": len(panels[model].get("detailed", [])),
            }
        )
    return pd.DataFrame.from_records(records)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    jobs = _jobs()
    sixteen, sixteen_rows = _extract_16s(jobs)
    shotgun, shotgun_rows = _extract_shotgun(jobs)
    sixteen_rows.to_csv(TABLES / "16s_da_by_prompt_values.tsv", sep="\t", index=False)
    shotgun_rows.to_csv(TABLES / "shotgun_da_by_prompt_values.tsv", sep="\t", index=False)
    summary = pd.concat(
        [
            _method_summary("16S rRNA gene, genus", SIXTEEN_S_METHOD, sixteen_rows, sixteen),
            _method_summary("Shotgun metagenome, species", SHOTGUN_METHOD, shotgun_rows, shotgun),
        ],
        ignore_index=True,
    )
    summary.to_csv(TABLES / "da_prompt_method_summary.tsv", sep="\t", index=False)
    ylabels = {
        "16s": {model: "DESeq2 log2 fold change" for model in ROW_ORDER},
        "shotgun": {model: f"{SHOTGUN_METHOD[model]} log2 fold change" for model in ROW_ORDER},
    }
    _draw(sixteen, ylabels["16s"], "16S differential abundance", "16s_da_by_prompt")
    _draw(shotgun, ylabels["shotgun"], "shotgun differential abundance", "shotgun_da_by_prompt")


if __name__ == "__main__":
    main()
