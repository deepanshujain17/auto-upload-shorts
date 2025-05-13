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

4. To generate token.pkl for YouTube API authentication, run:
    - Run function in auth.py for the first time
    - This will open a browser window for you to authenticate your Google account and grant permissions.
    - After successful authentication, a `token.pkl` file will be created in the same directory. This file stores your access and refresh tokens securely for future use.

5. Create .env file in the root directory and the GNEWS API Credentials:
```bash 
GNEWS_API_KEY=your_gnews_api_key
````

6. To run the application as Github Action:
    - create a `.github/workflows/youtube_upload.yml` file and create the necessary default workflow.
    - Encode base64 the `client_secrets.json` and `token.pkl` files and add them as secrets in your GitHub repository.
    - Add the GNEWS API key as a secret in your GitHub repository.

## Project Structure

```
.
├── main.py                # Main application entry point
├── requirements.txt       # Python dependencies
├── settings.py           # Application settings
├── archive_scripts/      # Archive of previous implementations
├── assets/
│   ├── images/          # Static images
│   └── videos/          # Background videos and BGM
├── news/
│   ├── news_fetcher.py  # News fetching implementation
│   ├── news_cards/      # Generated news card images
│   ├── temp/            # Temporary HTML templates
│   └── utils/           # News processing utilities
├── others/              # Authentication files
│   ├── client_secrets.json
│   └── token.pkl
├── output/              # Generated video outputs
└── utils/              
    ├── auth.py         # YouTube authentication
    ├── upload.py       # YouTube upload functionality
    └── video_processor.py
```
``
