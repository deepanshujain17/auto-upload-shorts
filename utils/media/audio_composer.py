from typing import Dict

from moviepy.audio.AudioClip import AudioArrayClip, CompositeAudioClip

from settings import AudioSettings
from utils.media.audio_utils import convert_text_to_speech
from utils.media.ssml_text_generator import TextProcessor


class AudioComposer:
    """Handles audio generation and composition."""

    @staticmethod
    def generate_article_audio(article: Dict[str, str]) -> AudioArrayClip:
        """
        Generate audio from article text. Process the article text into SSML format and convert to speech.
        Args:
            article (Dict[str, str]): The article data containing title, description, and content etc.
        """
        ssml_text = TextProcessor.prepare_article_text(article)
        print("🎙️Generating audio from processed text")

        return convert_text_to_speech(
            text=ssml_text,
            voice_id=AudioSettings.DEFAULT_VOICE_ID,
            engine=AudioSettings.DEFAULT_ENGINE,
            text_type=AudioSettings.DEFAULT_TEXT_TYPE
        )

    @staticmethod
    def create_composite_audio(speech_audio: AudioArrayClip,
                             music_audio_clip: AudioArrayClip,
                             duration: float) -> CompositeAudioClip:
        """Combine speech and background music."""

        # Scale speech audio volume
        speech_audio = speech_audio.with_volume_scaled(AudioSettings.SPEECH_VOLUME)

        # Scale background music volume and set duration same as speech audio
        music_audio = (music_audio_clip
                       .with_volume_scaled(AudioSettings.BACKGROUND_MUSIC_VOLUME)
                       .with_duration(duration))

        # Combine speech and music audio
        combined_audio = CompositeAudioClip([speech_audio, music_audio])

        return combined_audio