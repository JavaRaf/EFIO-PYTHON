from datetime import datetime
from datetime import timedelta
from utils.tools.logger import get_logger
import re
from pathlib import Path
from langdetect import detect


logger = get_logger(__name__)

LANGUAGE_CODES = {
    "en": "English",
    "pt": "Português",
    "es": "Español",
    "spa": "Español",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "ru": "Русский (Russian)",
    "tr": "Türkçe (Turkish)",
    "vi": "Tiếng Việt (Vietnamese)",
    "nl": "Nederlands (Dutch)",
    "uk": "Українська (Ukrainian)",
    "id": "Bahasa Indonesia (Indonesian)",
    "tl": "Tagalog (Filipino)",
    # add more language codes here
}


def remove_tags(message: str) -> str:
    """Remove tags ASS/SSA"""
    PATTERNS = re.compile(r"\{\s*[^}]*\s*\}|\\N|\\[^}]+")

    return PATTERNS.sub(" ", message).strip()


def timestamp_to_seconds(time_str: str) -> float:
    """Convert H:MM:SS.MS format to seconds"""
    h, m, s = map(float, time_str.split(":"))
    return h * 3600 + m * 60 + s


def frame_to_timestamp(img_fps: int | float, current_frame: int) -> str | None:
    """Convert frame number to timestamp"""

    if not isinstance(img_fps, (int, float)) or not isinstance(current_frame, int):
        logger.error("Error, img_fps or frame_number must be a number", exc_info=True)
        return None

    frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=current_frame / img_fps)

    hr, min, sec, ms = (
        frame_timestamp.hour,
        frame_timestamp.minute,
        frame_timestamp.second,
        frame_timestamp.microsecond // 10000,
    )

    return f"{hr}:{min:02d}:{sec:02d}.{ms:02d}"


def language_detect(file_path: Path, dialogues: list[str]) -> str:
    """Detects the language based on the dialogue content and renames the file."""
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return "Unknown"

    # Divide the file name into parts
    name_parts = file_path.stem.split(".")
    ext = file_path.suffix.lstrip(".")  # Remove the dot from the extension

    # If there is already a valid language code in the file name, use it
    if (
        len(name_parts) > 1
        and name_parts[-1] in LANGUAGE_CODES
        and not any(c.isdigit() for c in name_parts[-1])
    ):
        return LANGUAGE_CODES.get(name_parts[-1], "Unknown")

    # Detects the language of the extracted text
    lang_code = detect(" ".join(dialogues))
    language = LANGUAGE_CODES.get(lang_code, "Unknown")

    if language == "Unknown":
        print("Language detection failed. Keeping original filename.")
        return language

    # Generates a new file path with the detected language
    new_file_path = file_path.with_name(
        f"{file_path.stem.split('.')[0]}.{language}.{ext}"
    )

    try:
        if new_file_path.exists():
            return language

        file_path.rename(new_file_path)
        return language
    except Exception as e:
        logger.error(f"Error renaming file subtitle: {e}")
        return "Unknown"


def subtitle_ass(
    subtitle_file: str, current_frame: int, current_episode: int, configs: dict
) -> str | None:
    """
    Returns the subtitle message for the current frame.
    """

    img_fps = configs.get("episodes", {}).get(current_episode, {}).get("img_fps", 0)

    if not img_fps:
        logger.error(
            "Error, img_fps not set, please define img_fps in the configs.yml file",
            exc_info=True,
        )
        return None

    frame_in_seconds = timestamp_to_seconds(frame_to_timestamp(img_fps, current_frame))

    with open(subtitle_file, "r", encoding="utf-8_sig") as file:
        content = file.readlines()

    dialogues = [line for line in content if line.startswith("Dialogue:")]
    lang_name = language_detect(Path(subtitle_file), dialogues)
    subtitles = []

    for line in dialogues:
        parts = line.split(",")
        start_time_seconds = timestamp_to_seconds(parts[1])
        end_time_seconds = timestamp_to_seconds(parts[2])
        style = parts[3]  # Estilo (por exemplo, "Lyrics" ou "Signs")
        name = parts[4]  # Nome (opcional, usado em alguns casos)
        text = line.split(",,")[-1]  # O texto da legenda

        if start_time_seconds <= frame_in_seconds <= end_time_seconds:
            # Verifica se o estilo é relacionado a sinais (Signs)
            if re.match(r"(?i)^signs?", style) or re.match(r"(?i)^signs?", name):
                subtitle = f"【 {remove_tags(text)} 】"
                subtitles.append(subtitle + "\n")

            # Verifica se o estilo ou o nome é relacionado a letras de música (Lyrics ou Songs)
            elif re.search(r"(?i)lyrics?|songs?", style) or re.search(r"(?i)lyrics?|songs?", name):
                subtitle = f"♪ {remove_tags(text)} ♪\n"
                subtitles.append(subtitle)

            # Caso contrário, apenas adiciona o texto
            else:
                subtitle = remove_tags(text)
                subtitles.append(subtitle + "\n")
    if not subtitles:
        return None

    return f"[{lang_name}]\n {' '.join(subtitles)}"


def get_subtitle_message(
    current_frame: int, current_episode: int, configs: dict
) -> str | None:
    """
    Returns the subtitle message for the current frame.
    """

    if not isinstance(current_frame, int) or not isinstance(current_episode, int):
        logger.error(
            "Error, current_frame and current_episode must be integers", exc_info=True
        )
        return None

    subtitles_dir = Path(__file__).parent.parent.parent / "subtitles"
    subtitle_dir = subtitles_dir / f"{current_episode:02d}"

    if not subtitle_dir.exists():
        return None

    files = [f for f in subtitle_dir.iterdir() if f.is_file() and f.suffix == ".ass"]
    if not configs.get("posting", {}).get("multi_language_subtitles", False):
        files = [files[0]]

    message = ""

    for file in files:
        subtitle_file = subtitle_dir / file

        result = subtitle_ass(subtitle_file, current_frame, current_episode, configs)
        if result:
            message += result + "\n\n"

    return "𝑺𝒖𝒃𝒕𝒊𝒕𝒍𝒆𝒔:\n" + message if message else None
