"""Project paths and collection constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"
EVENT_PANEL_PATH = PROJECT_ROOT / "data" / "event_panel.csv"

TICKETMASTER_BASE_URL = "https://app.ticketmaster.com/discovery/v2"
REQUEST_TIMEOUT_SECONDS = 30
POLL_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
