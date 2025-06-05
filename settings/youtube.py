class YouTubeSettings:
    DEFAULT_PRIVACY = "public"  # Options: "public", "private", "unlisted"
    ARTICLE_MAX_TAGS = 3
    MAX_TAGS = 9

    # Default HashTags
    DEFAULT_HASHTAGS = ["TrendingNow", "CurrentAffairs"]
    EXTRA_DESCRIPTION_HASHTAGS = ["shorts"]

    # Mapping of content categories to Relevant HashTags
    CATEGORY_HASHTAG_MAP = {
        "general": ["BreakingNews", "TrendingNow"],
        "sports": ["SportsNews", "GameDay"],
        "world": ["WorldNews", "GlobalUpdates"],
        "nation": ["IndiaNews", "HeadlinesToday"],
        "business": ["MarketWatch", "EconomyToday"],
        "technology": ["TechNews", "Innovation"],
        "entertainment": ["CelebBuzz", "PopCulture"],
        "science": ["SpaceAndBeyond", "Discovery"]
    }

    # Default YouTube category ID for videos
    DEFAULT_YOUTUBE_CATEGORY = 22        # People & Blogs

    # Mapping of content categories to YouTube category IDs
    CATEGORY_TO_YOUTUBE_CATEGORY_MAP = {
        "general": 22,           # People & Blogs
        "sports": 17,            # Sports
        "world": 25,             # News & Politics
        "nation": 25,            # News & Politics
        "business": 26,          # Howto & Style (finance-oriented content)
        "technology": 28,        # Science & Technology
        "entertainment": 24,     # Entertainment
        "science": 28,           # Science & Technology
        "health": 26             # Howto & Style (for wellness/fitness)
    }

    # YouTube Playlist Settings
    DEFAULT_PLAYLIST_ID = "PLxkrFcfC1HKTjWUEuNsGkx7596lkYHmnM"     # #NowTrending 🔥 – What Everyone's Talking About

    # Mapping of content categories to the respective YouTube playlist IDs
    CATEGORY_PLAYLIST_MAP = {
        "general": "PLxkrFcfC1HKQtEf4Ief6JdVjej1vA9xbG",           # NewsFlash 🔥 Top Stories & Trends
        "sports": "PLxkrFcfC1HKTo4hVW1uxhesL9T6j99NSP",            # Game On! ⚽ Sports Highlights & Updates
        "world": "PLxkrFcfC1HKQ8WPQJUHA6B69C0ag8h5T1",             # Global Pulse 🌍 What's Happening Around the World
        "nation": "PLxkrFcfC1HKQ9EAijefBRgiEtlwQOaNYU",            # India Now 🇮🇳 Headlines That Matter
        "business": "PLxkrFcfC1HKSnjFyVE2Je1KlrrjzPtUDJ",          # Market Moves 📈 Business & Economy Shorts
        "technology": "PLxkrFcfC1HKTkvOIQKV0yByHn3uRdmE3g",        # Tech Shorts 🚀 Gadgets, AI & Future Bytes
        "entertainment": "PLxkrFcfC1HKQRZA4hBZbW9T0AY-7TprxX",     # PopBeat 🎬 Movies, Celebs & Culture
        "science": "PLxkrFcfC1HKRwOXokC0nh2gmnE4Vgwls5",           # Mind Blown 🔬 Fascinating Science & Discoveries
        "health": "PLxkrFcfC1HKREoe7AA5sSsvhuae5-K2se",            # Health Shot 💪 Wellness, Fitness & Medical News
    }
