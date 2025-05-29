# auto-upload-shorts

A Python automation tool that creates and uploads YouTube Shorts with news overlays on a video. The tool fetches current news, generates visual news cards, overlays them on videos, and automatically uploads the result to YouTube as Shorts.

## Features

- 📰 Automatic news fetching and categorization
- 🎨 Dynamic news card generation with HTML templates
- 🎬 Video processing with news card overlay
- 🚀 Automated YouTube Shorts upload
- 🔒 Secure YouTube authentication

## Prerequisites

- Python 3.x
- A Google Cloud Project with YouTube Data API v3 enabled
- OAuth 2.0 credentials for YouTube API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auto-upload-shorts.git
cd auto-upload-shorts
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Additional Setup for YouTube API:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the YouTube Data API v3.
   - Create OAuth 2.0 credentials and download the `client_secrets.json` file.

4. To generate token.pkl for YouTube API authentication:
    - Run function in auth.py for the first time
    - This will open a browser window for you to authenticate your Google account and grant permissions.
    - After successful authentication, a `token.pkl` file will be created in the same directory. This file stores your access and refresh tokens securely for future use.

5. Create .env file in the root directory with the GNEWS API Credentials:
```bash
GNEWS_API_KEY=your_api_key_here
```

6. To run the application as Github Action:
    - create a `.github/workflows/youtube_upload.yml` file and create the necessary default workflow.
    - Encode base64 the `client_secrets.json` and `token.pkl` files and add them as secrets in your GitHub repository.
    - Add the GNEWS API key as a secret in your GitHub repository.


## Execution

The project supports different execution modes through GitHub Actions workflows or manual execution:

### GitHub Actions Workflows

Two separate workflows are configured to run at different times:

1. **Categories Workflow** (`youtube_upload_categories.yml`):
   - Processes news by predefined categories
   - Runs at different time on weekdays and weekends
   - Can be manually triggered through GitHub Actions UI

2. **Keywords Workflow** (`youtube_upload_keywords.yml`):
   - Processes news based on trending keywords/hashtags
   - Runs at different time on weekdays and weekends
   - Can be manually triggered through GitHub Actions UI

NOTE: Total scheduled runs of both the workflows on any day, together should be under 100 to avoid hitting the GNews API limit.

### Manual Execution

You can run the script locally in different modes:

```bash
Usage: python main.py [process_type]

process_type options:
    all        - Process both categories and trending keywords (default)
    categories - Process only predefined news categories
    keywords   - Process only trending keywords/hashtags
```

## Project Structure

```
.
├── main.py               # Main application entry point
├── requirements.txt      # Python dependencies
├── settings.py           # Application settings and configurations
├── Pipfile               # Pipenv dependency management
├── assets/               # Static assets
│   ├── images/            # Static images for overlay
│   ├── music/             # Background music files
│   └── videos/            # Background videos
├── core/                 # Core functionality modules
│   ├── news/              # News API integration
│   ├── trends/            # Trending topics API integration
│   └── youtube/           # YouTube API integration
├── others/               # Authentication and configuration
│   └── archive_scripts/         # Legacy implementation scripts
│   ├── client_secrets.json      # YouTube API credentials
│   ├── client_secrets.json.b64  # Base64 encoded credentials
│   ├── token.pkl                # YouTube authentication token
│   └── token.b64                # Base64 encoded token
├── output/              # Generated outputs
│   ├── history/           # Historical data storage
│   ├── intermediate/      # Temporary processing files
│   └── text_audio/        # Generated audio files
├── playground/          # Testing and development
│   └── outputs/           # Test output files
├── services/             # Core service implementations
│   ├── auth.py               # Authentication service
│   ├── fetch_news.py         # News fetching service
│   ├── shorts_uploader.py    # YouTube upload service
│   └── video_processor.py    # Video processing service
└── utils/              # Utility modules
    ├── commons.py         # Common utility functions
    ├── media/             # Media processing utilities
    ├── metadata/          # Metadata and tagging utilities
    └── web/               # Web-related utilities
```
