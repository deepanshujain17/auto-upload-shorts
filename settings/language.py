from __future__ import annotations

from .news import news_settings
from .media import audio_settings
from .config import get_env_var

# Map supported languages to their environment keys and TTS voice IDs
_LANG_CONFIG: dict[str, dict[str, str]] = {
    "en": {
        "api_key_env": "GNEWS_API_KEY",
        "voice_id": "Joanna",
        "language": "en",
    },
    "hi": {
        "api_key_env": "GNEWS_HI_API_KEY",
        "voice_id": "Kajal",
        "language": "hi",
    },
}


def apply_language(lang_code: str) -> None:
    """Apply language-specific settings and validate API key.

    Uses the language-specific env var first, then falls back to GNEWS_API_KEY.
    Raises ValueError only if both are missing.
    """
    code = (lang_code or "").strip().lower()
    if code not in _LANG_CONFIG:
        raise ValueError(f"Unsupported language code: {lang_code}")

    cfg = _LANG_CONFIG[code]

    # Update language setting
    news_settings.language = cfg.get("language", code)

    # Resolve API key with fallback to the default env var
    primary_env = cfg["api_key_env"]
    api_key = get_env_var(primary_env)
    if not api_key:
        fallback_env = "GNEWS_API_KEY"
        api_key = get_env_var(fallback_env)
        if not api_key:
            raise ValueError(
                f"Missing API key for language '{code}'. Set {primary_env} (preferred) or {fallback_env}."
            )
    news_settings.api_key = api_key

    # Update default voice for Polly
    audio_settings.DEFAULT_VOICE_ID = cfg["voice_id"]
