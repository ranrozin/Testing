#!/usr/bin/env python3
"""Score restaurants for Ran. Higher = better, 0 to 1.

score = weighted average of the core axes (authentic, good, character,
casual, light) + a small affinity bonus (Thai, wine, ...) when the place
is actually strong there. Explainable: it is just the average of the
0-1 judgments in the options file.

Area, walk time, open-now, and family are gates from the current
question. They decide who gets scored, never the score itself.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text())


def require_dims(values: dict, dims: list[str], label: str) -> None:
    missing = [d for d in dims if d not in values]
    if missing:
        raise SystemExit(f"{label} missing {', '.join(missing)}")


def merged_gates(profile: dict, query: str) -> dict[str, float]:
    gates = dict(profile["gates"]["always"])
    extra = profile["gates"].get(query)
    if extra is None:
        raise SystemExit(f"unknown query '{query}'")
    gates.update(extra)
    return gates


def gate_failures(vector: dict, gates: dict[str, float]) -> list[str]:
    failed = []
    for dim, minimum in gates.items():
        got = float(vector[dim])
        if got < float(minimum):
            failed.append(f"{dim} {got:.2f} < {minimum}")
    return failed


def core_score(vector: dict, weights: dict) -> float:
    total = sum(float(weights[d]) * float(vector[d]) for d in weights)
    return total / sum(float(w) for w in weights.values())


def affinity_bonus(profile: dict, vector: dict, query: str) -> tuple[float, list[str]]:
    weights = profile["affinityWeights"][query]
    hits = []
    bonus = 0.0
    for dim, weight in weights.items():
        value = float(vector[dim])
        if weight > 0 and value >= 0.6:
            bonus += (value - 0.5) * float(weight)
            hits.append(dim)
    return bonus * float(profile["affinityBonusScale"]), hits


def weak_spots(vector: dict, weights: dict, n: int = 3) -> list[dict]:
    rows = []
    for dim, weight in weights.items():
        miss = (1.0 - float(vector[dim])) * float(weight)
        if miss > 0.15:
            rows.append((miss, {"dim": dim, "value": vector[dim]}))
    rows.sort(key=lambda row: row[0], reverse=True)
    return [row[1] for row in rows[:n]]


def confidence(editorial: float) -> str:
    if editorial >= 0.75:
        return "high"
    if editorial >= 0.45:
        return "medium"
    return "unverified"


def rank(profile: dict, options: list[dict], query: str) -> dict:
    if query not in profile["affinityWeights"]:
        raise SystemExit(f"unknown query '{query}'")
    weights = profile["coreWeights"]
    gates = merged_gates(profile, query)
    eligible = []
    ineligible = []
    for opt in options:
        require_dims(opt["vector"], profile["dimensions"], opt["name"])
        failed = gate_failures(opt["vector"], gates)
        if failed:
            ineligible.append({"name": opt["name"], "reason": "; ".join(failed)})
            continue
        core = core_score(opt["vector"], weights)
        bonus, hits = affinity_bonus(profile, opt["vector"], query)
        eligible.append(
            {
                "name": opt["name"],
                "score": round(min(1.0, core + bonus), 2),
                "coreScore": round(core, 2),
                "affinityBonus": round(bonus, 2),
                "affinityHits": hits,
                "weakSpots": weak_spots(opt["vector"], weights),
                "confidence": confidence(float(opt["vector"]["editorial"])),
            }
        )
    eligible.sort(key=lambda row: row["score"], reverse=True)
    return {
        "query": query,
        "metric": "weighted_core_average_plus_affinity_bonus",
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
