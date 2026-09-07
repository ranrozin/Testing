#!/usr/bin/env python3
"""Tiny 30-day cache of scored options. No search dumps. Stdlib only.

Keyed from the current question (preset, city, area, kind).
Not taste, not where he lives, not the agent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CACHE_PATH = Path("data/search-cache.json")
MAX_AGE_DAYS = 30
MAX_ENTRIES = 40
MAX_OPTIONS = 4
MAX_INELIGIBLE = 4
MAX_NOTE = 120
MAX_ASKED = 140
MAX_BYTES = 64_000
VECTOR_DIMS = (
    "authentic_local",
    "neighborhood",
    "genuinely_good",
    "character",
    "casual",
    "light_food",
    "seafood",
    "asian_thai",
    "meat",
    "wine",
    "coffee",
    "near_now",
    "family_easy",
    "editorial",
)


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:40]


def make_key(preset: str, city: str, anchor: str, kind: str) -> str:
    return "|".join(
        [
            slug(preset) or "default",
            slug(city) or "any",
            slug(anchor) or "any",
            slug(kind) or "eat",
        ]
    )


def empty_cache() -> dict:
    return {"maxAgeDays": MAX_AGE_DAYS, "maxEntries": MAX_ENTRIES, "entries": []}


def load_cache(path: Path) -> dict:
    if not path.exists():
        return empty_cache()
    data = json.loads(path.read_text())
    data.setdefault("entries", [])
    return data


def clip(text: str | None, limit: int) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def compact_vector(vector: dict) -> dict[str, float]:
    missing = [d for d in VECTOR_DIMS if d not in vector]
    if missing:
        raise SystemExit(f"vector missing {', '.join(missing)}")
    return {d: round(float(vector[d]), 3) for d in VECTOR_DIMS}


def compact_option(raw: dict) -> dict:
    return {
        "name": clip(raw.get("name"), 80),
        "kind": clip(raw.get("kind"), 20) or "eat",
        "near": clip(raw.get("near"), 80),
        "note": clip(raw.get("note"), MAX_NOTE),
        "distance": round(float(raw["distance"]), 3) if raw.get("distance") is not None else None,
        "confidence": clip(raw.get("confidence"), 16),
        "vector": compact_vector(raw["vector"]),
    }


def prune(data: dict, now_ts: datetime | None = None) -> dict:
    now_ts = now_ts or now()
    cutoff = now_ts - timedelta(days=MAX_AGE_DAYS)
    kept = []
    for entry in data.get("entries", []):
        try:
            at = parse_time(entry["at"])
        except (KeyError, ValueError):
            continue
        if at >= cutoff:
            kept.append(entry)
    kept.sort(key=lambda e: e.get("at", ""), reverse=True)
    data["entries"] = kept[:MAX_ENTRIES]
    data["maxAgeDays"] = MAX_AGE_DAYS
    data["maxEntries"] = MAX_ENTRIES
    return data


def write_cache(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    while len(payload.encode()) > MAX_BYTES and data["entries"]:
        data["entries"].pop()
        payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(payload)


def lookup(path: Path, key: str) -> dict:
    data = prune(load_cache(path))
    write_cache(path, data)
    for entry in data["entries"]:
        if entry.get("key") == key:
            age_days = (now() - parse_time(entry["at"])).days
            return {"hit": True, "ageDays": age_days, "entry": entry}
    return {"hit": False, "key": key}


def save(path: Path, payload: dict) -> dict:
    key = payload.get("key") or make_key(
        payload.get("preset", "default"),
        payload.get("city", ""),
        payload.get("anchor", ""),
        payload.get("kind", "eat"),
    )
    options = [compact_option(opt) for opt in (payload.get("options") or [])[:MAX_OPTIONS]]
    ineligible = []
    for row in (payload.get("ineligible") or [])[:MAX_INELIGIBLE]:
        ineligible.append(
            {
                "name": clip(row.get("name"), 80),
                "reason": clip(row.get("reason"), 80),
            }
        )
    entry = {
        "key": key,
        "at": now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "asked": clip(payload.get("asked"), MAX_ASKED),
        "preset": clip(payload.get("preset"), 24) or "default",
        "city": clip(payload.get("city"), 40),
        "anchor": clip(payload.get("anchor"), 40),
        "kind": clip(payload.get("kind"), 20) or "eat",
        "pick": clip(payload.get("pick"), 80),
        "options": options,
        "ineligible": ineligible,
    }
    data = load_cache(path)
    data["entries"] = [e for e in data.get("entries", []) if e.get("key") != key]
    data["entries"].insert(0, entry)
    write_cache(path, prune(data))
    return {"saved": True, "key": key, "entries": len(load_cache(path)["entries"])}


def clear(path: Path) -> dict:
    write_cache(path, empty_cache())
    return {"cleared": True, "entries": 0}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=CACHE_PATH)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_key = sub.add_parser("key")
    p_key.add_argument("--preset", required=True)
    p_key.add_argument("--city", required=True)
    p_key.add_argument("--anchor", required=True)
    p_key.add_argument("--kind", default="eat")

    p_lookup = sub.add_parser("lookup")
    p_lookup.add_argument("--key", required=True)

    p_save = sub.add_parser("save")
    p_save.add_argument("--payload", required=True, type=Path)

    sub.add_parser("clear")

    args = parser.parse_args()
    if args.cmd == "key":
        result = {"key": make_key(args.preset, args.city, args.anchor, args.kind)}
    elif args.cmd == "lookup":
        result = lookup(args.cache, args.key)
    elif args.cmd == "save":
        result = save(args.cache, json.loads(args.payload.read_text()))
    elif args.cmd == "clear":
        result = clear(args.cache)
    else:
        raise SystemExit("unknown command")
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
