class PathSettings:
    # Directory paths
    OUTPUT_DIR = "output"
    ASSETS_DIR = "assets"
    CONFIG_DIR = f"{ASSETS_DIR}/config"
    ASSETS_VIDEO_DIR = f"{ASSETS_DIR}/videos"
    ASSETS_MUSIC_DIR = f"{ASSETS_DIR}/music"
    ASSETS_IMAGE_DIR = f"{ASSETS_DIR}/images"
    HTML_CARD_DIR = f"{OUTPUT_DIR}/intermediate/html_card"
    NEWS_CARDS_DIR = f"{OUTPUT_DIR}/intermediate/news_card"

    # File path helper methods
    @staticmethod
    def get_html_output(category: str) -> str:
        return f"{PathSettings.HTML_CARD_DIR}/temp_{category}.html"

    @staticmethod
    def get_overlay_image(category: str) -> str:
        return f"{PathSettings.NEWS_CARDS_DIR}/card_{category}.png"

    @staticmethod
    def get_video_path(bgm_video: str) -> str:
        return f"{PathSettings.ASSETS_VIDEO_DIR}/{bgm_video}.mp4"

    @staticmethod
    def get_music_path(bg_music: str) -> str:
        return f"{PathSettings.ASSETS_MUSIC_DIR}/{bg_music}.mp3"

    @staticmethod
    def get_image_path(bg_image: str) -> str:
        return f"{PathSettings.ASSETS_IMAGE_DIR}/{bg_image}.png"

    @staticmethod
    def get_final_video(category: str) -> str:
        return f"{PathSettings.OUTPUT_DIR}/short_with_overlay_{category}.mp4"
