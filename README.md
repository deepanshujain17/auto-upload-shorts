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

## Project Structure

```
├── assets/
│   ├── images/      # Store your image assets
