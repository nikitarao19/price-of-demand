"""Discover candidate music events and write a reviewable panel CSV."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import EVENT_PANEL_PATH
from price_of_demand.data.ticketmaster_client import TicketmasterClient


def event_row(event: dict) -> dict[str, str | int]:
    venue = (event.get("_embedded", {}).get("venues") or [{}])[0]
    classifications = event.get("classifications") or [{}]
    segment = classifications[0].get("segment", {}).get("name", "")
    genre = classifications[0].get("genre", {}).get("name", "")
    return {
        "event_id": event.get("id", ""),
        "event_name": event.get("name", ""),
        "genre": genre or segment,
        "venue_name": venue.get("name", ""),
        "market": venue.get("city", {}).get("name", ""),
        "venue_capacity": "",
        "tier": "",
    }


def has_positive_price(event: dict) -> bool:
    return any(
        (price.get("min") or 0) > 0 or (price.get("max") or 0) > 0
        for price in event.get("priceRanges", [])
    )


def discover(output_path: Path = EVENT_PANEL_PATH) -> Path:
    client = TicketmasterClient()
    start = datetime.now(timezone.utc).replace(microsecond=0)
    end = start + timedelta(days=365)
    events = client.search_events(
        classificationName="Music",
        sort="date,asc",
        startDateTime=start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        endDateTime=end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    candidates = [event_row(event) for event in events if has_positive_price(event)]
    by_genre = defaultdict(list)
    for row in candidates:
        by_genre[row["genre"]].append(row)
    rows = []
    genre_names = sorted(by_genre)
    while len(rows) < min(40, len(candidates)):
        added = False
        for genre in genre_names:
            if by_genre[genre]:
                rows.append(by_genre[genre].pop(0))
                added = True
                if len(rows) == 40:
                    break
        if not added:
            break
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as panel_file:
        writer = csv.DictWriter(panel_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return output_path


if __name__ == "__main__":
    print(f"Wrote candidate panel to {discover()}")
