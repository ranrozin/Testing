#!/usr/bin/env python3
"""Rank restaurants against Ran's taste.

Place score uses only the restaurant (and his standing taste).
Where he is, walk, and open-now are this question: they gate options,
they are not stored on his profile.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text())


def require_dims(values: dict, dims: list[str], label: str) -> None:
    missing = [d for d in dims if d not in values]
    if missing:
        raise SystemExit(f"{label} missing {', '.join(missing)}")


def weighted_vec(dims: list[str], values: dict, weights: dict) -> list[float]:
    return [float(values[d]) * float(weights[d]) for d in dims]


def euclidean(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def merged_gates(profile: dict, query: str) -> dict[str, float]:
    always = dict(profile.get("gates", {}).get("always", {}))
    extra = profile.get("gates", {}).get(query)
    if extra is None and query != "always":
        raise SystemExit(f"unknown query '{query}'")
    always.update(extra or {})
    return always


def gate_failures(opt: dict, gates: dict[str, float]) -> list[str]:
    values = opt["vector"]
    failed = []
    for dim, minimum in gates.items():
        got = float(values[dim])
        if got < float(minimum):
            failed.append(f"{dim} {got:.2f} < {minimum}")
    return failed


def drivers(core: list[str], ran: dict, option: dict, weights: dict, n: int = 3) -> list[dict]:
    gaps = []
    for d in core:
        gap = (float(ran[d]) - float(option[d])) * float(weights[d])
        if gap > 0.05:
            gaps.append(
                {
                    "dim": d,
                    "ran": ran[d],
                    "option": option[d],
                    "gap": round(gap, 3),
                }
            )
    gaps.sort(key=lambda row: row["gap"], reverse=True)
    return gaps[:n]


def affinity_hits(profile: dict, option: dict, query: str) -> tuple[float, list[str]]:
    weights = profile["affinityWeights"][query]
    hits = []
    bonus = 0.0
    for dim, weight in weights.items():
        score = float(option[dim])
        if weight > 0 and score >= 0.6:
            bonus += (score - 0.5) * float(weight)
            hits.append(dim)
    return bonus * float(profile.get("affinityBonusScale", 0.2)), hits


def confidence(editorial: float) -> str:
    if editorial >= 0.75:
        return "high"
    if editorial >= 0.45:
        return "medium"
    return "unverified"


def rank(profile: dict, options: list[dict], query: str) -> dict:
    if query not in profile["affinityWeights"]:
        raise SystemExit(f"unknown query '{query}'")
    core = profile["roles"]["core"]
    all_dims = profile["dimensions"]
    weights = profile["coreWeights"]
    gates = merged_gates(profile, query)
    ran = profile["ran"]
    ran_dims = core + profile["roles"]["affinity"] + profile["roles"]["confidence"]
    require_dims(ran, ran_dims, "ran")
    ran_vec = weighted_vec(core, ran, weights)
    eligible = []
    ineligible = []
    for opt in options:
        require_dims(opt["vector"], all_dims, opt["name"])
        failed = gate_failures(opt, gates)
        if failed:
            ineligible.append({"name": opt["name"], "reason": "; ".join(failed)})
            continue
        opt_vec = weighted_vec(core, opt["vector"], weights)
        core_distance = euclidean(ran_vec, opt_vec)
        bonus, hits = affinity_hits(profile, opt["vector"], query)
        distance = round(max(0.0, core_distance - bonus), 3)
        eligible.append(
            {
                "name": opt["name"],
                "distance": distance,
                "coreDistance": round(core_distance, 3),
                "affinityBonus": round(bonus, 3),
                "affinityHits": hits,
                "drivers": drivers(core, ran, opt["vector"], weights),
                "confidence": confidence(float(opt["vector"]["editorial"])),
            }
        )
    eligible.sort(key=lambda row: row["distance"])
    return {
        "query": query,
        "metric": "core_euclidean_minus_affinity_bonus",
        "ranked": eligible,
        "ineligible": ineligible,
        "pick": eligible[0]["name"] if eligible else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="data/taste-vector.json", type=Path)
    parser.add_argument("--options", required=True, type=Path)
    parser.add_argument("--query", default="default")
    args = parser.parse_args()
    result = rank(load_json(args.profile), load_json(args.options), args.query)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if result["pick"] is None:
        sys.exit(2)


if __name__ == "__main__":
    main()
