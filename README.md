# Dice Jobs AI Automation

A Selenium + OpenAI-powered Python bot that auto-applies to jobs on [Dice.com](https://www.dice.com) matching your keywords and location. Uses an LLM to answer the dynamic free-text questions that Dice sprinkles into application forms, and skips roles you've already applied to.

> **Disclaimer:** Dice's Terms of Service prohibit automated activity; running this against a live account carries account-suspension risk. This project is intended for learning browser-automation and LLM-integration patterns.

## What it does

1. Logs into Dice with credentials from `src/config.yaml`
2. Searches for roles by keyword, location, and how recently they were posted
3. Iterates job cards and clicks **Easy Apply** where available
4. Fills standard fields from your saved profile data
5. For dynamic free-text questions, asks OpenAI to draft an answer based on your profile
6. Clicks through **Next** steps and submits
7. Tracks applied job IDs so it never applies twice

## Stack

| Layer | Tool |
|---|---|
| Language | Python 3.8+ |
| Browser automation | Selenium |
| Driver management | `webdriver-manager` (auto-downloads matching ChromeDriver) |
| LLM | OpenAI (default model: `openai==0.28`) |
| Config | YAML (`src/config.yaml`) |

## Setup

```bash
git clone https://github.com/svrohith9/dice_jobs_ai_automation.git
cd dice_jobs_ai_automation

python3 -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

No manual ChromeDriver install required — `webdriver-manager` fetches the right version for your installed Chrome on first run.

## Configure

Copy the template and fill in your real values:

```bash
cp src/config.yaml.example src/config.yaml
```

Then edit `src/config.yaml`:

```yaml
credentials:
  username: "you@example.com"
  password: "your-password"

search_params:
  keyword: "Java"
  location: "United States"
  days_posted: 3

openai:
  api_key: "sk-..."
```

> **Security:** `src/config.yaml` is gitignored — your real credentials won't be committed. Only the placeholder template (`src/config.yaml.example`) is tracked.

## Run

```bash
python src/app.py
```

The script launches Chrome, signs in, and starts the apply loop. Already-applied job IDs are persisted locally so reruns continue where you left off. Logs stream to the console and to `application.log`.

## Project structure

```
src/
├── app.py           # Main orchestrator — search, iterate, apply
├── login.py         # Dice login flow
├── job_search.py    # Search and pagination
├── ai_helper.py           # OpenAI wrapper for dynamic form answers
├── config.yaml.example    # Committed template — copy to config.yaml
├── config.yaml            # Your real credentials (gitignored)
└── data.yaml              # Profile data used to fill standard fields
```

## Roadmap

- [ ] Headless-mode toggle
- [ ] Bump `openai` to v1.x with the new client API
- [ ] Per-job cover letter generation
- [ ] End-of-run summary (applied / skipped / failed)

## Troubleshooting

- **ChromeDriver version mismatch** — delete `~/.wdm` cache so `webdriver-manager` re-fetches.
- **Dice UI changed** — this bot relies on page selectors. Expect locator updates when Dice ships a redesign.
- **OpenAI rate limits** — lower the apply rate or switch to a cheaper model in `ai_helper.py`.

## License

MIT
