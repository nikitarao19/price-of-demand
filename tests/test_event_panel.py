from pathlib import Path

import pytest

from price_of_demand.data.event_panel import load_event_panel


def test_empty_panel_is_rejected(tmp_path: Path) -> None:
    panel = tmp_path / "panel.csv"
    panel.write_text("event_id,event_name,genre,venue_name,market,venue_capacity,tier\n", encoding="utf-8")
    with pytest.raises(ValueError, match="No tracked events"):
        load_event_panel(panel)
