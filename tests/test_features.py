import pandas as pd

from price_of_demand.modeling.features import make_features


def test_features_include_initial_price_and_target() -> None:
    frame = pd.DataFrame(
        {
            "event_id": ["a", "a", "b"],
            "price_mid": [10.0, 12.0, 20.0],
            "days_until_event": [10, 9, 8],
            "genre": ["Rock", "Rock", "Jazz"],
            "venue_capacity": [100, 100, 200],
            "price_change": [None, 2.0, None],
        }
    )
    features, target = make_features(frame)
    assert "initial_price" in features
    assert len(target) == 1
