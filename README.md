# HoYoLAB Auto Daily Check-In

Automatically checks in to HoYoLAB daily for Genshin Impact, Honkai: Star Rail, and Zenless Zone Zero using GitHub Actions.

---

## Features

- Daily automated check-in via GitHub Actions cron schedule
- Supports Genshin Impact, Honkai: Star Rail, and Zenless Zone Zero
- Email notification on check-in failure
- Secrets managed securely via GitHub Environment secrets

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hoyolab-checkin.git
cd hoyolab-checkin
```

### 2. Configure GitHub Environment Secrets

Go to **Settings → Environments → production** and add the following:

#### Secrets
| Secret | Description |
|---|---|
| `ACCOUNT_ID` | HoYoLAB account ID (`ltuid_v2` / `account_id_v2`) |
| `ACCOUNT_MID` | HoYoLAB account MID (`ltmid_v2` / `account_mid_v2`) |
| `ACCOUNT_TOKEN` | HoYoLAB account token (`ltoken_v2`) |
| `EMAIL_APP_PASSWORD` | Gmail App Password for failure notifications |
| `GAME_GI_AID` | Genshin Impact activity ID |
| `GAME_HSR_AID` | Honkai: Star Rail activity ID |
| `GAME_ZZZ_AID` | Zenless Zone Zero activity ID |

#### Variables
| Variable | Description |
|---|---|
| `EMAIL` | Gmail address for sending and receiving failure notifications |

---

### 3. Get Your HoYoLAB Cookie

1. Log in to [hoyolab.com](https://www.hoyolab.com)
2. Open DevTools (`F12`) → Application → Cookies
3. Copy the values for:
   - `ltuid_v2` → `ACCOUNT_ID`
   - `ltoken_v2` → `ACCOUNT_TOKEN`
   - `ltmid_v2` → `ACCOUNT_MID`

---

### 4. Get a Gmail App Password

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification → App Passwords
3. Generate a password for "Mail" → save it as `EMAIL_APP_PASSWORD`

> Gmail App Passwords require 2-Step Verification to be enabled.

---

### 5. Push to Main Branch

Once secrets are configured, push your code to `main`. The workflow will run automatically on schedule.

---

## How It Works

```
Daily at 12pm (PDT)
       │
       ▼
  GitHub Actions triggers
       │
       ▼
  Inject secrets from production environment
       │
       ▼
  Run main.py
  ├── Check in: Genshin Impact
  ├── Check in: Honkai: Star Rail
  └── Check in: Zenless Zone Zero
       │
    failures? ──► Send failure email
       │
    done ✅
```

---

## Running Manually

1. Go to the **Actions** tab in your repository
2. Click **HoYoLAB Daily Check-In**
3. Click **Run workflow** → select `main` → **Run workflow**

Always do a manual run first to confirm secrets are correctly configured before relying on the schedule.

---

## Schedule

Runs daily at **12:00 PM PDT (19:00 UTC)**.

To change the schedule, edit `.github/workflows/ci-cd.yml`:

```yaml
- cron: "0 19 * * *"    # daily at 12pm PDT (UTC-7)
```

> GitHub cron runs in UTC. The schedule may be delayed up to 60 minutes during high traffic periods.

> ⚠️ **Important:** GitHub automatically disables scheduled workflows if the repository has **no activity for 60 days**. You will receive an email from GitHub before it is disabled. To re-enable, go to the **Actions tab → HoYoLAB Daily Check-In → Enable workflow**.

---

## Email Notifications

You will receive two types of notifications:

| Source | When |
|---|---|
| **GitHub** | Workflow crashes or errors (exit code 1) |
| **Your Gmail** | Check-in fails due to expired cookie or API error |

---

## Local Development

Create a `.env` file in the project root (never commit this):

```bash
ACCOUNT_ID=your_account_id
ACCOUNT_MID=your_account_mid
ACCOUNT_TOKEN=your_token
EMAIL=your@gmail.com
EMAIL_APP_PASSWORD=your_app_password
GAME_GI_AID=e202102251931481
GAME_HSR_AID=e202303301540311
GAME_ZZZ_AID=e202406031448091
```

Install dependencies:

```bash
pip install requests python-dotenv
```

Run the script:

```bash
python main.py
```

---

## Project Structure

```
hoyolab-checkin/
├── main.py                        # main check-in script
├── requirements.txt               # dependencies (requests)
├── .env                           # local secrets (not committed)
├── .gitignore
└── .github/
    └── workflows/
        └── ci-cd.yml              # GitHub Actions workflow
```

---

## Troubleshooting

**Check-in fails with `-100` retcode**
Your cookie has expired. Repeat step 3 to get a fresh cookie and update your GitHub secrets.

**Workflow not triggering on schedule**
GitHub disables scheduled workflows after 60 days of repository inactivity. Go to Actions tab and click **Enable workflow**.

**`Missing account secrets` error**
One or more secrets are not set in your GitHub environment. Verify all secrets exist under **Settings → Environments → production**.

**`TabError: inconsistent use of tabs and spaces`**
Open `main.py` in Notepad++ → Edit → Blank Operations → **Tab to Space**, then save and push.

---

## Supported Games

| Game | Region |
|---|---|
| Genshin Impact | Global (HoYoLAB) |
| Honkai: Star Rail | Global (HoYoLAB) |
| Zenless Zone Zero | Global (HoYoLAB) |
