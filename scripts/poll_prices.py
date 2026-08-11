"""Poll current prices for every event in the fixed panel."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from config import EVENT_PANEL_PATH, RAW_DATA_DIR
from price_of_demand.data.event_panel import load_event_panel
from price_of_demand.data.ticketmaster_client import TicketmasterClient


def extract_snapshot(event: object, payload: dict, polled_at: str) -> dict:
    event_data = payload.get("dates", {}).get("start", {})
    prices = payload.get("priceRanges", [])
    price_min = min((item.get("min") for item in prices if item.get("min") is not None), default=None)
    price_max = max((item.get("max") for item in prices if item.get("max") is not None), default=None)
    return {
        "event_id": payload.get("id", getattr(event, "event_id")),
        "event_name": payload.get("name", getattr(event, "event_name")),
        "genre": getattr(event, "genre"),
        "market": getattr(event, "market"),
        "venue_name": getattr(event, "venue_name"),
        "venue_capacity": getattr(event, "venue_capacity"),
        "tier": getattr(event, "tier"),
        "poll_timestamp": polled_at,
        "event_start": event_data.get("dateTime"),
        "price_min": price_min,
        "price_max": price_max,
        "currency": prices[0].get("currency") if prices else None,
        "raw_payload": payload,
    }


def poll(panel_path: Path = EVENT_PANEL_PATH, output_dir: Path = RAW_DATA_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    polled_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output_path = output_dir / f"snapshot_{polled_at[:10]}.jsonl"
    client = TicketmasterClient()
    with output_path.open("a", encoding="utf-8") as output_file:
        for event in load_event_panel(panel_path):
            payload = client.get_event(event.event_id)
            output_file.write(json.dumps(extract_snapshot(event, payload, polled_at)) + "\n")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=EVENT_PANEL_PATH)
    parser.add_argument("--output-dir", type=Path, default=RAW_DATA_DIR)
    args = parser.parse_args()
    print(f"Wrote {poll(args.panel, args.output_dir)}")
