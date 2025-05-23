import boto3
import os
from typing import Optional

def convert_text_to_speech(text: str,
                          output_filename: Optional[str] = None,
                          voice_id: str = "Joanna",
                          engine: str = "neural",
                          text_type: str = "text") -> str:
    """
    Convert article text to speech using Amazon Polly.

    Args:
        text (str): The text to convert to speech
        output_filename (str, optional): Path where to save the audio file.
                                       If None, saves to default location
        voice_id (str): Amazon Polly voice ID to use (default: Joanna)
        engine (str): Polly engine type - 'neural' or 'standard' (default: neural)
        text_type (str): Type of input text - 'text' or 'ssml' (default: text)

    Returns:
        str: Path to the generated audio file
    """
    # Initialize Polly client
    polly = boto3.client("polly")

    # If no output filename provided, use default path
    if output_filename is None:
        os.makedirs("../output/text_audio", exist_ok=True)
        output_filename = "../output/text_audio/polly_output.mp3"

    # Generate speech
    audio_output = polly.synthesize_speech(
        Text=text,
        TextType=text_type,
        OutputFormat="mp3",
        VoiceId=voice_id,
        Engine=engine
    )

    # Save the audio file
    # with open(output_filename, "wb") as f:
    #     f.write(audio_output["AudioStream"].read())

    # print(f"✅ Audio saved as '{output_filename}'")
    return audio_output
