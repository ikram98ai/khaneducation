from typing import List
from google import genai
from google.genai import types
import os
from pathlib import Path
import wave
import boto3
from botocore.exceptions import ClientError
from ..config import settings
import tempfile
from moviepy import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips
import logging
import re
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


S3_BUCKET = "aitutor-files-1234"
MODEL_ID = "gemini-2.5-flash"
IMAGE_MODEL_ID = "gemini-2.5-flash-image-preview"
AUDIO_MODEL_ID = "gemini-2.5-flash-preview-tts"
GOOGLE_API_KEY = settings.gemini_api_key

client = genai.Client(api_key=GOOGLE_API_KEY)
s3_client = boto3.client("s3")

def clean_filename(filename:str):
    filename = filename[:100]
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9\_]", "", filename)
    filename = re.sub(r"_+", "_", filename)
    return filename.strip("_")

def upload_to_s3(file_path: str, s3_key: str) -> str:
    """Upload a file to S3 bucket and return the URL."""
    try:
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
        logger.info(f"Uploaded {file_path} to S3: {url}")
        return url
    except ClientError as e:
        logger.error(f"Error uploading to S3: {e}")
        raise


def save_image(response, concept: str, topic: str, use_s3: bool = True) -> List[str]:
    """Save images locally or to S3."""
    image_paths = []
    concept = clean_filename(concept)
    # Create a temporary directory if using S3
    if use_s3:
        temp_dir = tempfile.mkdtemp()
        image_dir = temp_dir
    else:
        Path("images").mkdir(exist_ok=True)
        Path(f"images/{topic}").mkdir(exist_ok=True)

        image_dir = f"images/{topic}/{concept.replace(' ', '_')}"
        Path(image_dir).mkdir(exist_ok=True)

    for i, part in enumerate(response.parts):
        if image := part.as_image():
            image_name = f"{concept.replace(' ', '_')}_{i}.png"
            local_path = os.path.join(image_dir, image_name)
            image.save(local_path)

            if use_s3:
                s3_key = f"images/{topic}/{image_name}"
                s3_url = upload_to_s3(local_path, s3_key)
                image_paths.append(s3_url)
                # Clean up local file after upload
                os.remove(local_path)
            else:
                image_paths.append(local_path)

    # Clean up temp directory if using S3
    if use_s3:
        os.rmdir(image_dir)

    return image_paths


def image_generation(lesson_concept, topic: str, use_s3: bool = True) -> List[str]:
    """Generate an image based on the given prompt."""
    prompt = f"""
    Create clear, educational whiteboard-style illustrations showing: {lesson_concept.concept}

    Context: {lesson_concept.explanation}
    
    Style requirements:
    - Clean white background like a classroom whiteboard
    - Simple, clear diagrams with labels
    - Educational and professional appearance
    - Easy to understand for students
    - Include text labels and explanations

    NOTE: Create atleast one image for given concept, it would be nice if you generate upto 5 images to illustrate the concept.
    """

    response = client.models.generate_content(
        model=IMAGE_MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["Image"]),
    )
    return save_image(response, lesson_concept.concept, topic, use_s3)


def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Create a wave file from PCM data."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


def text_to_speech(text: str, filename: str, topic: str, use_s3: bool = True) -> str:
    """Convert text to speech and save locally or to S3."""
    response = client.models.generate_content(
        model=AUDIO_MODEL_ID,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Charon",
                    )
                )
            ),
        ),
    )

    data = response.candidates[0].content.parts[0].inline_data.data

    if use_s3:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            wave_file(temp_file.name, data)
            temp_path = temp_file.name

        # Upload to S3
        s3_key = f"audioes/{topic}/{filename}.wav"
        s3_url = upload_to_s3(temp_path, s3_key)

        # Clean up
        os.remove(temp_path)
        return s3_url
    else:
        # Save locally
        Path("audioes").mkdir(exist_ok=True)
        Path(f"audioes/{topic}").mkdir(exist_ok=True)
        file_path = f"audioes/{topic}/{filename}.wav"
        wave_file(file_path, data)
        return file_path


def create_mini_video(
    img_paths: List[str],
    audio_path: str,
    output_name: str,
    topic: str,
    use_s3: bool = True,
) -> str:
    """Create a mini video from images and audio."""
    # Download files from S3 if needed
    if use_s3 and img_paths and img_paths[0].startswith("http"):
        # Implementation for downloading from S3 would go here
        # For simplicity, we'll assume the function receives local paths
        pass

    # Load audio clip
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration

    # Calculate duration for each image
    num_images = len(img_paths)
    image_duration = audio_duration / num_images if num_images > 0 else 0

    # Create video clips from images
    video_clips = []
    for img_path in img_paths:
        clip = ImageClip(img_path).with_duration(image_duration)
        video_clips.append(clip)

    # Concatenate clips and add audio
    final_clip = concatenate_videoclips(video_clips)
    final_clip = final_clip.with_audio(audio_clip)

    # Export video
    if use_s3:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            final_clip.write_videofile(temp_file.name, fps=24)
            temp_path = temp_file.name

        # Upload to S3
        s3_key = f"videos/{topic}/{output_name}.mp4"
        s3_url = upload_to_s3(temp_path, s3_key)

        # Clean up
        os.remove(temp_path)
        return s3_url
    else:
        Path("videos").mkdir(exist_ok=True)
        Path(f"videos/{topic}").mkdir(exist_ok=True)

        output_path = f"videos/{topic}/{output_name}.mp4"
        final_clip.write_videofile(output_path, fps=24)
        return output_path


def create_full_video(
    mini_video_paths: List[str], output_name: str, use_s3: bool = True
) -> str:
    """Create a full video by concatenating mini videos."""
    # Download files from S3 if needed
    if use_s3 and mini_video_paths and mini_video_paths[0].startswith("http"):
        # Implementation for downloading from S3 would go here
        pass

    # Load video clips
    video_clips = [VideoFileClip(path) for path in mini_video_paths]

    # Concatenate clips
    final_clip = concatenate_videoclips(video_clips)

    # Export video
    if use_s3:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            final_clip.write_videofile(temp_file.name, fps=24)
            temp_path = temp_file.name

        # Upload to S3
        s3_key = f"videos/{output_name}.mp4"
        s3_url = upload_to_s3(temp_path, s3_key)

        # Clean up
        os.remove(temp_path)
        return s3_url
    else:
        Path("videos").mkdir(exist_ok=True)
        output_path = f"videos/{output_name}.mp4"
        final_clip.write_videofile(output_path, fps=24)
        return output_path
