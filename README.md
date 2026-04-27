# auto-upload-shorts 🎬

Python automation that turns GNews articles into YouTube Shorts: fetch news, render an HTML news card (screenshot), synthesize speech with **AWS Polly**, compose video with **MoviePy/FFmpeg**, and upload via the **YouTube Data API**.

📖 For a full local + CI runbook (secrets, workflows, troubleshooting), see **[AGENTS.md](AGENTS.md)**.

## Features

- 📰 News from **GNews** by category and/or trending + manual keywords
- 🎨 News card overlay (HTML → Selenium screenshot)
- 🎬 **TTS** (Polly) and short video composition
- 🚀 Automated Shorts upload (and playlist handling where configured)
- 🌍 Multi-country / multi-language runs (`en`, `hi`, etc.) with the correct GNews key and token file when configured

## Prerequisites

- 🐍 **Python 3.12** (matches CI; other 3.x may work but 3.12 is the tested version)
- 🎞️ **FFmpeg** (on PATH) for encode/mux
- 🌐 **Chrome or Chromium** for Selenium card rendering
- ☁️ **Google Cloud**: project with YouTube Data API v3 enabled, OAuth client → `client_secrets.json` in repo root
- 🔑 **AWS credentials** with Polly access (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`)
- 📡 **GNews** API key(s) in `.env` (see below)

## Installation 🛠️

1. Clone the repository and enter the directory.

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **macOS system dependency** (FFmpeg):

```bash
brew install ffmpeg
```

4. **YouTube OAuth**: place `client_secrets.json` in the **repo root**. Generate tokens by running the app once (browser OAuth):

```bash
python main.py categories
```

This creates `token.pkl` for the default language/channel. For Hindi (`hi`), the pipeline uses `token_hi.pkl` when you run with language `hi` (see [AGENTS.md](AGENTS.md)).

5. **Environment variables (local only)** — create a file named **`.env` in the repo root** (next to `main.py`). `python-dotenv` loads it when you run locally. YouTube files stay as **normal files** in the repo root, not base64:

```bash
# GNews (required for most runs)
GNEWS_API_KEY=your_key
# Optional: used when you run with language hi (see settings)
# GNEWS_HI_API_KEY=...

# AWS Polly / boto3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=...
```

| Variable | Where (local) | Role |
|----------|-----------------|------|
| `GNEWS_API_KEY` | `.env` | Default GNews key |
| `GNEWS_HI_API_KEY` | `.env` | Optional; preferred for Hindi (`hi`) |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` | `.env` (or your shell / IAM role) | Polly TTS |
| — | **Files** in repo root, not in `.env` | `client_secrets.json`, `token.pkl`, `token_hi.pkl` |

## How to run locally 🖥️

```bash
python main.py [all|categories|keywords] [country] [language]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `process_type` | `all` | `all`, `categories`, or `keywords` |
| `country` | `in` | Country code (e.g. `in`, `us`) |
| `language` | `en` | Language code (e.g. `en`, `hi`) |

Examples:

```bash
python main.py categories us en
python main.py keywords in en
python main.py categories in hi
```

## GitHub Actions ⚙️

Workflows live under `.github/workflows/`. Typical set:

| Workflow | Purpose |
|----------|---------|
| `youtube_upload_categories.yml` | Categories, default country |
| `youtube_upload_keywords.yml` | Keywords, default country |
| `youtube_upload_categories_us.yml` | Categories, `us` |
| `youtube_upload_keywords_us.yml` | Keywords, `us` |
| `youtube_upload_categories_hi.yml` | Hindi (`in hi`), includes Devanagari font setup |

### Where to define values for Actions

On GitHub: **Repository → Settings → Secrets and variables → Actions → New repository secret**.  
Use the **name** in the first column exactly (that is how `${{ secrets.… }}` resolves in the workflows).

| Repository secret | What to paste | On the runner the job… |
|-------------------|---------------|-------------------------|
| `GNEWS_API_KEY` | Plain GNews API key | Writes **`.env`** with `GNEWS_API_KEY=…` |
| `GNEWS_HI_API_KEY` | Plain GNews API key | Writes **`.env`** with `GNEWS_HI_API_KEY=…` (**Hindi** workflow only) |
| `CLIENT_SECRETS_B64` | **Base64** of your local `client_secrets.json` (single line, no newlines in the secret value) | Decodes to **`client_secrets.json`** in repo root |
| `TOKEN_PKL_B64` | **Base64** of your local `token.pkl` | Decodes to **`token.pkl`** in repo root |
| `TOKEN_HI_PKL_B64` | **Base64** of your local `token_hi.pkl` | Decodes to **`token_hi.pkl`** in repo root (**Hindi** workflow only) |
| `AWS_ACCESS_KEY_ID` | Plain key | Passed into **aws-actions/configure-aws-credentials** (not added to `.env` by these workflows) |
| `AWS_SECRET_ACCESS_KEY` | Plain secret | Same |
| `AWS_REGION` | Region string, e.g. `us-east-1` | Same |

**Which workflows need which secrets**

| Workflows | Required repository secrets |
|-----------|-----------------------------|
| `youtube_upload_categories.yml`, `youtube_upload_keywords.yml`, `youtube_upload_categories_us.yml`, `youtube_upload_keywords_us.yml` | `GNEWS_API_KEY`, `CLIENT_SECRETS_B64`, `TOKEN_PKL_B64`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |
| `youtube_upload_categories_hi.yml` | `GNEWS_HI_API_KEY`, `CLIENT_SECRETS_B64`, `TOKEN_HI_PKL_B64`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |

To produce a one-line base64 string locally (example for `client_secrets.json` on macOS):

```bash
base64 < client_secrets.json | tr -d '\n'
```

Paste the entire output into the matching `*_B64` secret. Repeat for `token.pkl` / `token_hi.pkl`.

Workflows decode credentials into the repo root at runtime; do not commit real secrets or paste raw JSON/pickle into GitHub—only the **base64** form for the `*_B64` secrets.

**Quotas:** keep total scheduled GNews traffic within your plan (historically workflows note staying under daily limits when scheduling multiple jobs).

## Code layout 🧩

- `main.py` — async orchestrator
- `core/` — GNews, trends, YouTube API clients
- `services/` — auth, fetch news, video pipeline, upload
- `utils/` — Selenium rendering, media, metadata, file locking, idempotency helpers
- `settings/` — config, paths, language (`apply_language`)

## Project structure (high level) 📁

```
.
├── main.py
├── requirements.txt
├── AGENTS.md
├── settings/              # config, language, paths
├── core/
│   ├── news/
│   ├── trends/
│   └── youtube/
├── services/
│   ├── auth.py
│   ├── fetch_news.py
│   ├── video_processor.py
│   └── shorts_uploader.py
├── utils/
│   ├── media/
│   ├── web/
│   ├── metadata/
│   ├── file_lock.py
│   └── idempotency_store.py
├── assets/                # images, music, videos, config (e.g. manual hashtags)
├── output/                # generated videos and intermediates (gitignored as appropriate)
└── others/archive_scripts/  # legacy reference only
```

🔒 Do not commit `client_secrets.json`, `token.pkl`, `token_hi.pkl`, or `.env`. In CI, those files are recreated from Actions secrets each run.
