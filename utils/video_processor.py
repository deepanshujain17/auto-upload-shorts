from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
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

def create_overlay_video_output(category: str, article: dict, overlay_image: str) -> str:
    """
    Create an overlay video with the news card.
    Args:
        category (str): News category to process
        article (dict): News article
        overlay_image (str): Path to the overlay image

    Returns:
        str: Path to the final video
    Raises:
        Exception: If video creation fails
    """
    try:
        # Correct
        final_outcome_video = PathSettings.get_final_video(category)
        final_bg_video_path = PathSettings.get_bg_video(category)


        category_bg_image = NewsSettings.CATEGORY_BG_IMAGE.get(category, NewsSettings.CATEGORY_BG_IMAGE["default"])
        bg_image = PathSettings.get_image_path(category_bg_image)
        print(f"BGM image: {bg_image}")

        category_bg_music = NewsSettings.CATEGORY_BGM.get(category, NewsSettings.CATEGORY_BGM["default"])
        bg_music = PathSettings.get_music_path(category_bg_music)
        print(f"BGM music: {bg_music}")

        article_audio = generate_article_audio(article)
        print(f"Article audio: {article_audio}")

        # Create a video with the bg image, article audio and background music
        create_video_with_audio(
            image_path=bg_image,
            fg_audio_path=article_audio,
            bg_audio_path=bg_music,
            output_path=final_bg_video_path,
            fg_volume=1.0,
            bg_volume=0.1,
            fps=VideoSettings.FPS
        )

        print(f"🎬 Creating overlay video for {category}...")
        output = create_overlay_video(final_bg_video_path, overlay_image, final_outcome_video)
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

    return article_audio



def play_audio(article_audio) -> None:
    """
    Play the generated audio using playsound.
    Args:
        article_audio: The audio stream from the text-to-speech conversion
    """
    # Save the audio to a temporary file
    # import tempfile
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
    #     tmpfile.write(article_audio['AudioStream'].read())
    #     tmpfile_path = tmpfile.name
    #
    # # Play the audio
    # playsound(tmpfile_path)
    playsound(article_audio)


def create_video_with_audio(image_path: str,
                          fg_audio_path: str,
                          bg_audio_path: str,
                          output_path: str,
                          fg_volume: float = 1.0,
                          bg_volume: float = 0.1,
                          fps: int = 24) -> str:
    """
    Create a video by combining a static image with foreground and background audio tracks.

    Args:
        image_path (str): Path to the image file to use as video
        fg_audio_path (str): Path to the foreground audio file (e.g., speech)
        bg_audio_path (str): Path to the background audio file (e.g., music)
        output_path (str): Path where the output video will be saved
        fg_volume (float): Volume multiplier for foreground audio (default: 1.0)
        bg_volume (float): Volume multiplier for background audio (default: 0.2)
        fps (int): Frames per second for the output video (default: 24)
    """
    # Load the foreground audio and scale its volume
    fg_audio = AudioFileClip(fg_audio_path).with_volume_scaled(fg_volume)
    # Set the duration to match the foreground audio's duration
    duration = fg_audio.duration

    # Load the background audio and scale its volume
    bg_audio = AudioFileClip(bg_audio_path).with_volume_scaled(bg_volume).with_duration(duration)

    # Combine the foreground and background audio tracks
    combined_audio = CompositeAudioClip([fg_audio, bg_audio])

    # Create an image clip with the specified duration and fps
    image_clip = ImageClip(image_path).with_duration(duration).with_fps(fps)

    # Set the combined audio to the image clip
    video = image_clip.with_audio(combined_audio)

    # Write the final video to the output path
    video.write_videofile(output_path, fps=fps, audio_codec='aac')

    # Clean up resources
    fg_audio.close()
    bg_audio.close()
    combined_audio.close()
    image_clip.close()
    video.close()

    print(f"✅ Video created successfully: {output_path}")


