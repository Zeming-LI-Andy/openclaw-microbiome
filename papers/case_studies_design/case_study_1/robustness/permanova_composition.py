#!/usr/bin/env python3
"""Blocked Bray–Curtis PERMANOVA for composition profiles.

Each observation is one session's relative-abundance profile of one sample.
Permutations shuffle model labels only inside a sample, so the test asks
whether model identity explains profile differences beyond the three sessions.
Taxa absent from a profile are entered as zero. P-values use 999 permutations.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_composition_da_distributions as comp
import score_robustness as sr
from plot_model_distributions import LEVEL_ORDER, MODEL_LABEL, MODEL_ORDER, PAIRS, holm

OUT = Path(__file__).resolve().parent / "tables"
N_PERM = 999
RNG = np.random.default_rng(13)


def _square_sums(D: np.ndarray, labels: np.ndarray) -> tuple[float, float, float]:
    """Anderson (2001) sums of squares from a square distance matrix."""
    n = D.shape[0]
    sq = np.triu(D * D, 1)
    ss_total = float(sq.sum() / n)
    ss_within = 0.0
    for group in np.unique(labels):
        idx = np.flatnonzero(labels == group)
        ng = len(idx)
        if ng < 2:
            continue
        block = sq[np.ix_(idx, idx)]
        ss_within += float(block.sum() / ng)
    return ss_total, ss_total - ss_within, ss_within


def permanova_f(D: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    n = int(labels.shape[0])
    ss_total, ss_among, ss_within = _square_sums(D, labels)
    k = int(np.unique(labels).size)
    if ss_total <= 0 or n <= k:
        return np.nan, np.nan
    r2 = ss_among / ss_total
    if ss_within <= 0:
        return np.inf, float(r2)
    pseudo_f = (ss_among / (k - 1)) / (ss_within / (n - k))
    return float(pseudo_f), float(r2)


def blocked_p(D: np.ndarray, labels: np.ndarray, blocks: np.ndarray) -> tuple[float, float, float]:
    observed, r2 = permanova_f(D, labels)
    if not np.isfinite(observed) and observed != np.inf:
        return observed, r2, np.nan
    exceed = 0
    for _ in range(N_PERM):
        shuffled = labels.copy()
        for block in np.unique(blocks):
            idx = np.flatnonzero(blocks == block)
            shuffled[idx] = RNG.permutation(shuffled[idx])
        pseudo_f, _ = permanova_f(D, shuffled)
        if pseudo_f >= observed:
            exceed += 1
    return observed, r2, (exceed + 1) / (N_PERM + 1)


def braycurtis(X: np.ndarray) -> np.ndarray:
    n = X.shape[0]
    D = np.zeros((n, n), dtype=float)
    for i in range(n - 1):
        diff = np.abs(X[i + 1 :] - X[i])
        denom = (X[i + 1 :] + X[i]).sum(axis=1)
        values = np.divide(diff.sum(axis=1), denom, out=np.zeros(diff.shape[0]), where=denom > 0)
        D[i, i + 1 :] = values
    return D + D.T


def _check_formula() -> None:
    D = np.array(
        [
            [0, 1, 1, 4],
            [1, 0, 3, 2],
            [1, 3, 0, 3],
            [4, 2, 3, 0],
        ],
        dtype=float,
    )
    labels = np.array([0, 0, 1, 1])
    A = -0.5 * D * D
    G = A - A.mean(axis=1, keepdims=True) - A.mean(axis=0, keepdims=True) + A.mean()
    ss_total, ss_among, _ss_within = _square_sums(D, labels)
    gower_among = 0.0
    for group in (0, 1):
        idx = np.flatnonzero(labels == group)
        gower_among += G[np.ix_(idx, idx)].sum() / len(idx)
    if abs(ss_total - np.trace(G)) > 1e-8 or abs(ss_among - gower_among) > 1e-8:
        raise RuntimeError("PERMANOVA sum-of-squares formula failed the Gower check")


def load_profiles() -> dict[tuple[str, str, str, str], pd.Series]:
    jobs = pd.read_csv(sr.JOBS)
    profiles = {}
    for row in jobs.itertuples(index=False):
        analysis = sr.ROOT / row.job_id / "analysis"
        print(f"extract {row.session}", flush=True)
        for kind, task in (("genus", "16s_composition"), ("species", "shotgun_composition")):
            matrix, _source = comp.best_composition(analysis, kind)
            if matrix is None:
                continue
            for sample_id, abundances in matrix.iterrows():
                values = pd.to_numeric(abundances, errors="coerce")
                values = values[np.isfinite(values.to_numpy(dtype=float))]
                profiles[(row.level, task, row.model, str(sample_id), row.session)] = values
    return profiles


def pair_matrix(profiles, level: str, task: str, left: str, right: str):
    chosen = []
    for key, series in profiles.items():
        key_level, key_task, model, sample_id, session = key
        if key_level == level and key_task == task and model in {left, right}:
            chosen.append((sample_id, model, session, series))
    if not chosen:
        return None
    counts = {}
    for sample_id, model, _session, _series in chosen:
        counts.setdefault(sample_id, set()).add(model)
    keep_samples = {sample_id for sample_id, models in counts.items() if models == {left, right}}
    chosen = [item for item in chosen if item[0] in keep_samples]
    if len(keep_samples) < 2:
        return None
    taxa = sorted(set().union(*(set(item[3].index) for item in chosen)))
    columns = {taxon: i for i, taxon in enumerate(taxa)}
    X = np.zeros((len(chosen), len(taxa)), dtype=float)
    labels = np.empty(len(chosen), dtype=int)
    blocks = np.empty(len(chosen), dtype=object)
    for row_i, (sample_id, model, _session, series) in enumerate(chosen):
        for taxon, value in series.items():
            X[row_i, columns[taxon]] = float(value)
        labels[row_i] = 0 if model == left else 1
        blocks[row_i] = sample_id
    return X, labels, blocks, len(keep_samples)


def prompt_matrix(profiles, model: str, task: str, left: str, right: str):
    chosen = []
    for key, series in profiles.items():
        key_level, key_task, key_model, sample_id, session = key
        if key_model == model and key_task == task and key_level in {left, right}:
            chosen.append((sample_id, key_level, session, series))
    if not chosen:
        return None
    counts = {}
    for sample_id, level, _session, _series in chosen:
        counts.setdefault(sample_id, set()).add(level)
    keep_samples = {sample_id for sample_id, levels in counts.items() if levels == {left, right}}
    chosen = [item for item in chosen if item[0] in keep_samples]
    if len(keep_samples) < 2:
        return None
    taxa = sorted(set().union(*(set(item[3].index) for item in chosen)))
    columns = {taxon: i for i, taxon in enumerate(taxa)}
    X = np.zeros((len(chosen), len(taxa)), dtype=float)
    labels = np.empty(len(chosen), dtype=int)
    blocks = np.empty(len(chosen), dtype=object)
    for row_i, (sample_id, level, _session, series) in enumerate(chosen):
        for taxon, value in series.items():
            X[row_i, columns[taxon]] = float(value)
        labels[row_i] = 0 if level == left else 1
        blocks[row_i] = sample_id
    return X, labels, blocks, len(keep_samples)


def median_profile_distance(X: np.ndarray, labels: np.ndarray, blocks: np.ndarray) -> float:
    """Median across samples of Bray–Curtis between the two session-mean profiles."""
    distances = []
    for sample_id in np.unique(blocks):
        idx = np.flatnonzero(blocks == sample_id)
        left = X[idx][labels[idx] == 0]
        right = X[idx][labels[idx] == 1]
        if len(left) == 0 or len(right) == 0:
            continue
        a = left.mean(axis=0)
        b = right.mean(axis=0)
        denom = float((a + b).sum())
        distances.append(0.0 if denom == 0 else float(np.abs(a - b).sum() / denom))
    return float(np.median(distances)) if distances else np.nan


def build_difference_table(profiles) -> pd.DataFrame:
    """Per-sample Bray–Curtis difference for model pairs and prompt pairs."""
    prompt_pairs = [("detailed", "medium"), ("detailed", "simple"), ("medium", "simple")]
    rows = []

    def accumulate(family: str, group: str, task: str, pairs, builder):
        bundles = []
        raw = []
        for left, right in pairs:
            built = builder(left, right)
            if built is None:
                diffs = pd.DataFrame(columns=["sample_id", "difference"])
                pvalue, _n = np.nan, 0
            else:
                X, labels, blocks, _n_samples = built
                diffs = sample_differences(X, labels, blocks)
                pvalue, _n = wilcoxon_greater(diffs["difference"].to_numpy(dtype=float))
            raw.append(pvalue)
            bundles.append((left, right, diffs, pvalue))
        usable = [i for i, pvalue in enumerate(raw) if np.isfinite(pvalue)]
        adjusted = holm([raw[i] for i in usable]) if usable else []
        holm_p = [np.nan] * len(raw)
        for slot, value in zip(usable, adjusted):
            holm_p[slot] = value
        for (left, right, diffs, pvalue), p_holm in zip(bundles, holm_p):
            for record in diffs.to_dict("records"):
                rows.append(
                    {
                        "family": family,
                        "group": group,
                        "task": task,
                        "left": left,
                        "right": right,
                        "sample_id": record["sample_id"],
                        "difference": record["difference"],
                        "p_greater": pvalue,
                        "p_holm": p_holm,
                    }
                )

    for level in LEVEL_ORDER:
        for task in ("16s_composition", "shotgun_composition"):
            accumulate(
                "model_within_prompt",
                level,
                task,
                PAIRS,
                lambda left, right, level=level, task=task: pair_matrix(profiles, level, task, left, right),
            )
    for model in MODEL_ORDER:
        for task in ("16s_composition", "shotgun_composition"):
            accumulate(
                "prompt_within_model",
                model,
                task,
                prompt_pairs,
                lambda left, right, model=model, task=task: prompt_matrix(profiles, model, task, left, right),
            )
    return pd.DataFrame.from_records(rows)


def compare_prompts() -> None:
    _check_formula()
    profiles = load_profiles()
    prompt_pairs = [("detailed", "medium"), ("detailed", "simple"), ("medium", "simple")]
    rows = []
    for model in MODEL_ORDER:
        for task in ("16s_composition", "shotgun_composition"):
            raw = []
            bundles = []
            for left, right in prompt_pairs:
                built = prompt_matrix(profiles, model, task, left, right)
                if built is None:
                    raw.append(np.nan)
                    bundles.append((left, right, 0, np.nan, np.nan, np.nan, np.nan))
                    continue
                X, labels, blocks, n_samples = built
                print(f"{model} {task} {left} vs {right}: profiles={len(labels)} samples={n_samples}", flush=True)
                distance = median_profile_distance(X, labels, blocks)
                D = braycurtis(X)
                pseudo_f, r2, pvalue = blocked_p(D, labels, blocks)
                raw.append(pvalue)
                bundles.append((left, right, n_samples, distance, pseudo_f, r2, pvalue))
            usable = [i for i, pvalue in enumerate(raw) if np.isfinite(pvalue)]
            adjusted = holm([raw[i] for i in usable]) if usable else []
            holm_p = [np.nan] * len(raw)
            for slot, value in zip(usable, adjusted):
                holm_p[slot] = value
            for (left, right, n_samples, distance, pseudo_f, r2, pvalue), p_holm in zip(bundles, holm_p):
                rows.append(
                    {
                        "model": model,
                        "task": task,
                        "prompt_a": left,
                        "prompt_b": right,
                        "n_samples": n_samples,
                        "median_braycurtis": distance,
                        "pseudo_F": pseudo_f,
                        "R2": r2,
                        "p_perm": pvalue,
                        "p_holm": p_holm,
                        "n_perm": N_PERM,
                    }
                )
    result = pd.DataFrame.from_records(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT / "permanova_braycurtis_prompts.tsv", sep="\t", index=False)
    view = result.copy()
    view["model"] = view["model"].map(MODEL_LABEL)
    print(view.to_string(index=False), flush=True)


def main() -> None:
    _check_formula()
    profiles = load_profiles()
    rows = []
    for level in LEVEL_ORDER:
        for task in ("16s_composition", "shotgun_composition"):
            raw = []
            bundles = []
            for left, right in PAIRS:
                built = pair_matrix(profiles, level, task, left, right)
                if built is None:
                    raw.append(np.nan)
                    bundles.append((left, right, 0, np.nan, np.nan, np.nan))
                    continue
                X, labels, blocks, n_samples = built
                print(f"{level} {task} {left} vs {right}: profiles={len(labels)} samples={n_samples}", flush=True)
                D = braycurtis(X)
                pseudo_f, r2, pvalue = blocked_p(D, labels, blocks)
                raw.append(pvalue)
                bundles.append((left, right, n_samples, pseudo_f, r2, pvalue))
            usable = [i for i, pvalue in enumerate(raw) if np.isfinite(pvalue)]
            adjusted = holm([raw[i] for i in usable]) if usable else []
            holm_p = [np.nan] * len(raw)
            for slot, value in zip(usable, adjusted):
                holm_p[slot] = value
            for (left, right, n_samples, pseudo_f, r2, pvalue), p_holm in zip(bundles, holm_p):
                rows.append(
                    {
                        "level": level,
                        "task": task,
                        "model_a": left,
                        "model_b": right,
                        "n_samples": n_samples,
                        "pseudo_F": pseudo_f,
                        "R2": r2,
                        "p_perm": pvalue,
                        "p_holm": p_holm,
                        "n_perm": N_PERM,
                    }
                )
    result = pd.DataFrame.from_records(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT / "permanova_braycurtis_models.tsv", sep="\t", index=False)
    view = result.copy()
    view["model_a"] = view["model_a"].map(MODEL_LABEL)
    view["model_b"] = view["model_b"].map(MODEL_LABEL)
    print(view.to_string(index=False), flush=True)


def _mean_pairwise(rows: np.ndarray) -> float:
    if len(rows) < 2:
        return np.nan
    distances = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            denom = float((rows[i] + rows[j]).sum())
            distances.append(0.0 if denom == 0 else float(np.abs(rows[i] - rows[j]).sum() / denom))
    return float(np.mean(distances))


def sample_differences(X: np.ndarray, labels: np.ndarray, blocks: np.ndarray) -> pd.DataFrame:
    """One row per sample: between-condition distance minus within-condition session distance."""
    records = []
    for sample_id in np.unique(blocks):
        idx = np.flatnonzero(blocks == sample_id)
        left = X[idx][labels[idx] == 0]
        right = X[idx][labels[idx] == 1]
        if len(left) == 0 or len(right) == 0:
            continue
        within_parts = [value for value in (_mean_pairwise(left), _mean_pairwise(right)) if np.isfinite(value)]
        if not within_parts:
            continue
        within = float(np.mean(within_parts))
        a = left.mean(axis=0)
        b = right.mean(axis=0)
        denom = float((a + b).sum())
        between = 0.0 if denom == 0 else float(np.abs(a - b).sum() / denom)
        records.append({"sample_id": sample_id, "between": between, "within": within, "difference": between - within})
    return pd.DataFrame.from_records(records)


def wilcoxon_greater(differences: np.ndarray) -> tuple[float, int]:
    from scipy import stats

    usable = differences[np.isfinite(differences) & (differences != 0)]
    if len(usable) == 0:
        return np.nan, 0
    result = stats.wilcoxon(usable, alternative="greater", zero_method="wilcox")
    return float(result.pvalue), int(len(usable))


def compare_wilcoxon() -> None:
    _check_formula()
    profiles = load_profiles()
    prompt_pairs = [("detailed", "medium"), ("detailed", "simple"), ("medium", "simple")]
    rows = []

    def add_family(records, family, task, group, pairs_done):
        raw = [item["p_greater"] for item in pairs_done]
        usable = [i for i, pvalue in enumerate(raw) if np.isfinite(pvalue)]
        adjusted = holm([raw[i] for i in usable]) if usable else []
        holm_p = [np.nan] * len(raw)
        for slot, value in zip(usable, adjusted):
            holm_p[slot] = value
        for item, p_holm in zip(pairs_done, holm_p):
            item["p_holm"] = p_holm
            item["family"] = family
            item["task"] = task
            item["group"] = group
            records.append(item)

    for level in LEVEL_ORDER:
        for task in ("16s_composition", "shotgun_composition"):
            done = []
            for left, right in PAIRS:
                built = pair_matrix(profiles, level, task, left, right)
                done.append(_wilcoxon_row(built, left, right, "model"))
            add_family(rows, "model_within_prompt", task, level, done)
    for model in MODEL_ORDER:
        for task in ("16s_composition", "shotgun_composition"):
            done = []
            for left, right in prompt_pairs:
                built = prompt_matrix(profiles, model, task, left, right)
                done.append(_wilcoxon_row(built, left, right, "prompt"))
            add_family(rows, "prompt_within_model", task, model, done)
    result = pd.DataFrame.from_records(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT / "wilcoxon_braycurtis_differences.tsv", sep="\t", index=False)
    view = result.copy()
    view["group"] = view["group"].replace({**MODEL_LABEL, "detailed": "Detailed", "medium": "Medium", "simple": "Simple"})
    view["left"] = view["left"].replace({**MODEL_LABEL, "detailed": "Detailed", "medium": "Medium", "simple": "Simple"})
    view["right"] = view["right"].replace({**MODEL_LABEL, "detailed": "Detailed", "medium": "Medium", "simple": "Simple"})
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 80)
    pd.set_option("display.float_format", lambda value: f"{value:.4g}")
    print(view.to_string(index=False), flush=True)


def _wilcoxon_row(built, left: str, right: str, kind: str) -> dict:
    empty = {
        "left": left,
        "right": right,
        "n_samples": 0,
        "n_tested": 0,
        "n_positive": 0,
        "median_between": np.nan,
        "median_within": np.nan,
        "median_difference": np.nan,
        "p_greater": np.nan,
    }
    if built is None:
        return empty
    X, labels, blocks, _n_samples = built
    print(f"{kind} {left} vs {right}: profiles={len(labels)}", flush=True)
    diffs = sample_differences(X, labels, blocks)
    pvalue, n_tested = wilcoxon_greater(diffs["difference"].to_numpy(dtype=float))
    return {
        "left": left,
        "right": right,
        "n_samples": int(len(diffs)),
        "n_tested": n_tested,
        "n_positive": int((diffs["difference"] > 0).sum()),
        "median_between": float(diffs["between"].median()),
        "median_within": float(diffs["within"].median()),
        "median_difference": float(diffs["difference"].median()),
        "p_greater": pvalue,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "prompts":
        compare_prompts()
    elif len(sys.argv) > 1 and sys.argv[1] == "wilcoxon":
        compare_wilcoxon()
    else:
        main()
