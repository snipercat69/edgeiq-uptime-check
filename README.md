# uptime.check ⏱️

**URL uptime monitoring with email and webhook alerts.**

- Free: 3 monitors, daily checks, email alerts
- Pro ($5/mo): 20 monitors, 5-minute checks, webhook alerts, 90-day history

---

## Quick Start

```bash
# Add your first monitor
python3 uptime_check.py --add https://example.com --name "Example" --alert-email you@example.com

# List all monitors
python3 uptime_check.py --list

# Check all now
python3 uptime_check.py --check-all

# Check one now
python3 uptime_check.py --check "Example"

# Remove a monitor
python3 uptime_check.py --remove "Example"
```

---

## Install

```bash
pip install colorama
```

Or grab the two files:
- `uptime_check.py`
- `edgeiq_licensing.py`

---

## Cron Setup (Automated Daily Checks)

```bash
# Run every day at 9am
0 9 * * * /usr/bin/python3 ~/uptime_check.py --check-all >> ~/.uptime_check/cron.log 2>&1
```

Edit your crontab with `crontab -e`.

---

## Pro Features ($5/mo)

Pro mode unlocks:
- **20 monitors** (vs 3 for free)
- **5-minute check loop** — run continuously with `--monitor`
- **Webhook alerts** — POST JSON to your endpoint when sites go down
- **90-day history** — stored in `~/.uptime_check/history/`

```bash
python3 uptime_check.py --pro --check-all
python3 uptime_check.py --pro --monitor  # runs continuously
```

**Upgrade:** https://buy.stripe.com/fZu00l8dZbxrbQo0487wA0v

---

## Status Icons

| Icon | Status |
|------|--------|
| 🟢 UP | Site responding (2xx) |
| 🔴 DOWN | Site down (4xx/5xx/error/timeout) |
| 🟡 SLOW | Responding but >5 seconds |
| ⚪ UNKNOWN | Never checked yet |

---

## All Commands

```
--add URL --name "Name" [--alert-email EMAIL] [--alert-webhook URL]
  Add a URL monitor. Each name must be unique.

--remove NAME
  Remove a monitor.

--list
  Show all monitors with status, uptime %, and last check time.

--check NAME
  Check one monitor immediately.

--check-all
  Check all monitors immediately.

--set-alert-email EMAIL
  Set default alert email for all monitors.

--set-alert-webhook URL
  Set default webhook URL (pro only).

--pro --check-all
  Run in Pro mode with enhanced output.

--pro --monitor
  Continuous monitoring loop (5-min intervals, pro only).
```

---

## Data Location

- Monitors: `~/.uptime_check/monitors.json`
- History (pro): `~/.uptime_check/history/*.jsonl`
- Logs: `~/.uptime_check/cron.log`

---

## Install via ClawHub

```bash
clawhub install snipercat69/uptime-check
```