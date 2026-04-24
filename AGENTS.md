# AGENTS.md

This file is the **development + deployment runbook** for this repo. It’s meant to be the single source of truth for how to run the pipeline locally and how it runs in CI (GitHub Actions).

## Project Purpose
- Automates YouTube Shorts from GNews: fetch article -> render card -> synthesize speech -> compose video -> upload.
- Entry point is `main.py`; orchestration is async and supports category mode, keyword mode, or both.

## What this project does
- Fetch news (GNews) by **category** and/or **keywords (trending + manual)**.
- Render a “news card” overlay (HTML → screenshot).
- Generate TTS audio (AWS Polly) and compose a short video (MoviePy/FFmpeg).
- Upload to YouTube Shorts (YouTube Data API).

**Entry point:** `main.py`

## Repo layout (what to touch)
- `main.py`: async orchestrator (`categories`, `keywords`, `all`)
- `services/`
  - `auth.py`: YouTube OAuth (`client_secrets.json` + token pickle files)
  - `fetch_news.py`: pulls articles for categories/keywords
  - `video_processor.py`: render overlay + compose audio/video
  - `shorts_uploader.py`: upload + playlist add
- `core/`: API clients (news, trends, youtube)
- `utils/`: rendering (Selenium), media composition, metadata helpers, file locking
- `settings/`: configuration + language selection (`apply_language`)

## Runtime data flow (quick mental model)
- **News fetch**: `main.py` → `services/fetch_news.py` → `core/news/*`
- **Card rendering**: `utils/web/html_utils.py:create_html_card` → `utils/web/browser_utils.py:render_card_to_image`
- **Audio (TTS)**: `utils/media/ssml_text_generator.py` → `utils/media/audio_utils.py` (AWS Polly) → `utils/media/audio_composer.py`
- **Video compose**: `services/video_processor.py` + `utils/media/video_composer.py` → `output/*.mp4`
- **Upload**: `services/shorts_uploader.py` → `core/youtube/*` (upload + playlist add)

## Local development: prerequisites
- **Python**: 3.12 is what CI uses (see workflows in `.github/workflows/`)
- **FFmpeg**: required by MoviePy for encode/mux
- **A Chrome runtime** (or Chromium): required for Selenium screenshot rendering

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### System dependencies (macOS)

```bash
brew install ffmpeg
```

Selenium needs Chrome/Chromium available. If you hit driver/browser issues, verify Chrome is installed and that `webdriver-manager` can download a compatible driver.

## Required secrets / credentials

### GNews
Environment variables (loaded via `python-dotenv` from `.env`):
- `GNEWS_API_KEY`: default API key (also used as fallback for other languages)
- `GNEWS_HI_API_KEY`: optional, preferred key for Hindi runs (`hi`)

Minimal local `.env`:

```bash
GNEWS_API_KEY=...
```

### AWS (Polly)
TTS uses `boto3`, so your runtime must have standard AWS credentials available (any of the usual AWS SDK mechanisms work):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

CI uses `aws-actions/configure-aws-credentials`.

### YouTube (OAuth)
Files expected in **repo root**:
- `client_secrets.json`
- `token.pkl` (default channel)
- `token_hi.pkl` (used when language is `hi`)

Token selection is automatic in `services/auth.py` based on the configured language.

#### Generating token pickle(s) locally
Run once locally to complete OAuth in a browser and create the token file:

```bash
python main.py categories
```

This triggers YouTube authentication and writes `token.pkl` (or `token_hi.pkl` when running with `hi`).

## How to run locally
`main.py` supports:

```bash
python main.py [all|categories|keywords] [country] [language]
```

Defaults when omitted:
- `process_type`: `all`
- `country`: `in`
- `language`: `en`

Examples:

```bash
python main.py categories us en
python main.py keywords in en
python main.py categories in hi
```

## Deployment (GitHub Actions)
This repo deploys by **scheduled GitHub Actions workflows** in `.github/workflows/`:
- `youtube_upload_categories.yml`: categories (default country)
- `youtube_upload_keywords.yml`: keywords (default country)
- `youtube_upload_categories_us.yml`, `youtube_upload_keywords_us.yml`: US runs (`us`)
- `youtube_upload_categories_hi.yml`: Hindi run (`in hi`) + installs Devanagari fonts

### CI runtime expectations
Workflows install:
- system deps: `ffmpeg`
- python deps: `pip install -r requirements.txt`
- AWS credentials: via `aws-actions/configure-aws-credentials@v4`

### Required GitHub secrets
English/default workflows expect:
- `GNEWS_API_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- `CLIENT_SECRETS_B64`: base64 of `client_secrets.json`
- `TOKEN_PKL_B64`: base64 of `token.pkl`

Hindi workflow (`youtube_upload_categories_hi.yml`) expects:
- `GNEWS_HI_API_KEY`
- `TOKEN_HI_PKL_B64`: base64 of `token_hi.pkl`
- `CLIENT_SECRETS_B64`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`

At runtime the workflows decode secrets into repo root:
- `client_secrets.json`
- `token.pkl` or `token_hi.pkl`
- `.env` containing the appropriate `GNEWS_*` key

## Operational notes / guardrails
- **Language must be applied before auth**: `main.py` calls `apply_language()` early; keep it that way so the correct GNews key and Polly voice are selected.
- **Concurrency**: category and hashtag processing is intentionally bounded (semaphores). Avoid unbounded `gather()` expansions that can trigger API rate limits.
- **File outputs**: video/image/html outputs are protected by `utils/file_lock.py`. Keep locks in place when adding new intermediate outputs.
- **Cleanup**: `async_main()` calls `close_session()` and executor cleanup in `finally`. Preserve those patterns so CI runners don’t leak resources.
- **Layering**: keep boundaries intact (`core` for API calls, `services` for orchestration, `utils` for primitives). Avoid leaking HTTP/API specifics into `services`.
- **Paths**: prefer `settings/paths.py` helpers over hardcoded asset/output paths.
- **Non-fatal empties**: missing/empty news results should remain non-fatal; continue iterating across categories/keywords.
- **Legacy scripts**: treat `others/archive_scripts/` as legacy reference, not part of the active pipeline.

## If you change the pipeline
Update this file if you change any of:
- CLI args / defaults in `main.py`
- required env vars / secrets
- token file naming or locations
- CI workflow names, schedules, or secret names

