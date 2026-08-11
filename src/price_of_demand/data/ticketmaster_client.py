"""Small, testable wrapper around the Ticketmaster Discovery API."""

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

from config import REQUEST_TIMEOUT_SECONDS, TICKETMASTER_BASE_URL


class TicketmasterAPIError(RuntimeError):
    """Raised when Ticketmaster returns an unsuccessful response."""


class TicketmasterClient:
    def __init__(self, api_key: str | None = None, session: requests.Session | None = None) -> None:
        load_dotenv()
        self.api_key = api_key or os.getenv("TICKETMASTER_API_KEY")
        if not self.api_key:
            raise ValueError("TICKETMASTER_API_KEY is required in .env or the environment")
        self.session = session or requests.Session()

    def get_event(self, event_id: str) -> dict[str, Any]:
        response = self.session.get(
            f"{TICKETMASTER_BASE_URL}/events/{event_id}.json",
            params={"apikey": self.api_key},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if not response.ok:
            raise TicketmasterAPIError(f"Ticketmaster returned HTTP {response.status_code}: {response.text[:200]}")
        return response.json()

    def search_events(self, **filters: str | int) -> list[dict[str, Any]]:
        """Return upcoming events matching Discovery API filters."""
        params: dict[str, str | int] = {"apikey": self.api_key, "size": 200, **filters}
        response = self.session.get(
            f"{TICKETMASTER_BASE_URL}/events.json",
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if not response.ok:
            raise TicketmasterAPIError(f"Ticketmaster returned HTTP {response.status_code}: {response.text[:200]}")
        return response.json().get("_embedded", {}).get("events", [])
