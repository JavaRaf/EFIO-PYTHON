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


def remove_tags(message: str) -> str:
    """Remove tags HTML e códigos de formatação da string."""

    PATTERNS = re.compile(
    r"""
        {\s*[^}]*\s*}    |  # Remove códigos de formatação ASS/SSA entre chaves
        \\[Nn]           |  # Substitui \N e \n por espaço
        \[[^\]]+\]       |  # Remove tags de idioma entre colchetes
        \\[^}]+          |  # Remove códigos de formatação ASS/SSA
    """,
        re.VERBOSE,
    )

    return PATTERNS.sub(" ", message).strip()


def timestamp_to_seconds(time_str: str) -> float:
    """Convert H:MM:SS.MS format to seconds"""
    h, m, s = map(float, time_str.split(":"))
    return h * 3600 + m * 60 + s


def frame_to_timestamp(episode_number: int, frame_number: int) -> str:

    configs = load_configs()
    img_fps: int | float = (
        configs.get("episodes", {}).get(episode_number, {}).get("img_fps")
    )

    if not img_fps:
        logger.error("Erro, img_fps não esta settado", exc_info=True)
        return "0:00:00.00"

    frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=frame_number / img_fps)

    hr, min, sec, ms = (
        frame_timestamp.hour,
        frame_timestamp.minute,
        frame_timestamp.second,
        frame_timestamp.microsecond // 10000,
    )

    return f"{hr}:{min:02d}:{sec:02d}.{ms:02d}"


def subtitle_srt(episode_number: int, frame_number: int, subtitle_file: str) -> str:
    pass


def subtitle_ass(
    episode_number: int, frame_number: int, subtitle_file: str
) -> tuple[str, str]:

    with open(subtitle_file, "r", encoding="utf-8_sig") as file:
        content = file.readlines()

    dialogues = [line for line in content if line.startswith("Dialogue:")]

    # Cria a lista temporária para armazenar os textos das legendas
    temporary_subtitles = [remove_tags(d.split(",,")[-1]) for d in dialogues]
    lang_code = detect(" ".join(temporary_subtitles))
    lang_name = LANGUAGE_CODES.get(lang_code, lang_code)

    frame_in_seconds = timestamp_to_seconds(
        frame_to_timestamp(episode_number, frame_number)
    )
    subtitles = []

    # [0] layer
    # [1] start
    # [2] end
    # [3] style
    # [4] name
    # [5] marginL
    # [6] marginR
    # [7] marginV
    # [8] effect
    # [9] text or [-1]

    for line in dialogues:
        parts = line.split(",")
        start_time_seconds = timestamp_to_seconds(parts[1])
        end_time_seconds = timestamp_to_seconds(parts[2])
        style = parts[3]  # Estilo (por exemplo, "Lyrics" ou "Signs")
        name = parts[4]  # Nome (opcional, usado em alguns casos)
        text = line.split(",,")[-1]  # O texto da legenda

        if start_time_seconds <= frame_in_seconds <= end_time_seconds:
            # Verifica se o estilo é relacionado a sinais (Signs)
            if re.search(r"\bsigns?\b", style, re.IGNORECASE):
                subtitles.append(f"【 {remove_tags(text)} 】\n")
            
            # Verifica se o estilo ou o nome é relacionado a letras de música (Lyrics ou Songs)
            elif re.search(r"\b(lyrics?|songs?)\b", style, re.IGNORECASE) or re.search(r"\b(lyrics?|songs?)\b", name, re.IGNORECASE):
                subtitles.append(f"♪ {remove_tags(text)} ♪\n")  # Adiciona um estilo especial para letras de música
            
            # Caso contrário, apenas adiciona o texto
            else:
                subtitles.append(remove_tags(text))

    if not subtitles:
        return None, None

    return (
        f"[{lang_name}]\n {' '.join(subtitles)}",
        f"{frame_to_timestamp(episode_number, frame_number)}",
    )



def get_subtitle_message(
    episode_number: int, frame_number: int
) -> tuple[str, str] | None:
    """
    Retorna o texto da legenda para um frame específico e o timestamp.
    """

    subtitle_dir = subtitles_dir / f"{episode_number:02d}"

    if not subtitle_dir.exists():
        return None

    files = os.listdir(subtitle_dir)

    if not load_configs().get("posting", {}).get("multi_language_subtitles", False):
        files = [files[0]]

    message = ""

    for file in files:
        subtitle_file = subtitle_dir / file

        if subtitle_file.suffix == ".ass":
            result = subtitle_ass(episode_number, frame_number, subtitle_file)
            if result:
                subtitle_msg, frame_timestamp = result

        elif subtitle_file.suffix == ".srt":
            result = subtitle_srt(episode_number, frame_number, subtitle_file)
            if result:
                subtitle_msg, frame_timestamp = result

        if "subtitle_msg" in locals() and subtitle_msg:
            message += subtitle_msg + "\n\n"

    if not message:
        return None, None

    return "𝑺𝒖𝒃𝒕𝒊𝒕𝒍𝒆𝒔:\n" + message, frame_timestamp
