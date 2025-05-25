from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from settings import VideoSettings, NewsSettings, PathSettings
from utils.media_utils.audio_utils import convert_text_to_speech
from pathlib import Path
from moviepy.audio.AudioClip import AudioArrayClip

def generate_article_audio(article: dict) -> AudioArrayClip:
    """Generate audio from article using text-to-speech.

    Args:
        article (dict): Article dictionary containing title, description, and content

    Returns:
        AudioArrayClip: Audio clip generated from article text

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

    # Get audio clip directly
    return convert_text_to_speech(
        text=ssml_text,
        voice_id="Joanna",
        engine="neural",
        text_type="ssml"
    )

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
        # Get output path
        final_video = PathSettings.get_final_video(category)

        # Get background assets
        bg_image = PathSettings.get_image_path(
            NewsSettings.CATEGORY_BG_IMAGE.get(category, NewsSettings.CATEGORY_BG_IMAGE["default"])
        )
        bg_music = PathSettings.get_music_path(
            NewsSettings.CATEGORY_BGM.get(category, NewsSettings.CATEGORY_BGM["default"])
        )
        print(f"📸 Using background: {bg_image}")
        print(f"🎵 Using music: {bg_music}")

        # Generate article audio
        print("🎙️ Generating audio from article...")
        speech_audio = generate_article_audio(article)
        duration = speech_audio.duration

        # Validate input files
        for path in [bg_image, bg_music, overlay_image]:
            if not Path(path).is_file():
                raise FileNotFoundError(f"Required file not found: {path}")

        # Ensure output directory exists
        Path(final_video).parent.mkdir(parents=True, exist_ok=True)

        # Create video with all components in one step
        with AudioFileClip(bg_music) as music_audio, \
             ImageClip(bg_image) as bg_clip, \
             ImageClip(overlay_image) as overlay_clip:

            # Configure audio
            speech_audio = speech_audio.with_volume_scaled(1.0)
            music_audio = music_audio.with_volume_scaled(0.1).with_duration(duration)
            combined_audio = CompositeAudioClip([speech_audio, music_audio])

            # Configure video clips
            bg_clip = bg_clip.with_duration(duration).with_fps(VideoSettings.FPS)
            overlay_clip = (overlay_clip
                          .with_duration(duration)
                          .resized(height=VideoSettings.IMAGE_HEIGHT)
                          .with_position(("center", bg_clip.h // 2 - VideoSettings.IMAGE_VERTICAL_OFFSET)))

            # Combine everything
            final = CompositeVideoClip([bg_clip, overlay_clip]).with_audio(combined_audio).with_duration(duration)
            final.write_videofile(
                final_video,
                fps=VideoSettings.FPS,
                codec=VideoSettings.VIDEO_CODEC,
                audio_codec=VideoSettings.AUDIO_CODEC,
                logger=None
            )

        print(f"✅ Video created successfully: {final_video}")
        return final_video

    except Exception as e:
        print(f"❌ Error creating video for {category}: {str(e)}")
        raise

