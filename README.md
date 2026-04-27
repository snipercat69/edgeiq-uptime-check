# ⏱️ EdgeIQ Uptime Check

**URL uptime monitoring with email and webhook alerts.**

Monitor your critical URLs and get instant alerts when they go down. Free tier supports 3 monitors with daily checks; Pro tier adds 5-minute intervals and webhook alerts.

[![Project Stage](https://img.shields.io/badge/Stage-Beta-blue)](https://edgeiqlabs.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

---

## What It Does

Checks URL availability at configurable intervals, records response times and status codes, and sends alerts via email or webhook when a monitor goes down or recovers.

---

## Key Features

- **HTTP/HTTPS monitoring** — GET checks with status code validation
- **Response time tracking** — measure latency over time
- **Email alerts** — notify when a monitor fails
- **Webhook alerts** — integrate with Slack, PagerDuty, custom endpoints
- **History tracking** — 90-day history of checks (Pro)
- **Batch monitor management** — add/remove/list monitors via CLI

---

## Prerequisites

- Python 3.8+
- `colorama` for colored terminal output

---

## Installation

```bash
git clone https://github.com/snipercat69/edgeiq-uptime-check.git
cd edgeiq-uptime-check
pip install -r requirements.txt
```

---

## Quick Start

```bash
# Add your first monitor
python3 uptime_check.py --add https://example.com --name "Example Site" --alert-email you@example.com

# List all monitors
python3 uptime_check.py --list

# Check a specific monitor now
python3 uptime_check.py --check my-site

# Check all monitors now
python3 uptime_check.py --check-all

# Remove a monitor
python3 uptime_check.py --remove "Example Site"
```

---

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 3 monitors, daily checks, email alerts |
| **Pro** | $5/mo | 20 monitors, 5-minute checks, email + webhook alerts, 90-day history |

---

## Integration with EdgeIQ Tools

- **[EdgeIQ Alerting System](https://github.com/snipercat69/edgeiq-alerting-system)** — use EdgeIQ alerting infrastructure
- **[EdgeIQ SSL Watcher](https://github.com/snipercat69/edgeiq-ssl-watcher)** — combine with SSL monitoring

---

## Support

Open an issue at: https://github.com/snipercat69/edgeiq-uptime-check/issues

---

*Part of EdgeIQ Labs — [edgeiqlabs.com](https://edgeiqlabs.com)*
