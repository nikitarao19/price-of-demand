"""Combine raw JSONL snapshots into one analysis-ready CSV."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def build_dataset(raw_dir: Path, output_path: Path) -> pd.DataFrame:
    records = []
    for path in sorted(raw_dir.glob("snapshot_*.jsonl")):
        with path.open(encoding="utf-8") as snapshot_file:
            records.extend(json.loads(line) for line in snapshot_file if line.strip())
    if not records:
        raise ValueError(f"No raw snapshots found in {raw_dir}")
    frame = pd.DataFrame(records).drop(columns=["raw_payload"], errors="ignore")
    frame["poll_timestamp"] = pd.to_datetime(frame["poll_timestamp"], utc=True)
    frame["event_start"] = pd.to_datetime(frame["event_start"], utc=True, errors="coerce")
    frame["days_until_event"] = (frame["event_start"] - frame["poll_timestamp"]).dt.total_seconds() / 86400
    frame = frame.sort_values(["event_id", "poll_timestamp"])
    frame["price_mid"] = frame[["price_min", "price_max"]].mean(axis=1)
    frame["price_status"] = "not_listed"
    frame.loc[frame["price_mid"].eq(0), "price_status"] = "free_or_no_charge"
    frame.loc[frame["price_mid"].gt(0), "price_status"] = "listed"
    frame["price_change"] = frame.groupby("event_id")["price_mid"].diff()
    frame["price_change_pct"] = frame.groupby("event_id")["price_mid"].pct_change(fill_method=None)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame
