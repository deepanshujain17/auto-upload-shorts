from typing import Dict, Optional
import os
import hashlib
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

from moviepy.audio.AudioClip import AudioArrayClip, CompositeAudioClip

from settings import AudioSettings, PathSettings
from utils.media.audio_utils import convert_text_to_speech
from utils.media.ssml_text_generator import TextProcessor

# Shared thread pool for audio processing
_audio_executor: Optional[ThreadPoolExecutor] = None
_audio_executor_lock = asyncio.Lock()

def get_audio_executor() -> ThreadPoolExecutor:
    """Get or create the shared thread pool executor for audio processing."""
    global _audio_executor
    if _audio_executor is None:
        _audio_executor = ThreadPoolExecutor(max_workers=3)
    return _audio_executor

async def cleanup_audio_executor():
    """Cleanup the shared audio executor."""
    global _audio_executor
    async with _audio_executor_lock:
        if _audio_executor is not None:
            _audio_executor.shutdown(wait=True)
            _audio_executor = None

async def _run_in_audio_executor(func, *args, **kwargs):
    """Helper function to run a synchronous function in the audio executor."""
    loop = asyncio.get_running_loop()
    executor = get_audio_executor()
    return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))

class AudioComposer:
    """Handles audio generation and composition."""

    # Simple cache to avoid regenerating the same audio
    _audio_cache = {}

    @staticmethod
    async def generate_article_audio(article: Dict[str, str]) -> AudioArrayClip:
        """
        Generate audio from article text asynchronously.
        Args:
            article (Dict[str, str]): The article data containing title, description, and content etc.
        """
        # Create a unique hash of the article text to use as cache key
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        text_hash = hashlib.md5(f"{title}{description}{content}".encode('utf-8')).hexdigest()
        cache_file_path = os.path.join(PathSettings.OUTPUT_DIR, 'text_audio', f"cached_{text_hash}.mp3")

        # Check if we've already generated this audio
        if text_hash in AudioComposer._audio_cache:
            print("🎙️ Using cached audio for article")
            return AudioComposer._audio_cache[text_hash]

        # Check if cached file exists
        cache_exists = await _run_in_audio_executor(os.path.exists, cache_file_path)
        if cache_exists:
            print(f"🎙️ Loading cached audio from file: {cache_file_path}")
            # Load cached audio file logic would go here
            # For now, we'll continue with generation

        # Process the text in the main thread (this is lightweight)
        ssml_text = TextProcessor.prepare_article_text(article)
        print("🎙️ Generating audio from processed text")

        # Run the CPU-intensive text-to-speech in executor
        audio = await _run_in_audio_executor(
            convert_text_to_speech,
            ssml_text,
            AudioSettings.DEFAULT_VOICE_ID,
            AudioSettings.DEFAULT_ENGINE,
            AudioSettings.DEFAULT_TEXT_TYPE
        )

        # Cache the result
        AudioComposer._audio_cache[text_hash] = audio

        # We could also save to file for persistent caching
        # That would require additional code

        return audio

    @staticmethod
    async def create_composite_audio(speech_audio: AudioArrayClip,
                             music_audio_clip: AudioArrayClip,
                             duration: float) -> CompositeAudioClip:
        """Combine speech and background music asynchronously."""
        try:
            # These operations are CPU-bound and should run in executor

            # Scale speech audio volume
            scaled_speech = await _run_in_audio_executor(
                speech_audio.with_volume_scaled,
                AudioSettings.SPEECH_VOLUME
            )

            # Cut music to match speech duration and reduce volume
            music_audio = await _run_in_audio_executor(
                lambda: music_audio_clip.subclip(0, duration).with_volume_scaled(AudioSettings.MUSIC_VOLUME)
            )

            # Create composite audio
            composite = await _run_in_audio_executor(
                CompositeAudioClip,
                [scaled_speech, music_audio]
            )

            return composite
        except Exception as e:
            print(f"Error creating composite audio: {str(e)}")
            raise
