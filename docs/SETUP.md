# Quote of the Day Setup Guide

Display a daily inspirational quote from ZenQuotes.

## Overview

The Quote of the Day plugin fetches a daily quote from the ZenQuotes API. The same quote is returned for the full day. No API key required; the free tier allows 1 request per second.

- API reference: https://zenquotes.io/

### Prerequisites

No API key required.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **Quote of the Day**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `quote_of_day` plugin variables:
   ```
   {{{ quote_of_day.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `quote_of_day.quote` | Full quote text | `Do it with passion` |
| `quote_of_day.author` | Quote author | `Rosa Parks` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `refresh_seconds` | Refresh Interval (seconds) | How often to refresh. ZenQuotes returns the same quote all day. | `3600` |

## Troubleshooting

- **Rate limited** — ZenQuotes free tier allows 1 req/s. Keep refresh at 1+ hours.
- **Same quote** — ZenQuotes returns the same quote all day; this is expected behavior.

