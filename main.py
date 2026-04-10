"""
HoYoLAB Auto Daily Check-In
Supports: Genshin Impact, Honkai: Star Rail, Zenless Zone Zero
"""

import os
import requests
import time
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
#  CONFIGURATION — edit these values
# ─────────────────────────────────────────────

ACCOUNT_ID    = os.environ.get("ACCOUNT_ID")
ACCOUNT_MID   = os.environ.get("ACCOUNT_MID")
ACCOUNT_TOKEN = os.environ.get("ACCOUNT_TOKEN")

COOKIE = "; ".join([
    f"ltuid_v2={ACCOUNT_ID}",
    f"ltoken_v2={ACCOUNT_TOKEN}",
    f"ltmid_v2={ACCOUNT_MID}",
    f"account_id_v2={ACCOUNT_ID}",
    f"account_mid_v2={ACCOUNT_MID}",
])

# Toggle which games to check in for
GAMES = {
    "genshin":  True,   # Genshin Impact
    "starrail": True,   # Honkai: Star Rail
    "zzz":      True,   # Zenless Zone Zero
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# avoids rate limiting
DELAY_BETWEEN = 5

# ─────────────────────────────────────────────
#  EMAIL CONFIGURATION
# ─────────────────────────────────────────────

EMAIL_SENDER       = os.environ.get("EMAIL")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT    = EMAIL_SENDER

# ─────────────────────────────────────────────
#  GAME CONFIGS
# ─────────────────────────────────────────────

GAME_GI_AID  = "e202102251931481"   # Genshin Impact — global constant
GAME_HSR_AID = "e202303301540311"   # Honkai: Star Rail — global constant
GAME_ZZZ_AID = "e202406031448091"   # Zenless Zone Zero — global constant

GAME_CONFIGS = {
    "genshin": {
        "name": "Genshin Impact",
        "url": "https://sg-hk4e-api.hoyolab.com/event/sol/sign",
        "params": {"lang": "en-us"},
        "body": {"act_id": GAME_GI_AID},
        "referer": f"https://act.hoyolab.com/ys/event/signin-sea-v3/index.html?act_id={GAME_GI_AID}",
    },
    "starrail": {
        "name": "Honkai: Star Rail",
        "url": "https://sg-public-api.hoyolab.com/event/luna/os/sign",
        "params": {"lang": "en-us"},
        "body": {"act_id": GAME_HSR_AID},
        "referer": f"https://act.hoyolab.com/bbs/event/signin/hkrpg/index.html?act_id={GAME_HSR_AID}",
    },
    "zzz": {
        "name": "Zenless Zone Zero",
        "url": "https://sg-public-api.hoyolab.com/event/luna/zzz/os/sign",
        "params": {"lang": "en-us", "act_id": GAME_ZZZ_AID},
        "body": {"act_id": GAME_ZZZ_AID},
        "referer": f"https://act.hoyolab.com/bbs/event/signin/zzz/{GAME_ZZZ_AID}.html?act_id={GAME_ZZZ_AID}",
    },
}

# ─────────────────────────────────────────────
#  EMAIL HELPER
# ─────────────────────────────────────────────

def send_failure_email(failures: list) -> None:
    if not EMAIL_SENDER or not EMAIL_APP_PASSWORD:   # skip if secrets not set
        return
    lines = [f"  • {f['game']}: {f['reason']}" for f in failures]
    body = (
        "The following HoYoLAB check-ins failed today:\n\n"
        + "\n".join(lines)
        + "\n\nPlease check your script or update your cookie."
    )
    msg = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECIPIENT
    msg["Subject"] = f"⚠️ HoYoLAB Check-In Failed ({len(failures)} game{'s' if len(failures) > 1 else ''})"
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print(f"  📧  Failure email sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"  ❌  Could not send email: {e}")

# ─────────────────────────────────────────────
#  CHECK-IN LOGIC
# ─────────────────────────────────────────────

def check_in(game_key: str):
    """Returns a failure dict if something went wrong, otherwise None."""
    config = GAME_CONFIGS[game_key]
    name   = config["name"]

    headers = {
        "Cookie":            COOKIE,
        "User-Agent":        USER_AGENT,
        "Referer":           config["referer"],
        "Accept":            "application/json, text/plain, */*",
        "Content-Type":      "application/json;charset=utf-8",
        "Origin":            "https://act.hoyolab.com",
        "x-rpc-client_type": "5" if game_key == "zzz" else "4",
        "x-rpc-platform":    "4",
        "x-rpc-language":    "en-us",
    }
    
    if game_key == "zzz":
        headers["x-rpc-signgame"] = "zzz"
        
    try:
        response = requests.post(
            config["url"],
            params=config["params"],
            json=config["body"],
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        retcode = data.get("retcode", -1)
        message = data.get("message", "Unknown response")

        if retcode == 0:
            print(f"  ✅  {name}: Check-in successful! ({message})")
            return None
        elif retcode == -5003:
            print(f"  ℹ️   {name}: Already checked in today.")
            return None
        elif retcode == -100:
            reason = "Cookie expired or invalid — please refresh your cookie."
            print(f"  ❌  {name}: {reason}")
            return {"game": name, "reason": reason}
        else:
            reason = f"Unexpected response — retcode={retcode}, message='{message}'"
            print(f"  ⚠️   {name}: {reason}")
            return {"game": name, "reason": reason}

    except requests.exceptions.Timeout:
        reason = "Request timed out."
        print(f"  ❌  {name}: {reason}")
        return {"game": name, "reason": reason}
    except requests.exceptions.ConnectionError:
        reason = "Connection error — check internet connection."
        print(f"  ❌  {name}: {reason}")
        return {"game": name, "reason": reason}
    except requests.exceptions.HTTPError as e:
        reason = f"HTTP error — {e}"
        print(f"  ❌  {name}: {reason}")
        return {"game": name, "reason": reason}
    except Exception as e:
        reason = f"Unexpected error — {e}"
        print(f"  ❌  {name}: {reason}")
        return {"game": name, "reason": reason}


def run_checkins() -> None:
    if not account_id or not account_mid or not account_token:
        print("=" * 55)
        print("  ⚠️  Missing account secrets!")
        print("  Ensure ACCOUNT_ID, ACCOUNT_MID, ACCOUNT_TOKEN")
        print("  are set in your GitHub environment secrets.")
        print("=" * 55)
        sys.exit(1)

    enabled = [k for k, v in GAMES.items() if v]
    if not enabled:
        print("No games enabled. Set at least one game to True in GAMES config.")
        sys.exit(1)

    print("=" * 55)
    print("  HoYoLAB Daily Check-In")
    print("=" * 55)

    failures = []
    for i, game_key in enumerate(enabled):
        result = check_in(game_key)
        if result:
            failures.append(result)
        if i < len(enabled) - 1:
            time.sleep(DELAY_BETWEEN)

    print("=" * 55)
    print("  Done!")

    if failures:
        print()
        send_failure_email(failures)


if __name__ == "__main__":
    run_checkins()
