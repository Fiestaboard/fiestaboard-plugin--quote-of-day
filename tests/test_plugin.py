"""Tests for the quote_of_day plugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from plugins.quote_of_day import QuoteOfDayPlugin
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "quote_of_day",
    "name": "Quote of the Day",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often to refresh. ZenQuotes returns the same quote all day.",
                "default": 3600,
                "minimum": 3600
            }
        },
        "required": []
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
[
    {
        "q": "Do what you can, with what you have, where you are.",
        "a": "Theodore Roosevelt",
        "h": "<blockquote>&ldquo;...&rdquo; &mdash; <footer>Theodore Roosevelt</footer></blockquote>"
    }
]
""")


@pytest.fixture
def plugin():
    return QuoteOfDayPlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = QuoteOfDayPlugin(MANIFEST)
    p.config = json.loads("""
{}
""")
    return p


class TestQuoteOfDayPlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "quote_of_day"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.quote_of_day.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "quote" in result.data, "missing variable: quote"
        assert "author" in result.data, "missing variable: author"

    @patch("plugins.quote_of_day.requests.get")
    def test_fetch_data_network_error(self, mock_get, configured_plugin):
        import requests as req_mod
        mock_get.side_effect = req_mod.exceptions.ConnectionError("network down")

        result = configured_plugin.fetch_data()

        assert result.available is False
        assert result.error is not None

    @patch("plugins.quote_of_day.requests.get")
    def test_fetch_data_bad_json(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("bad json")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is False

