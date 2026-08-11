"""Load and validate the fixed event panel."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrackedEvent:
    event_id: str
    event_name: str
    genre: str
    venue_name: str
    market: str
    venue_capacity: int | None
    tier: str


def load_event_panel(path: Path) -> list[TrackedEvent]:
    with path.open(newline="", encoding="utf-8") as panel_file:
        rows = csv.DictReader(row for row in panel_file if not row.startswith("#"))
        events = []
        for row in rows:
            if not row.get("event_id"):
                continue
            capacity = row.get("venue_capacity", "").strip()
            events.append(
                TrackedEvent(
                    event_id=row["event_id"],
                    event_name=row.get("event_name", ""),
                    genre=row.get("genre", ""),
                    venue_name=row.get("venue_name", ""),
                    market=row.get("market", ""),
                    venue_capacity=int(capacity) if capacity else None,
                    tier=row.get("tier", ""),
                )
            )
    if not events:
        raise ValueError(f"No tracked events found in {path}; add event IDs before polling")
    return events
