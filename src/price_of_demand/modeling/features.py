"""Feature engineering shared by training and dashboard code."""

from __future__ import annotations

import pandas as pd


NUMERIC_FEATURES = ["days_until_event", "initial_price", "venue_capacity"]


def make_price_level_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Create non-leaky features for the current listed-price cross-section."""
    data = frame.copy()
    data["venue_capacity"] = pd.to_numeric(data.get("venue_capacity", pd.Series(index=data.index)), errors="coerce")
    capacity_values = data["venue_capacity"].dropna()
    capacity_median = capacity_values.median() if not capacity_values.empty else 0
    data["venue_capacity"] = data["venue_capacity"].fillna(0 if pd.isna(capacity_median) else capacity_median)
    data["days_until_event"] = pd.to_numeric(data["days_until_event"], errors="coerce")
    data["genre"] = data.get("genre", pd.Series("unknown", index=data.index)).fillna("unknown")
    data = pd.get_dummies(data, columns=["genre"], dtype=float)
    feature_columns = ["days_until_event", "venue_capacity"] + sorted(
        column for column in data if column.startswith("genre_")
    )
    usable = data.dropna(subset=feature_columns + ["price_mid"])
    return usable[feature_columns], usable["price_mid"]


def make_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    data = frame.copy()
    data["initial_price"] = data.groupby("event_id")["price_mid"].transform("first")
    data["venue_capacity"] = pd.to_numeric(data.get("venue_capacity", pd.Series(index=data.index)), errors="coerce")
    capacity_values = data["venue_capacity"].dropna()
    capacity_median = capacity_values.median() if not capacity_values.empty else 0
    data["venue_capacity"] = data["venue_capacity"].fillna(0 if pd.isna(capacity_median) else capacity_median)
    data["genre"] = data.get("genre", pd.Series("unknown", index=data.index)).fillna("unknown")
    data = pd.get_dummies(data, columns=["genre"], dtype=float)
    feature_columns = NUMERIC_FEATURES + sorted(column for column in data if column.startswith("genre_"))
    usable = data.dropna(subset=feature_columns + ["price_change"])
    return usable[feature_columns], usable["price_change"]
