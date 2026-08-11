from pathlib import Path

import pandas as pd

from price_of_demand.modeling.train_models import train_models


def _make_frame(observations_per_event: int) -> pd.DataFrame:
    rows = []
    for i in range(20):
        event_id = f"event-{i}"
        genre = "Rock" if i % 2 == 0 else "Jazz"
        base_price = 50.0 + i
        for obs in range(observations_per_event):
            rows.append(
                {
                    "event_id": event_id,
                    "genre": genre,
                    "days_until_event": 30 - obs,
                    "venue_capacity": 500,
                    "price_mid": base_price + obs * 2,
                    "price_change": None if obs == 0 else 2.0,
                }
            )
    return pd.DataFrame(rows)


def test_price_change_model_skips_when_not_enough_repeat_observations(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.csv"
    _make_frame(observations_per_event=1).to_csv(dataset_path, index=False)

    results = train_models(dataset_path, tmp_path / "models")

    assert "linear" in results["price_level"]
    assert results["price_change"] == {
        "status": "not_enough_data",
        "usable_rows": 0,
        "minimum_required": 10,
    }


def test_price_change_model_trains_once_enough_repeats_exist(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.csv"
    _make_frame(observations_per_event=2).to_csv(dataset_path, index=False)

    results = train_models(dataset_path, tmp_path / "models")

    assert "rmse" in results["price_change"]["linear"]
    assert "rmse" in results["price_change"]["gradient_boosting"]
    assert results["price_change"]["analysis_target"] == "price_change_since_previous_observation"
