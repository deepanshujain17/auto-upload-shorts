from io import BytesIO
import time
import boto3
from botocore.config import Config
import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip
from pydub import AudioSegment

def _init_polly_client():
    """Initialize and return AWS Polly client with proper timeout settings."""
    # Configure AWS client with appropriate timeouts and retries
    config = Config(
        connect_timeout=10,  # 10 seconds for connection timeout
        read_timeout=30,     # 30 seconds for read timeout
        retries={
            'max_attempts': 3,  # Retry up to 3 times
            'mode': 'standard'
        }
    )
    return boto3.client("polly", config=config)

def _process_audio_stream(audio_stream: bytes) -> AudioArrayClip:
    """
    Process raw audio stream into an AudioArrayClip.

    Args:
        audio_stream: Raw audio data in bytes

    Returns:
        AudioArrayClip: Processed audio clip
    """
    # Convert audio stream to AudioSegment
    audio_data = BytesIO(audio_stream)
    audio_segment = AudioSegment.from_mp3(audio_data)

    # Convert to numpy array and normalize
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
    samples = samples / (2**15)  # Normalize Polly output to range [-1, 1]

    # Create and return AudioArrayClip
    fps = audio_segment.frame_rate
    return AudioArrayClip(samples.reshape(-1, 1), fps)

def convert_text_to_speech(
    text: str,
    voice_id: str = "Joanna",
    engine: str = "neural",
    text_type: str = "ssml"
) -> AudioArrayClip:
    """
    Generate audio from text using AWS Polly.

    Args:
        text: The text to convert to speech
        voice_id: AWS Polly voice ID (default: Matthew)
        engine: AWS Polly engine type (default: neural)
        text_type: Type of input text - 'text' or 'ssml' (default: text)

    Returns:
        AudioArrayClip: Generated audio as MoviePy AudioArrayClip

    Raises:
        ValueError: If text_type is invalid
        RuntimeError: If audio generation fails
    """
    if text_type not in ["text", "ssml"]:
        raise ValueError("text_type must be either 'text' or 'ssml'")

    # Implement retry logic for network issues
    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            polly = _init_polly_client()

            print(f"🎙️ Generating speech (attempt {attempt}/{max_retries})...")

            # Generate speech using Polly
            response = polly.synthesize_speech(
                Text=text,
                TextType=text_type,
                OutputFormat="mp3",
                VoiceId=voice_id,
                Engine=engine
            )

            audio_clip = _process_audio_stream(response["AudioStream"].read())
            print("🎙️ ✅ Audio generated successfully")
            return audio_clip

        except Exception as e:
            if "Read timeout" in str(e) and attempt < max_retries:
                print(f"⚠️ Read timeout occurred. Retrying in {retry_delay} seconds... (Attempt {attempt}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                error_msg = f"Error generating audio: {str(e)}"
                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg) from e
