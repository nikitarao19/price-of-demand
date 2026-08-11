import pandas as pd

from price_of_demand.analysis.elasticity import estimate_timing_elasticity


def test_timing_proxy_has_expected_direction() -> None:
    result = estimate_timing_elasticity(
        pd.DataFrame({"price_mid": [100, 90, 80, 70], "days_until_event": [1, 2, 3, 4]})
    )
    assert result["coefficient_price_per_day"] < 0
    assert result["price_elasticity_proxy"] < 0
