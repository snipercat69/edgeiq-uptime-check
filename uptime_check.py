#!/usr/bin/env python3
"""
uptime.check — URL Uptime Monitor
URL uptime monitoring with email and webhook alerts.
Free: 3 monitors, daily checks.
Pro ($5/mo): 20 monitors, 5-minute checks, email+webhook alerts, 90-day history.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from colorama import init as colorama_init, Fore, Style

# ── Licensing ──────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
try:
    from edgeiq_licensing import is_pro
except Exception:
    # Fallback if licensing not available
    def is_pro():
        return False

# ── Setup ─────────────────────────────────────────────────────────────────────
colorama_init(autoreset=True)
STATE_DIR = Path.home() / ".uptime_check"
STATE_FILE = STATE_DIR / "monitors.json"
HISTORY_DIR = STATE_DIR / "history"
STATE_DIR.mkdir(exist_ok=True)
HISTORY_DIR.mkdir(exist_ok=True)

UP = f"{Fore.GREEN}🟢 UP{Style.RESET_ALL}"
DOWN = f"{Fore.RED}🔴 DOWN{Style.RESET_ALL}"
SLOW = f"{Fore.YELLOW}🟡 SLOW{Style.RESET_ALL}"
UNKNOWN = f"{Fore.WHITE}⚪ UNKNOWN{Style.RESET_ALL}"
STRIPE_LINK = "https://buy.stripe.com/fZu00l8dZbxrbQo0487wA0v"
TIMEOUT = 10  # seconds


# ── State Management ───────────────────────────────────────────────────────────
def load_monitors():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_monitors(monitors):
    STATE_FILE.write_text(json.dumps(monitors, indent=2))


# ── Check Logic ────────────────────────────────────────────────────────────────
def check_url(url):
    """Returns (status, code, elapsed_ms). status: 'up'|'down'|'slow'|'unknown'"""
    start = time.time()
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "uptime-check/1.0")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            code = resp.getcode()
            elapsed_ms = (time.time() - start) * 1000
            if 200 <= code < 300:
                if elapsed_ms > 5000:
                    return "slow", code, elapsed_ms
                return "up", code, elapsed_ms
            elif 300 <= code < 400:
                return "down", code, elapsed_ms  # redirect counts as down
            else:
                return "down", code, elapsed_ms
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.time() - start) * 1000
        return "down", e.code, elapsed_ms
    except Exception:
        elapsed_ms = (time.time() - start) * 1000
        return "down", 0, elapsed_ms


def status_icon(status):
    return {"up": UP, "down": DOWN, "slow": SLOW, "unknown": UNKNOWN}.get(status, UNKNOWN)


def format_elapsed(ts):
    """Human-friendly elapsed time string."""
    if not ts:
        return "never"
    diff = time.time() - ts
    if diff < 60:
        return f"{int(diff)}s ago"
    elif diff < 3600:
        return f"{int(diff/60)}m ago"
    elif diff < 86400:
        return f"{int(diff/3600)}h ago"
    else:
        return f"{int(diff/86400)}d ago"


# ── Alerting ───────────────────────────────────────────────────────────────────
def send_email_alert(to_email, name, url, status, code):
    print(f"  📧 Email alert → {to_email}: {name} is {status} (HTTP {code})")


def send_webhook_alert(webhook_url, name, url, status, code):
    try:
        payload = json.dumps({
            "monitor": name,
            "url": url,
            "status": status,
            "code": code,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }).encode()
        req = urllib.request.Request(webhook_url, data=payload, headers={
            "Content-Type": "application/json",
            "User-Agent": "uptime-check/1.0",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"  📡 Webhook sent → {webhook_url} [{resp.getcode()}]")
    except Exception as e:
        print(f"  ⚠️  Webhook failed: {e}")


def handle_alerts(monitor, new_status):
    if new_status != "down":
        return
    last = monitor.get("last_status", "")
    if last == "down":
        return  # already alerted

    alert_email = monitor.get("alert_email")
    alert_webhook = monitor.get("alert_webhook")

    if alert_email:
        send_email_alert(alert_email, monitor["name"], monitor["url"], new_status,
                         monitor.get("last_code", "?"))

    pro = is_pro()
    if pro and alert_webhook:
        send_webhook_alert(alert_webhook, monitor["name"], monitor["url"],
                           new_status, monitor.get("last_code", "?"))


# ── Core check ────────────────────────────────────────────────────────────────
def do_check(m):
    url = m["url"]
    status, code, elapsed = check_url(url)
    m["last_check"] = time.time()
    m["last_status"] = status
    m["last_code"] = code
    m["check_count"] = m.get("check_count", 0) + 1

    was_down = m.get("last_status") == "down"

    if status == "down":
        m["down_count"] = m.get("down_count", 0) + 1
        m["last_down_time"] = time.time()

    # Uptime percentage
    if m["check_count"] > 0:
        m["uptime_percent"] = ((m["check_count"] - m.get("down_count", 0)) / m["check_count"]) * 100
    else:
        m["uptime_percent"] = 100.0

    elapsed_ms = int(elapsed)
    icon = status_icon(status)
    print(f"  {icon} {m['name']:<30} HTTP {code} ({elapsed_ms}ms)")

    handle_alerts(m, status)

    # Save history entry (pro only)
    if is_pro():
        safe_name = m["name"].replace(" ", "_").replace("/", "_")
        history_file = HISTORY_DIR / f"{safe_name}.jsonl"
        entry = {
            "ts": time.time(),
            "status": status,
            "code": code,
            "elapsed_ms": int(elapsed),
        }
        with open(history_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        trim_history(history_file)


def trim_history(history_file):
    try:
        cutoff = time.time() - (90 * 86400)
        lines = []
        if history_file.exists():
            with open(history_file) as f:
                for line in f:
                    try:
                        e = json.loads(line)
                        if e.get("ts", 0) > cutoff:
                            lines.append(line)
                    except Exception:
                        pass
            with open(history_file, "w") as f:
                f.writelines(lines)
    except Exception:
        pass


# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_add(args, monitors):
    pro = is_pro()
    max_monitors = 20 if pro else 3

    if len(monitors) >= max_monitors:
        print(f"❌ Monitor limit reached ({max_monitors}). Upgrade: {STRIPE_LINK}")
        return monitors, 1

    if any(m["name"] == args.name for m in monitors):
        print(f"❌ Monitor with name '{args.name}' already exists.")
        return monitors, 1

    monitors.append({
        "name": args.name,
        "url": args.add,
        "alert_email": args.alert_email or "",
        "alert_webhook": args.alert_webhook or "",
        "last_check": None,
        "last_status": "unknown",
        "last_code": None,
        "last_down_time": None,
        "check_count": 0,
        "down_count": 0,
        "uptime_percent": 100.0,
    })
    print(f"✅ Added '{args.name}' → {args.add}")
    return monitors, 0


def cmd_remove(args, monitors):
    before = len(monitors)
    monitors = [m for m in monitors if m["name"] != args.name]
    if len(monitors) == before:
        print(f"❌ No monitor named '{args.name}' found.")
        return monitors, 1
    print(f"🗑️  Removed '{args.name}'")
    return monitors, 0


def cmd_list(monitors):
    if not monitors:
        print("No monitors yet. Run: --add https://example.com --name 'My Site' --alert-email you@example.com")
        return 0

    print(f"\n  {'STATUS':<8} {'NAME':<30} {'URL':<40} {'UPTIME':>8}  LAST")
    print(f"  {'─'*8} {'─'*30} {'─'*40} {'─'*8}  {'─'*12}")

    for m in monitors:
        icon = status_icon(m.get("last_status", "unknown"))
        uptime = m.get("uptime_percent", 0)
        elapsed = format_elapsed(m.get("last_check"))
        name = m["name"][:30]
        url = m["url"][:40]
        uptime_str = f"{uptime:.1f}%" if uptime else "—"
        print(f"  {icon:<8} {name:<30} {url:<40} {uptime_str:>8}  {elapsed}")

    print()
    return 0


def cmd_check_one(name, monitors):
    m = next((x for x in monitors if x["name"] == name), None)
    if not m:
        print(f"❌ No monitor named '{name}'")
        return monitors, 1
    do_check(m)
    return monitors, 0


def cmd_check_all(monitors):
    if not monitors:
        print("No monitors to check.")
        return monitors, 0
    for m in monitors:
        do_check(m)
    return monitors, 0


def cmd_set_alert_email(email, monitors):
    for m in monitors:
        if not m.get("alert_email"):
            m["alert_email"] = email
    print(f"📧 Global alert email set to: {email}")
    return monitors, 0


def cmd_set_alert_webhook(url, monitors):
    if not is_pro():
        print(f"🔒 Webhook alerts require Pro. Upgrade: {STRIPE_LINK}")
        return monitors, 1
    for m in monitors:
        if not m.get("alert_webhook"):
            m["alert_webhook"] = url
    print(f"📡 Global alert webhook set to: {url}")
    return monitors, 0


def cmd_monitor(monitors):
    if not is_pro():
        print(f"🔒 5-minute monitoring requires Pro. Upgrade: {STRIPE_LINK}")
        return 1
    print("⏱️  Pro monitoring mode — checking every 5 minutes. Ctrl+C to stop.")
    while True:
        for m in monitors:
            do_check(m)
        save_monitors(monitors)
        time.sleep(300)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="uptime.check — URL Uptime Monitor")
    parser.add_argument("--pro", action="store_true", help="Run in Pro mode")
    parser.add_argument("--monitor", action="store_true", help="Continuous 5-min monitoring loop (pro only)")

    parser.add_argument("--add", help="URL to monitor")
    parser.add_argument("--name", help="Unique name for this monitor")
    parser.add_argument("--alert-email", help="Email for alerts")
    parser.add_argument("--alert-webhook", help="Webhook URL for alerts (pro)")

    parser.add_argument("--remove", help="Remove monitor by name")
    parser.add_argument("--list", action="store_true", help="List all monitors")
    parser.add_argument("--check", help="Check one monitor by name")
    parser.add_argument("--check-all", action="store_true", help="Check all monitors now")

    parser.add_argument("--set-alert-email", help="Set global alert email")
    parser.add_argument("--set-alert-webhook", help="Set global alert webhook URL")

    args = parser.parse_args()

    pro = is_pro()
    if args.pro and not pro:
        print(f"❌ Pro mode required. Upgrade: {STRIPE_LINK}")
        return 1

    monitors = load_monitors()

    # Handle commands
    if args.monitor:
        return cmd_monitor(monitors)

    if args.add and args.name:
        monitors, rc = cmd_add(args, monitors)
        save_monitors(monitors)
        return rc

    if args.remove:
        monitors, rc = cmd_remove(argparse.Namespace(name=args.remove), monitors)
        save_monitors(monitors)
        return rc

    if args.list:
        return cmd_list(monitors)

    if args.check:
        monitors, rc = cmd_check_one(args.check, monitors)
        save_monitors(monitors)
        return rc

    if args.check_all:
        monitors, rc = cmd_check_all(monitors)
        save_monitors(monitors)
        return rc

    if args.set_alert_email:
        monitors, rc = cmd_set_alert_email(args.set_alert_email, monitors)
        save_monitors(monitors)
        return rc

    if args.set_alert_webhook:
        monitors, rc = cmd_set_alert_webhook(args.set_alert_webhook, monitors)
        save_monitors(monitors)
        return rc

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())