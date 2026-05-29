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

    @patch("plugins.quote_of_day.time.sleep")
    @patch("plugins.quote_of_day.requests.get")
    def test_retries_on_connection_error(self, mock_get, mock_sleep, configured_plugin):
        """Connection errors are retried before giving up (fixes issue #807)."""
        import requests as req_mod
        mock_get.side_effect = req_mod.exceptions.ConnectionError("Connection reset by peer")

        result = configured_plugin.fetch_data()

        from plugins.quote_of_day import _MAX_RETRIES
        assert mock_get.call_count == _MAX_RETRIES + 1, "Should retry _MAX_RETRIES times"
        assert result.available is False

    @patch("plugins.quote_of_day.time.sleep")
    @patch("plugins.quote_of_day.requests.get")
    def test_succeeds_on_second_attempt(self, mock_get, mock_sleep, configured_plugin):
        """A transient error is recovered on retry."""
        import requests as req_mod
        good_response = Mock()
        good_response.json.return_value = SAMPLE_RESPONSE
        good_response.raise_for_status = Mock()
        mock_get.side_effect = [
            req_mod.exceptions.ConnectionError("transient"),
            good_response,
        ]

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.data["quote"] == "Do what you can, with what"[:22]

    @patch("plugins.quote_of_day.requests.get")
    def test_request_includes_user_agent(self, mock_get, configured_plugin):
        """Requests must include a browser-compatible User-Agent."""
        good_response = Mock()
        good_response.json.return_value = SAMPLE_RESPONSE
        good_response.raise_for_status = Mock()
        mock_get.return_value = good_response

        configured_plugin.fetch_data()

        _, kwargs = mock_get.call_args
        headers = kwargs.get("headers", {})
        assert "User-Agent" in headers
        assert "FiestaBoard" in headers["User-Agent"]

