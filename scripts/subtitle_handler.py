import os
import re
from datetime import datetime, timedelta

from langdetect import detect

from scripts.load_configs import load_configs
from scripts.paths import subtitles_dir

from scripts.logger import get_logger
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
    frame_timestamp = datetime(1900, 1, 1) + timedelta(
        seconds=frame_number
        / load_configs().get("episodes")[episode_num - 1]["img_fps"]
    )

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
            language_name = LANGUAGE_CODES.get(language_code, language_code)

            for block in subtitle_blocks:
                lines = block.strip().split("\n")
                if len(lines) >= 3:  # Verifica se o bloco tem formato válido
                    # Extrai os tempos de início e fim
                    time_line = lines[1]
                    start_str, end_str = time_line.split(" --> ")

                    start_time = datetime.strptime(
                        start_str.replace(",", "."), "%H:%M:%S.%f"
                    )
                    end_time = datetime.strptime(
                        end_str.replace(",", "."), "%H:%M:%S.%f"
                    )

                    if start_time >= frame_timestamp and end_time <= end_time:
                        # Junta todas as linhas de texto da legenda
                        subtitle_text = " ".join(lines[2:])
                        return f"[{language_name}] - {subtitle_text}"

        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def remove_tags(message: str) -> str:
    """Remove tags HTML e códigos de formatação da string."""
    # Remove códigos de formatação ASS/SSA entre chaves
    message = re.sub(r"{[^}]*}", "", message, flags=re.IGNORECASE)

    # Substitui \N e \n por espaço
    message = re.sub(r"\\[Nn]", " ", message)

    # Remove múltiplas quebras de linha
    message = re.sub(r"\\[N]+", " ", message)

    # Remove tags de idioma entre colchetes
    message = re.sub(r"\[[^\]]+\]", "", message)

    # Remove códigos de formatação ASS/SSA
    message = re.sub(r"\\[^}]+", "", message)

    # Remove espaços em branco duplos
    message = re.sub(r"\s+", " ", message).strip()

    return message

def extract_ass_subtitle(
    episode_num: int, frame_number: int, subtitle_file: str
) -> str:
    """Extrai o texto da legenda para um frame específico."""
    frame_timestamp = datetime(1900, 1, 1) + timedelta(
        seconds=frame_number
        / load_configs().get("episodes")[episode_num - 1]["img_fps"]
    )

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
                start_time = datetime.strptime(parts[1], "%H:%M:%S.%f")
                end_time = datetime.strptime(parts[2], "%H:%M:%S.%f")

                if start_time >= frame_timestamp and end_time <= end_time:
                    dialogue = remove_tags(dialogue.split(',,')[-1])
                    remove_tags
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

    for file in sorted(
        os.listdir(subtitle_dir), reverse=True
    ):  # reversed for English come first
        if file.endswith(".ass") or file.endswith(".ssa"):
            subtitle = extract_ass_subtitle(
                episode_num, frame_number, os.path.join(subtitle_dir, file)
            )
            if subtitle:
                message += "Subtitles:\n" + subtitle + "\n\n"
        else:
            subtitle = extract_srt_subtitle(
                episode_num, frame_number, os.path.join(subtitle_dir, file)
            )
            if subtitle:
                message += "Subtitles:\n" + subtitle + "\n\n"

    if not message:
        return None

    return message


def get_frame_timestamp(episode_number: int, frame_number: int) -> str:
    """Retorna o timestamp de um frame."""
    try:
        configs = load_configs()
        episodes = configs.get("episodes", [])
        
        if episode_number - 1 >= len(episodes):
            raise ValueError(f"Episódio {episode_number} não encontrado nas configurações.")
        
        img_fps = episodes[episode_number - 1].get("img_fps")
        
        if img_fps is None:
            raise ValueError(f"img_fps não encontrado para o episódio {episode_number}.")
        
        frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=frame_number / img_fps)

        hr, min, sec, ms = (
            frame_timestamp.hour,
            frame_timestamp.minute,
            frame_timestamp.second,
            frame_timestamp.microsecond // 10000,
        )
        return f"{hr}:{min:02d}:{sec:02d}:{ms:02d}"
    
    except Exception as e:
        logger.error(f"Erro ao obter o timestamp do frame: {e}", exc_info=True)
        return "0:00:00:00"
