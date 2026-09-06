#!/usr/bin/env python3
"""Distance between Ran's taste vector and scored options. Stdlib only.

Uses weighted Euclidean distance (lower = closer). Query gates drop options
that fail a hard constraint, e.g. near_hotel requires near_now >= 0.75.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text())


def weights_for(profile: dict, query: str) -> dict[str, float]:
    table = profile["queryWeights"]
    if query not in table:
        raise SystemExit(f"unknown query '{query}'. use: {', '.join(table)}")
    return table[query]


def vec(dims: list[str], values: dict[str, float], weights: dict[str, float]) -> list[float]:
    missing = [d for d in dims if d not in values]
    if missing:
        raise SystemExit(f"missing dimensions: {', '.join(missing)}")
    extra = [k for k in values if k not in dims]
    if extra:
        raise SystemExit(f"unknown dimensions: {', '.join(extra)}")
    return [float(values[d]) * float(weights[d]) for d in dims]


def euclidean(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def gate_failures(opt: dict, gates: dict[str, float]) -> list[str]:
    values = opt["vector"]
    failed = []
    for dim, minimum in gates.items():
        got = float(values[dim])
        if got < float(minimum):
            failed.append(f"{dim} {got:.2f} < {minimum}")
    return failed


def rank(profile: dict, options: list[dict], query: str) -> dict:
    dims = profile["dimensions"]
    weights = weights_for(profile, query)
    gates = profile.get("gates", {}).get(query, {})
    ran = vec(dims, profile["ran"], weights)
    eligible = []
    ineligible = []
    for opt in options:
        name = opt["name"]
        failed = gate_failures(opt, gates)
        if failed:
            ineligible.append({"name": name, "reason": "; ".join(failed)})
            continue
        option_vec = vec(dims, opt["vector"], weights)
        eligible.append(
            {
                "name": name,
                "distance": round(euclidean(ran, option_vec), 3),
            }
        )
    eligible.sort(key=lambda row: row["distance"])
    return {
        "query": query,
        "metric": "weighted_euclidean",
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
    profile = load_json(args.profile)
    options = load_json(args.options)
    if not isinstance(options, list):
        raise SystemExit("options file must be a JSON list of {name, vector}")
    result = rank(profile, options, args.query)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if result["pick"] is None:
        sys.exit(2)


if __name__ == "__main__":
    main()
