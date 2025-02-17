import os
import re
from datetime import datetime, timedelta

from langdetect import detect

from scripts.load_configs import load_configs
from scripts.logger import get_logger
from scripts.paths import subtitles_dir

logger = get_logger(__name__)

LANGUAGE_CODES = {
    "en": "English",
    "pt": "Português",
    "es": "Español",
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
    "ms": "Bahasa Melayu (Malay)",
    "tl": "Tagalog (Filipino)",
    # add more language codes here
}


def extract_srt_subtitle(
    episode_num: int, frame_number: int, subtitle_file: str
) -> str:
    """Extrai o texto da legenda para um frame específico."""

    img_fps = load_configs().get("episodes").get(episode_num).get("img_fps")
    frame_timestamp_seconds = timestamp_to_seconds(frame_to_timestamp(episode_num, frame_number))

    try:
        with open(subtitle_file, "r", encoding="utf-8") as file:
            content = file.read()

            # Divide o conteúdo em blocos de legendas
            subtitle_blocks = content.strip().split("\n\n")

            # Concatena todos os textos das legendas para detecção do idioma
            subtitle_texts = " ".join(
                ["\n".join(block.split("\n")[2:]) for block in subtitle_blocks]
            )
            language_code = detect(subtitle_texts)
            language_name = LANGUAGE_CODES.get(language_code)

            for block in subtitle_blocks:
                lines = block.strip().split("\n")
                if len(lines) >= 3:  # Verifica se o bloco tem formato válido
                    # Extrai os tempos de início e fim
                    time_line = lines[1]
                    start_str, end_str = time_line.split(" --> ")

                    start_time_seconds = timestamp_to_seconds(start_str)
                    end_time_seconds = timestamp_to_seconds(end_str)

                    if start_time_seconds <= frame_timestamp_seconds <= end_time_seconds:
                        # Junta todas as linhas de texto da legenda
                        subtitle_text = " ".join(lines[2:])
                        return f"[{language_name}] - {subtitle_text}"

        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def remove_tags(message: str) -> str:

    PATTERNS = re.compile(
    r"""
    {\s*[^}]*\s*}    |  # Remove códigos de formatação ASS/SSA entre chaves
    \\[Nn]           |  # Substitui \N e \n por espaço
    \[[^\]]+\]       |  # Remove tags de idioma entre colchetes
    \\[^}]+          |  # Remove códigos de formatação ASS/SSA
    \s+                # Remove espaços extras
    """, re.VERBOSE
    )

    """Remove tags HTML e códigos de formatação da string."""
    return PATTERNS.sub(" ", message).strip()


def timestamp_to_seconds(time_str: str) -> float:
    """Convert HH:MM:SS.MS format to seconds"""
    h, m, s = map(float, time_str.split(":"))
    return h * 3600 + m * 60 + s

def frame_to_timestamp(episode_number: int, frame_number: int) -> str:
    
    configs = load_configs()
    img_fps: int | float = configs.get("episodes", {}).get(episode_number, {}).get("img_fps")

    if not img_fps:
        logger.error("Erro, img_fps não esta settado", exc_info=True)
        return "0:00:00.00"

    frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=frame_number / img_fps)

    hr, min, sec, ms = (
        frame_timestamp.hour, frame_timestamp.minute,
        frame_timestamp.second, frame_timestamp.microsecond // 10000
        )
    
    return f"{hr}:{min:02d}:{sec:02d}.{ms:02d}"


def extract_ass_subtitle(
    episode_number: int, frame_number: int, subtitle_file: str
) -> str:
    """Extrai o texto da legenda para um frame específico."""

    img_fps = load_configs().get("episodes").get(episode_number).get("img_fps")

    frame_timestamp_seconds = timestamp_to_seconds(frame_to_timestamp(episode_number, frame_number))

    try:
        with open(subtitle_file, "r", encoding="utf_8_sig") as file:
            content = file.read()
            dialogues = [
                line for line in content.split("\n") if line.startswith("Dialogue:")
            ]

            # Concatena todos os textos das legendas em uma única string para detecção
            subtitle_texts = " ".join([d.split(",,")[-1] for d in dialogues])
            language_code = detect(subtitle_texts)
            language_name = LANGUAGE_CODES.get(language_code, language_code)

            for dialogue in dialogues:
                parts = dialogue.split(",")
                start_time_seconds = timestamp_to_seconds(parts[1])
                end_time_seconds = timestamp_to_seconds(parts[2])

                if start_time_seconds <= frame_timestamp_seconds <= end_time_seconds:
                    dialogue = remove_tags(dialogue.split(",,")[-1])
                    subtitle = f"[{language_name}] - {dialogue}"

                    return subtitle
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_subtitle_message(episode_num: int, frame_number: int) -> str:
    """Extrai todas as legendas do episódio para um frame específico."""

    subtitle_dir = subtitles_dir / f"{episode_num:02d}"
    message = ""

    if not subtitle_dir.exists():
        return None

    if load_configs().get("posting").get("multi_language_subtitles"):
        for file in sorted(os.listdir(subtitle_dir), reverse=True):
            subtitle_file = subtitle_dir / file
            if subtitle_file.suffix == ".srt":
                subtitle_msg = extract_srt_subtitle(
                    episode_num, frame_number, subtitle_file
                )
            elif subtitle_file.suffix == ".ass":
                subtitle_msg = extract_ass_subtitle(
                    episode_num, frame_number, subtitle_file
                )

            if subtitle_msg:
                message += "Subtitle:\n" + subtitle_msg + "\n\n"

    else:
        subtitle_file = subtitle_dir / os.listdir(subtitle_dir)[0]

        if subtitle_file.suffix == ".srt":
            subtitle_msg = extract_srt_subtitle(
                episode_num, frame_number, subtitle_file
            )
        elif subtitle_file.suffix == ".ass":
            subtitle_msg = extract_ass_subtitle(
                episode_num, frame_number, subtitle_file
            )

        if subtitle_msg:
            message += "Subtitle:\n" + subtitle_msg + "\n\n"

    return message


