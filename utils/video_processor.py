from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from playsound import playsound

from settings import VideoSettings, NewsSettings, PathSettings
from utils.media_utils.audio_utils import convert_text_to_speech


def create_overlay_video(video_path, image_path, output_path="output_with_overlay.mp4"):
    """
    Create a video with an image overlay.

    Args:
        video_path (str): Path to the input video file
        image_path (str): Path to the overlay image file
        output_path (str): Path where the output video will be saved

    Returns:
        str: Path to the output video file
    """
    video = VideoFileClip(video_path)
    image = (
        ImageClip(image_path)
        .with_duration(video.duration)
        .resized(height=VideoSettings.IMAGE_HEIGHT)
        .with_position(("center", video.h // 2 - VideoSettings.IMAGE_VERTICAL_OFFSET))
    )
    final = CompositeVideoClip([video, image])
    final.write_videofile(
        output_path,
        codec=VideoSettings.VIDEO_CODEC,
        audio_codec=VideoSettings.AUDIO_CODEC,
        logger=None) # Suppress moviepy logger. logger="bar" (default) providees a progress bar

    print("✅ Overlay video created successfully!")
    return output_path

def create_overlay_video_output(category: str, overlay_image: str) -> str:
    """
    Create an overlay video with the news card.
    Args:
        category (str): News category to process
        overlay_image (str): Path to the overlay image

    Returns:
        str: Path to the final video
    Raises:
        Exception: If video creation fails
    """
    try:
        bgm_video = NewsSettings.CATEGORY_BGM.get(category, NewsSettings.DEFAULT_CATEGORY_BGM)
        input_video = PathSettings.get_video_path(bgm_video)
        final_video = PathSettings.get_final_video(category)

        print(f"🎬 Creating overlay video for {category}...")
        output = create_overlay_video(input_video, overlay_image, final_video)
        return output
    except Exception as e:
        print(f"❌ Error creating overlay video for {category}: {str(e)}")
        raise

def generate_article_audio(article: dict) -> str:
    """Generate audio from article using text-to-speech.

    Args:
        article (dict): Article dictionary containing title, description, and content

    Returns:
        str: Path to the generated audio file
    """
    # Extract article components
    title = article.get('title', '')
    description = article.get('description', '')
    content = article.get('content', '')

    if not title and not description and not content:
        raise ValueError("Article must contain at least one of: title, description, or content")

    # Combine text with appropriate pauses
    full_text = f"{title}. \n\n{description}. \n\n{content}"

    ssml_text = """
    <speak>
        <prosody rate="95%" volume="loud">
          {}
        </prosody>
    </speak>
    """.format(full_text)


    article_audio = convert_text_to_speech(text=ssml_text,
                                           voice_id="Joanna",
                                           engine="neural",
                                           text_type="ssml")
    if not article_audio:
        raise ValueError("Failed to generate audio from text.")

    play_audio(article_audio)
    return article_audio



def play_audio(article_audio) -> None:
    """
    Play the generated audio using playsound.
    Args:
        article_audio: The audio stream from the text-to-speech conversion
    """
    # Save the audio to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(article_audio['AudioStream'].read())
        tmpfile_path = tmpfile.name

    # Play the audio
    playsound(tmpfile_path)