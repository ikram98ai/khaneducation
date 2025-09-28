from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from tqdm import tqdm
from .utils import (
    client,
    MODEL_ID,
    image_generation,
    text_to_speech,
    create_mini_video,
    create_full_video,
    clean_filename
)
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LessonConcept(BaseModel):
    concept: str
    explanation: str  # Fixed typo: explaination -> explanation


class Lesson(BaseModel):
    lesson_concepts: List[LessonConcept]


class LessonInput(BaseModel):
    """Input parameters for lesson generation."""

    grade_level: str
    language: str
    subject: str
    topic: str
    focus_areas: Optional[List[str]] = None
    use_s3: bool = True  # Added S3 flag


def lesson_generation(lesson_input: LessonInput) -> Lesson:
    focus_instruction = ""
    if lesson_input.focus_areas:
        focus_instruction = f"\nFocus especially on these areas that need improvement: {', '.join(lesson_input.focus_areas)}"

    prompt = f"""
    Create a comprehensive lesson with 1 to 5 concepts and clear explanation for:
    - Grade Level: {lesson_input.grade_level}
    - Language: {lesson_input.language}
    - Subject: {lesson_input.subject}
    - Topic: {lesson_input.topic}
    {focus_instruction}
    
    Explane Lesson with: Clear learning objectives, Detailed explanation of key concepts, Examples and illustrations, and Summary of important points

    Output Structure:
        lesson_concepts: [
            concept: str 
            explanation: str  # Fixed typo
        ]

    Make it age-appropriate and engaging for the grade level.
    Respond in {lesson_input.language}.
    """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Lesson,
        },
    )
    return response.parsed


def images_generation(
    lesson: Lesson, topic: str, use_s3: bool = True
) -> Dict[str, Dict[str, any]]:
    """Generate images for each lesson concept."""
    images_explanation = {}  # Fixed variable name
    for lesson_concept in tqdm(lesson.lesson_concepts):
        try:
            paths = image_generation(lesson_concept, topic, use_s3)
            images_explanation[lesson_concept.concept] = {  # Using concept as key
                "images_paths": paths,
                "explanation": lesson_concept.explanation,  # Fixed typo
            }
        except Exception as e:
            logger.error(
                f"Error in generating images for {lesson_concept.concept[:100]}; ERROR: {str(e)}"
            )
            break
    return images_explanation


def generate_mini_videos(
    images_explanation: Dict[str, Dict[str, any]], topic: str, use_s3: bool = True
) -> List[str]:
    """Generate mini videos for each concept."""
    mini_video_paths = []

    for i, (concept, img_exp) in tqdm(enumerate(images_explanation.items())):
        try:
            # Generate audio

            text = concept + "\n" + img_exp["explanation"]
            concept = clean_filename(concept)

            audio_filename = f"{concept}_{i}"
            audio_path = text_to_speech(text, audio_filename, topic, use_s3)

            # Generate video
            video_filename = f"{concept}_{i}"
            mini_video_path = create_mini_video(
                img_exp["images_paths"], audio_path, video_filename, topic, use_s3
            )
            mini_video_paths.append(mini_video_path)
        except Exception as e:
            logger.error(
                f"There is an error in creating mini videos for {concept}; ERROR{str(e)}"
            )
            continue

    return mini_video_paths


def create_lesson_video(lesson_input: LessonInput):
    """Main function to create a complete lesson video."""
    lesson = lesson_generation(lesson_input)
    logger.info(f"{len(lesson.lesson_concepts)} lesson concepts: {", ".join(con.concept for con in lesson.lesson_concepts)}")
    images_explanation = images_generation(
        lesson, lesson_input.topic, lesson_input.use_s3
    )
    mini_video_paths = generate_mini_videos(
        images_explanation, lesson_input.topic, lesson_input.use_s3
    )

    # Create final video
    final_video_name = f"{clean_filename(lesson_input.topic)}_{uuid.uuid4().hex[:8]}"
    full_video_path = create_full_video(
        mini_video_paths, final_video_name, lesson_input.use_s3
    )

    return {"lesson": lesson, "full_video": full_video_path}
