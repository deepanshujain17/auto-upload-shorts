import boto3
from typing import Optional
from pathlib import Path

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

    Raises:
        ValueError: If text is empty or text_type is invalid
        boto3.exceptions.BotoServerError: If AWS Polly service fails
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")

    if text_type not in ["text", "ssml"]:
        raise ValueError("text_type must be either 'text' or 'ssml'")

    # Initialize Polly client
    try:
        polly = boto3.client("polly")

        # If no output filename provided, use default path
        if output_filename is None:
            output_dir = Path("output/text_audio")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_filename = str(output_dir / "polly_output.mp3")
        else:
            # Ensure the directory exists for custom output path
            Path(output_filename).parent.mkdir(parents=True, exist_ok=True)

        # Generate speech
        response = polly.synthesize_speech(
            Text=text,
            TextType=text_type,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine=engine
        )

        # Save the audio file
        with open(output_filename, "wb") as f:
            f.write(response["AudioStream"].read())

        print(f"✅ Audio saved as '{output_filename}'")
        return output_filename

    except Exception as e:
        print(f"❌ Error generating audio: {str(e)}")
        raise
