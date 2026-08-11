"""Helpers for event-level price trajectory analysis."""

from __future__ import annotations

import pandas as pd


def event_price_path(frame: pd.DataFrame, event_id: str) -> pd.DataFrame:
    path = frame.loc[frame["event_id"].eq(event_id)].copy()
    if path.empty:
        raise ValueError(f"No observations found for event {event_id}")
    return path.sort_values("poll_timestamp")
