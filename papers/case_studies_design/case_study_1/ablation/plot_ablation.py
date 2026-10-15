#!/usr/bin/env python3
"""Session-level Case 1 component ablation, excluding the runtime-extension condition.

Scores archived jobs listed in job_ids.csv. A listed job whose directory is
absent is omitted and reported; it is not treated as a failed analysis.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "robustness"))
sys.path.insert(0, "/home/comp/cszmli/.cursor/skills/nature-figure/scripts")
import plot_task_completion as tc
import score_robustness as sr
from audit_panel_alignment import require_matplotlib_panel_alignment

OUT = Path(__file__).resolve().parent
TABLES = OUT / "tables"
FIGS = OUT / "figures"
PAPER_FIGS = OUT.parents[2] / "figures"
JOBS = OUT / "job_ids.csv"
ROOT = sr.ROOT

CONDITION_ORDER = ("full", "no-skills", "no-coding")
CONDITION_LABEL = {
    "full": "Full",
    "no-skills": "\u2212Skills",
    "no-coding": "\u2212Exec guidance",
}
TASKS = (
    ("16s_alpha", "16S\nalpha"),
    ("16s_beta", "16S\nbeta"),
    ("16s_taxonomy", "16S\ntaxonomy"),
    ("16s_da", "16S\nDA"),
    ("metaphlan", "MetaPhlAn\ntable"),
    ("shotgun_da", "Shotgun\nDA"),
    ("figures", "Analysis\nfigures"),
    ("scripts", "Analysis\nscripts"),
    ("report", "Analysis\nreport"),
)
METHODS = (
    ("depth_norm", "Depth\nnormalization"),
    ("shannon", "Shannon\ndiversity"),
    ("weighted_unifrac", "Weighted\nUniFrac"),
    ("unweighted_unifrac", "Unweighted\nUniFrac"),
    ("bray_curtis", "Bray\u2013Curtis\ndistance"),
    ("weighted_pcoa", "wUniFrac\nPCoA"),
    ("permanova", "PERMANOVA\n "),
    ("permdisp", "PERMDISP\n "),
)
COMPLETE = "#C5D8F0"
MISSING = "#F6D5D2"
MISS_MARK = "#7A2E2C"
RULE = "#4D4D4D"


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _text_head(path: Path, limit: int = 12000) -> str:
    try:
        return path.read_text(errors="replace")[:limit]
    except OSError:
        return ""


def _first_lines(path: Path, count: int = 8) -> list[str]:
    lines = []
    try:
        with path.open(errors="replace") as handle:
            for line in handle:
                lines.append(line.rstrip("\n"))
                if len(lines) >= count:
                    break
    except OSError:
        return []
    return lines


def genus_table(analysis: Path) -> tuple[int, str]:
    ok, source = tc.genus_abundance(analysis)
    if ok:
        return 1, source
    for path in sr.walk_files(analysis):
        if path.suffix.lower() not in {".tsv", ".csv"}:
            continue
        rel = str(path.relative_to(analysis)).lower()
        if any(token in rel for token in ("shotgun", "metaphlan", "deseq", "maaslin", "diff", "volcano")):
            continue
        if path.stat().st_size < 1000 or path.stat().st_size > 30_000_000:
            continue
        name = path.name.lower()
        lines = [line for line in _first_lines(path, 12) if line.strip()]
        if len(lines) < 4:
            continue
        sample_line = next((line for line in lines if line.count("\t") >= 30), "")
        taxon_line = next((line for line in lines if not line.startswith("#")), "")
        named_genus = any(token in name for token in ("genus", "level6", "level-6", "l6"))
        if "g__" not in taxon_line and not named_genus:
            continue
        if sample_line and ("g__" in taxon_line or named_genus):
            return 1, str(path.relative_to(analysis))
    return 0, ""


def narrative_report(analysis: Path) -> tuple[int, str]:
    preferred = []
    for path in sr.walk_files(analysis):
        rel = str(path.relative_to(analysis))
        low = rel.lower()
        if any(token in low for token in ("export", "provenance", "qzv")):
            continue
        if path.suffix.lower() not in {".md", ".txt"} or path.stat().st_size < 1000:
            continue
        name = path.name.lower()
        if name in {"report.md", "analysis_report.md", "summary_report.md", "readme_report.md"}:
            preferred.append(rel)
        elif "report" in name and "characterization" not in name and "qc" not in name:
            preferred.append(rel)
    if not preferred:
        return 0, ""
    preferred.sort(key=len)
    return 1, preferred[0]


def analysis_scripts(job_root: Path) -> tuple[int, str]:
    roots = [job_root / "analysis", job_root / "reproducibility" / "generated_scripts"]
    found = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py", ".r", ".sh"}:
                continue
            if path.name.startswith("_") or path.stat().st_size < 200:
                continue
            if "export" in str(path).lower():
                continue
            found.append(_rel(path, job_root))
    return (1, found[0]) if found else (0, "")


def analysis_figures(analysis: Path) -> tuple[int, str]:
    for path in sr.walk_files(analysis):
        if path.suffix.lower() not in {".png", ".pdf", ".svg"}:
            continue
        low = str(path.relative_to(analysis)).lower()
        if any(token in low for token in ("frequency", "provenance", "index.html")):
            continue
        if path.stat().st_size < 8000:
            continue
        return 1, str(path.relative_to(analysis))
    return 0, ""


def _metric_kind(rel: str) -> str | None:
    low = rel.lower()
    if "unweighted" in low and "unifrac" in low:
        return "unweighted_unifrac"
    if "weighted" in low and "unifrac" in low:
        return "weighted_unifrac"
    if "bray" in low:
        return "bray_curtis"
    return None


def method_evidence(analysis: Path) -> dict[str, str]:
    evidence = {key: "" for key, _label in METHODS}
    for path in sr.walk_files(analysis):
        rel = str(path.relative_to(analysis))
        low = rel.lower()
        if any(token in low for token in ("raref", "sampling-depth", "sampling_depth")) and not evidence["depth_norm"]:
            evidence["depth_norm"] = rel
        if "shannon" in low and path.suffix.lower() in {".tsv", ".csv", ".txt", ".qza"} and not evidence["shannon"]:
            evidence["shannon"] = rel
        kind = _metric_kind(rel)
        if kind and not evidence[kind] and (
            "distance" in low or "matrix" in low or path.suffix.lower() == ".qza"
        ):
            evidence[kind] = rel
        if kind == "weighted_unifrac" and "pcoa" in low and not evidence["weighted_pcoa"]:
            evidence["weighted_pcoa"] = rel
        if any(token in low for token in ("permanova", "adonis")) and not evidence["permanova"]:
            evidence["permanova"] = rel
        if any(token in low for token in ("permdisp", "permdip", "betadisper")) and not evidence["permdisp"]:
            evidence["permdisp"] = rel
    for path in sr.walk_files(analysis):
        if path.suffix.lower() not in {".tsv", ".txt", ".csv"} or path.stat().st_size > 2_000_000:
            continue
        rel = str(path.relative_to(analysis))
        if "export" in rel.lower():
            continue
        text = _text_head(path, 8000).upper()
        if "PERMANOVA" in text and not evidence["permanova"]:
            evidence["permanova"] = rel
        if "PERMDISP" in text and not evidence["permdisp"]:
            evidence["permdisp"] = rel
        if evidence["permanova"] and evidence["permdisp"]:
            break
    return evidence


def score_jobs(jobs: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    rows = []
    missing = []
    for row in jobs.itertuples(index=False):
        job_root = ROOT / row.job_id
        analysis = job_root / "analysis"
        if not analysis.is_dir():
            missing.append(f"{row.session} {row.job_id}")
            continue
        print(f"scoring {row.session}", flush=True)
        shared = tc.score_session(analysis)
        genus_ok, genus_source = genus_table(analysis)
        figure_ok, figure_source = analysis_figures(analysis)
        script_ok, script_source = analysis_scripts(job_root)
        report_ok, report_source = narrative_report(analysis)
        task_sources = {
            "16s_alpha": shared["16s_alpha"],
            "16s_beta": shared["16s_beta"],
            "16s_taxonomy": (genus_ok, genus_source),
            "16s_da": shared["16s_da"],
            "metaphlan": shared["shotgun_taxonomy"],
            "shotgun_da": shared["shotgun_da"],
            "figures": (figure_ok, figure_source),
            "scripts": (script_ok, script_source),
            "report": (report_ok, report_source),
        }
        for key, _label in TASKS:
            done, source = task_sources[key]
            rows.append(
                {
                    "session": row.session,
                    "replicate": int(row.replicate),
                    "condition": row.condition,
                    "job_id": row.job_id,
                    "item_type": "task",
                    "item": key,
                    "complete": int(done),
                    "evidence": source,
                }
            )
        methods = method_evidence(analysis)
        for key, _label in METHODS:
            rows.append(
                {
                    "session": row.session,
                    "replicate": int(row.replicate),
                    "condition": row.condition,
                    "job_id": row.job_id,
                    "item_type": "method",
                    "item": key,
                    "complete": int(bool(methods[key])),
                    "evidence": methods[key],
                }
            )
    return pd.DataFrame.from_records(rows), missing


def session_order(scores: pd.DataFrame) -> pd.DataFrame:
    sessions = (
        scores[["session", "replicate", "condition", "job_id"]]
        .drop_duplicates()
        .copy()
    )
    sessions["condition"] = pd.Categorical(sessions["condition"], CONDITION_ORDER, ordered=True)
    return sessions.sort_values(["condition", "replicate"]).reset_index(drop=True)


def matrix_for(scores: pd.DataFrame, sessions: pd.DataFrame, items: tuple[tuple[str, str], ...]) -> np.ndarray:
    grid = np.zeros((len(sessions), len(items)), dtype=float)
    lookup = {
        (row.session, row.item): int(row.complete)
        for row in scores.itertuples(index=False)
    }
    for i, session in enumerate(sessions.itertuples(index=False)):
        for j, (key, _label) in enumerate(items):
            grid[i, j] = lookup[(session.session, key)]
    return grid


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
            "axes.linewidth": 0.6,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def _draw_matrix(ax, grid: np.ndarray, xlabels: list[str], ylabels: list[str], title: str) -> None:
    ax.imshow(
        grid,
        cmap=ListedColormap([MISSING, COMPLETE]),
        vmin=0,
        vmax=1,
        aspect="auto",
        interpolation="nearest",
        origin="upper",
    )
    ax.set_xticks(np.arange(grid.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(grid.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xticks(range(grid.shape[1]))
    ax.set_xticklabels(xlabels)
    ax.set_yticks(range(grid.shape[0]))
    ax.set_yticklabels(ylabels)
    ax.tick_params(length=0, pad=2)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("#E5E7EB")
        spine.set_linewidth(0.4)
    ax.set_title(title, loc="left", pad=8, fontweight="medium")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i, j] == 0:
                ax.text(j, i, "\u00d7", ha="center", va="center", color=MISS_MARK, fontsize=8, fontweight="bold")
    # Separators follow the displayed session blocks: full, no-skills, no-coding.
    boundaries = []
    label_conditions = [label.split("  ")[0] for label in ylabels]
    for index in range(1, len(label_conditions)):
        if label_conditions[index] != label_conditions[index - 1]:
            boundaries.append(index - 0.5)
    for boundary in boundaries:
        ax.axhline(boundary, color=RULE, linewidth=0.6, zorder=3)


def draw(scores: pd.DataFrame, sessions: pd.DataFrame) -> None:
    _style()
    ylabels = [
        f"{CONDITION_LABEL[row.condition]}  {int(row.replicate)}"
        for row in sessions.itertuples(index=False)
    ]
    task_grid = matrix_for(scores[scores["item_type"] == "task"], sessions, TASKS)
    method_grid = matrix_for(scores[scores["item_type"] == "method"], sessions, METHODS)
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(7.20, 5.35),
        gridspec_kw={"hspace": 0.42, "height_ratios": [1, 1]},
    )
    fig.subplots_adjust(left=0.16, right=0.985, top=0.90, bottom=0.08)
    _draw_matrix(axes[0], task_grid, [label for _key, label in TASKS], ylabels, "Requested outputs")
    _draw_matrix(
        axes[1],
        method_grid,
        [label for _key, label in METHODS],
        ylabels,
        "Specified methods",
    )
    for ax, letter in ((axes[0], "a"), (axes[1], "b")):
        ax.text(
            -0.01,
            1.16,
            letter,
            transform=ax.transAxes,
            fontsize=8,
            fontweight="bold",
            ha="left",
            va="bottom",
        )
    fig.legend(
        handles=[
            Patch(facecolor=COMPLETE, edgecolor="#E5E7EB", linewidth=0.4, label="Completed"),
            Patch(facecolor=MISSING, edgecolor="#E5E7EB", linewidth=0.4, label="Not produced"),
        ],
        loc="upper right",
        bbox_to_anchor=(0.985, 0.985),
        ncol=2,
        frameon=False,
        fontsize=7,
        handlelength=1.2,
        handleheight=0.8,
        borderaxespad=0,
        columnspacing=1.2,
    )
    stem = FIGS / "component_ablation"
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
    fig.savefig(stem.with_suffix(".png"), dpi=600)
    fig.savefig(stem.with_suffix(".tiff"), dpi=600)
    PAPER_FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(PAPER_FIGS / "component_ablation.pdf")
    fig.savefig(PAPER_FIGS / "component_ablation.png", dpi=600)
    plt.close(fig)


def summarize(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for condition in CONDITION_ORDER:
        part = scores[scores["condition"] == condition]
        if part.empty:
            continue
        n_sessions = part["session"].nunique()
        for item_type, items in (("task", TASKS), ("method", METHODS)):
            block = part[part["item_type"] == item_type]
            n_items = len(items)
            completed = int(block["complete"].sum())
            rows.append(
                {
                    "condition": condition,
                    "item_type": item_type,
                    "n_sessions": n_sessions,
                    "n_items": n_items,
                    "n_completed": completed,
                    "n_possible": n_sessions * n_items,
                }
            )
    return pd.DataFrame.from_records(rows)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    jobs = pd.read_csv(JOBS)
    scores, missing = score_jobs(jobs)
    if scores.empty:
        raise SystemExit("no archived ablation jobs were scored")
    sessions = session_order(scores)
    summary = summarize(scores)
    scores.to_csv(TABLES / "session_scores.tsv", sep="\t", index=False)
    summary.to_csv(TABLES / "condition_summary.tsv", sep="\t", index=False)
    draw(scores, sessions)
    print(summary.to_string(index=False))
    missed = scores[scores["complete"] == 0]
    print("missing items")
    print(missed[["session", "item_type", "item"]].to_string(index=False) if len(missed) else "(none)")
    if missing:
        print("unarchived jobs")
        for item in missing:
            print(item)


if __name__ == "__main__":
    main()
