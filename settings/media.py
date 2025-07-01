from settings import HTMLSettings


class VideoSettings:
    IMAGE_HEIGHT = 800
    IMAGE_VERTICAL_OFFSET = 300
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    FPS = 24

class BrowserSettings:
    WINDOW_WIDTH = HTMLSettings.CARD_WIDTH
    WINDOW_HEIGHT = 820
    BROWSER_WAIT_TIME = 2  # seconds

class AudioSettings:
    NORMALIZATION_FACTOR = 2**15  # Factor to normalize audio samples to [-1, 1]
    SPEECH_VOLUME = 1.0
    BACKGROUND_MUSIC_VOLUME = 0.15

    # AWS Polly voice settings
    DEFAULT_VOICE_ID = "Joanna"
    DEFAULT_ENGINE = "neural"
    DEFAULT_TEXT_TYPE = "ssml"

    # SSML settings
    PROSODY_RATE = "100%"
    PROSODY_VOLUME = "loud"
    PROSODY_PITCH = "0%"
