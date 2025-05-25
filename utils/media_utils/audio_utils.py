import boto3
from io import BytesIO
import numpy as np
from pydub import AudioSegment
from moviepy.audio.AudioClip import AudioArrayClip

def convert_text_to_speech(text: str,
                          voice_id: str = "Joanna",
                          engine: str = "neural",
                          text_type: str = "text") -> AudioArrayClip:
    """
    Convert article text to speech using Amazon Polly and return as AudioArrayClip.

    Args:
        text (str): The text to convert to speech
        voice_id (str): Amazon Polly voice ID to use (default: Joanna)
        engine (str): Polly engine type - 'neural' or 'standard' (default: neural)
        text_type (str): Type of input text - 'text' or 'ssml' (default: text)

    Returns:
        AudioArrayClip: Audio clip that can be used directly with moviepy

    Raises:
        ValueError: If text is empty or text_type is invalid
        boto3.exceptions.BotoServerError: If AWS Polly service fails
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")

    if text_type not in ["text", "ssml"]:
        raise ValueError("text_type must be either 'text' or 'ssml'")

    try:
        # Initialize Polly client
        polly = boto3.client("polly")

        # Generate speech
        response = polly.synthesize_speech(
            Text=text,
            TextType=text_type,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine=engine
        )

        # Convert audio stream to AudioArrayClip
        audio_data = BytesIO(response["AudioStream"].read())
        audio_segment = AudioSegment.from_mp3(audio_data)

        # Convert to numpy array
        samples = np.array(audio_segment.get_array_of_samples())

        # Convert to float32 and normalize
        samples = samples.astype(np.float32)
        samples = samples / (2**15)  # Normalize to [-1, 1]

        # Create AudioArrayClip
        fps = audio_segment.frame_rate
        audio_clip = AudioArrayClip(samples.reshape(-1, 1), fps)

        print("✅ Audio generated successfully")
        return audio_clip

    except Exception as e:
        print(f"❌ Error generating audio: {str(e)}")
        raise
