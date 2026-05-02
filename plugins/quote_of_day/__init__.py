"""Display a daily inspirational quote from ZenQuotes."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

API_URL = "https://zenquotes.io/api/today"
USER_AGENT = "FiestaBoard Quote of the Day Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--quote-of-day)"


class QuoteOfDayPlugin(PluginBase):
    """Quote of the Day plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "quote_of_day"

    def fetch_data(self) -> PluginResult:
        try:
            response = requests.get(
                API_URL,
                headers={"User-Agent": USER_AGENT},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, list):
                return PluginResult(available=False, error="Unexpected response format")

            quote_obj = data[0]
            quote = str(quote_obj.get("q", ""))[:22]
            author = str(quote_obj.get("a", "Unknown"))[:20]

            return PluginResult(
                available=True,
                data={
                    "quote": quote,
                    "author": author,
                },
            )
        except Exception as e:
            logger.exception("Error fetching quote of the day")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        return []

    def cleanup(self) -> None:
        pass
