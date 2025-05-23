from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from settings import VideoSettings, NewsSettings, PathSettings
from utils.media_utils.audio_utils import convert_text_to_speech
from pathlib import Path
import contextlib


def generate_article_audio(article: dict, output_path: str = None) -> str:
    """Generate audio from article using text-to-speech.

    Args:
        article (dict): Article dictionary containing title, description, and content
        output_path (str, optional): Custom path to save the audio file

    Returns:
        str: Path to the generated audio file

    Raises:
        ValueError: If article has no content or audio generation fails
    """
    # Extract and validate article components
    title = article.get('title', '').strip()
    description = article.get('description', '').strip()
    content = article.get('content', '').strip()

    if not any([title, description, content]):
        raise ValueError("Article must contain at least one of: title, description, or content")

    # Combine text with appropriate pauses and SSML formatting
    text_parts = []
    if title:
        text_parts.append(title)
    if description:
        text_parts.append(description)
    if content:
        text_parts.append(content)

    ssml_text = f"""
    <speak>
        <prosody rate="95%" volume="loud">
            {". ".join(text_parts)}
        </prosody>
    </speak>
    """

    return convert_text_to_speech(
        text=ssml_text,
        output_filename=output_path,
        voice_id="Joanna",
        engine="neural",
        text_type="ssml"
    )


def create_video_with_audio(image_path: str,
                          fg_audio_path: str,
                          bg_audio_path: str,
                          output_path: str,
                          fg_volume: float = 1.0,
                          bg_volume: float = 0.1,
                          fps: int = 24) -> str:
    """Create a video by combining a static image with foreground and background audio.

    Args:
        image_path (str): Path to the image file to use as video
        fg_audio_path (str): Path to the foreground audio file (e.g., speech)
        bg_audio_path (str): Path to the background audio file (e.g., music)
        output_path (str): Path where the output video will be saved
        fg_volume (float): Volume multiplier for foreground audio (default: 1.0)
        bg_volume (float): Volume multiplier for background audio (default: 0.1)
        fps (int): Frames per second for the output video (default: 24)

    Returns:
        str: Path to the generated video file

    Raises:
        FileNotFoundError: If any input files are missing
        ValueError: If invalid parameters are provided
    """
    # Validate input files
    for file_path in [image_path, fg_audio_path, bg_audio_path]:
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Input file not found: {file_path}")

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Use context managers for proper resource cleanup
    with contextlib.ExitStack() as stack:
        # Load and configure audio clips
        fg_audio = stack.enter_context(AudioFileClip(fg_audio_path).with_volume_scaled(fg_volume))
        duration = fg_audio.duration

        bg_audio = stack.enter_context(
            AudioFileClip(bg_audio_path)
            .with_volume_scaled(bg_volume)
            .with_duration(duration)
        )

        # Create combined audio
        combined_audio = stack.enter_context(CompositeAudioClip([fg_audio, bg_audio]))

        # Create image-based video
        image_clip = stack.enter_context(
            ImageClip(image_path)
            .with_duration(duration)
            .with_fps(fps)
        )

        # Combine video and audio
        video = stack.enter_context(image_clip.with_audio(combined_audio))

        # Write final video
        video.write_videofile(
            output_path,
            fps=fps,
            audio_codec='aac',
            logger=None
        )

    print(f"✅ Video created successfully: {output_path}")
    return output_path


def create_overlay_video(video_path: str, image_path: str, output_path: str = None) -> str:
    """Create a video with an image overlay.

    Args:
        video_path (str): Path to the input video file
        image_path (str): Path to the overlay image file
        output_path (str, optional): Path where the output video will be saved

    Returns:
        str: Path to the output video file

    Raises:
        FileNotFoundError: If input files are missing
        ValueError: If video processing fails
    """
    # Validate input files
    for file_path in [video_path, image_path]:
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Input file not found: {file_path}")

    # Use default output path if none provided
    if output_path is None:
        output_path = str(Path(video_path).parent / "output_with_overlay.mp4")

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with contextlib.ExitStack() as stack:
        # Load video and create image overlay
        video = stack.enter_context(VideoFileClip(video_path))
        image = stack.enter_context(
            ImageClip(image_path)
            .with_duration(video.duration)
            .resized(height=VideoSettings.IMAGE_HEIGHT)
            .with_position(("center", video.h // 2 - VideoSettings.IMAGE_VERTICAL_OFFSET))
        )

        # Combine video and overlay
        final = stack.enter_context(CompositeVideoClip([video, image]))

        # Write final video
        final.write_videofile(
            output_path,
            codec=VideoSettings.VIDEO_CODEC,
            audio_codec=VideoSettings.AUDIO_CODEC,
            logger=None
        )

    print(f"✅ Overlay video created successfully: {output_path}")
    return output_path


def create_overlay_video_output(category: str, article: dict, overlay_image: str) -> str:
    """Create a complete video with news overlay and audio.

    Args:
        category (str): News category to process
        article (dict): News article data
        overlay_image (str): Path to the overlay image

    Returns:
        str: Path to the final video

    Raises:
        ValueError: If category is invalid or required assets are missing
        FileNotFoundError: If required files are missing
    """
    try:
        # Get paths for output files
        final_outcome_video = PathSettings.get_final_video(category)
        final_bg_video_path = PathSettings.get_bg_video(category)

        # Get background assets
        category_bg_image = NewsSettings.CATEGORY_BG_IMAGE.get(category, NewsSettings.CATEGORY_BG_IMAGE["default"])
        bg_image = PathSettings.get_image_path(category_bg_image)
        print(f"📸 Using background image: {bg_image}")

        category_bg_music = NewsSettings.CATEGORY_BGM.get(category, NewsSettings.CATEGORY_BGM["default"])
        bg_music = PathSettings.get_music_path(category_bg_music)
        print(f"🎵 Using background music: {bg_music}")

        # Generate article audio
        article_audio = generate_article_audio(article)
        print(f"🎙️ Generated article audio: {article_audio}")

        # Create video with background image and audio
        print(f"🎬 Creating base video for {category}...")
        create_video_with_audio(
            image_path=bg_image,
            fg_audio_path=article_audio,
            bg_audio_path=bg_music,
            output_path=final_bg_video_path,
            fg_volume=1.0,
            bg_volume=0.1,
            fps=VideoSettings.FPS
        )

        # Add overlay to the video
        print(f"🎨 Adding overlay to video for {category}...")
        output = create_overlay_video(final_bg_video_path, overlay_image, final_outcome_video)

        print(f"✅ Final video created successfully: {output}")
        return output

    except Exception as e:
        print(f"❌ Error creating video for {category}: {str(e)}")
        raise

