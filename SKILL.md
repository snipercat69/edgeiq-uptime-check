# SKILL.md — uptime.check

> URL uptime monitoring with email and webhook alerts.
> Free: 3 monitors, daily checks. Pro ($5/mo): 20 monitors, 5-minute checks, email+webhook alerts, 90-day history.

## Install

```bash
pip install colorama
curl -fsSL https://clawhub.ai/snipercat69/uptime-check/install.sh | sh
```

Or copy `uptime_check.py` and `edgeiq_licensing.py` to your PATH.

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

## Commands

### `--add URL --name "Name" [--alert-email EMAIL] [--alert-webhook URL]`
Add a URL to monitor. Each monitor needs a unique name.

```
python3 uptime_check.py --add https://example.com --name "Example" --alert-email admin@example.com
python3 uptime_check.py --add https://mysite.com --name "My Site" --alert-email me@here.com --alert-webhook https://hooks.example.com/uptime
```

Free tier: up to 3 monitors, email alerts only.
Pro ($5/mo): up to 20 monitors, email + webhook alerts.

### `--remove NAME`
Remove a monitor by name.

```bash
python3 uptime_check.py --remove "Example Site"
```

### `--list`
List all monitors with current status.

```bash
python3 uptime_check.py --list
```

Output:
```
🟢 UP    Example Site     https://example.com       (99.9% uptime, 2h ago)
🔴 DOWN  Test Site        https://test.com          (0 events)
⚪ UNKNOWN My Site         https://othersite.com     (never checked)
```

### `--check NAME`
Run a check on one monitor immediately.

```bash
python3 uptime_check.py --check Example
```

### `--check-all`
Run checks on all monitors immediately.

```bash
python3 uptime_check.py --check-all
```

### `--alert-email EMAIL`
Set a global alert email for all monitors (used for new monitors by default).

```bash
python3 uptime_check.py --alert-email admin@example.com
```

### `--alert-webhook URL`
Set a global webhook URL for all monitors (pro only).

```bash
python3 uptime_check.py --alert-webhook https://hooks.example.com/uptime
```

## Pro Features

Pro users get:
- **20 monitors** (vs 3 for free)
- **5-minute check simulation** — runs a continuous loop checking every 5 minutes
- **Webhook alerts** — POST alerts to your endpoint when a site goes down
- **90-day history** — track uptime over 90 days

Run in pro mode:
```bash
python3 uptime_check.py --pro --check-all
```

To unlock Pro, visit: **https://buy.stripe.com/fZu00l8dZbxrbQo0487wA0v**

## Cron Setup (Automated Daily Checks)

Add to your crontab (`crontab -e`):

```bash
# Check all monitors every day at 9am
0 9 * * * /usr/bin/python3 /home/user/uptime_check.py --check-all >> ~/.uptime_check/cron.log 2>&1
```

Or simulate 5-min monitoring in pro mode (runs continuously until killed):

```bash
python3 uptime_check.py --pro --monitor
```

## Output Icons

| Icon | Meaning |
|------|---------|
| 🟢 UP | Site is up (2xx response) |
| 🔴 DOWN | Site is down (4xx/5xx or error) |
| 🟡 SLOW | Site responded but slowly (>5s) |
| ⚪ UNKNOWN | Haven't checked yet |

## State File

All data stored in: `~/.uptime_check/monitors.json`

Pro users also get `~/.uptime_check/history/` with 90-day check logs.

## Upgrade to Pro

**https://buy.stripe.com/fZu00l8dZbxrbQo0487wA0v**

---

## 🔗 More from EdgeIQ Labs

**edgeiqlabs.com** — Security tools, OSINT utilities, and micro-SaaS products for developers and security professionals.

- 🛠️ **Subdomain Hunter** — Passive subdomain enumeration via Certificate Transparency
- 📸 **Screenshot API** — URL-to-screenshot API for developers
- 🔔 **uptime.check** — URL uptime monitoring with alerts
- 🛡️ **headers.check** — HTTP security headers analyzer

👉 [Visit edgeiqlabs.com →](https://edgeiqlabs.com)
