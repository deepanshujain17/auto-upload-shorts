from io import BytesIO

import boto3
import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip
from pydub import AudioSegment

def _init_polly_client():
    """Initialize and return AWS Polly client."""
    return boto3.client("polly")

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

    try:
        polly = _init_polly_client()

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
        error_msg = f"Error generating audio: {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg) from e
