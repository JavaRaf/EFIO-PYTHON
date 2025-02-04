import os
import re
from scripts.paths import subtitles_dir
from datetime import datetime, timedelta
from langdetect import detect
from scripts.load_configs import load_configs


LANGUAGE_CODES = {
    'en': 'English',
    'pt': 'Português',
    'es': 'Español',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'ru': 'Русский (Russian)',
    'hi': 'हिंदी (Hindi)',
    'bn': 'বাংলা (Bengali)',
    'tr': 'Türkçe (Turkish)',
    'vi': 'Tiếng Việt (Vietnamese)',
    'nl': 'Nederlands (Dutch)',
    'uk': 'Українська (Ukrainian)',
    'id': 'Bahasa Indonesia (Indonesian)',
    'ms': 'Bahasa Melayu (Malay)',
    'tl': 'Tagalog (Filipino)',

    # Adicione mais idiomas conforme necessário
}


def extract_srt_subtitle(episode_num: int, frame_number: int, subtitle_file: str) -> str:
    """Extrai o texto da legenda para um frame específico."""
    frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=frame_number / load_configs().get("episodes")[episode_num - 1]["img_fps"])
    

    try:
        with open(subtitle_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Divide o conteúdo em blocos de legendas
            subtitle_blocks = content.strip().split('\n\n')
            
            # Concatena todos os textos das legendas para detecção do idioma
            subtitle_texts = ' '.join(['\n'.join(block.split('\n')[2:]) for block in subtitle_blocks])
            language_code = detect(subtitle_texts)
            language_name = LANGUAGE_CODES.get(language_code, language_code)
            
            for block in subtitle_blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:  # Verifica se o bloco tem formato válido
                    # Extrai os tempos de início e fim
                    time_line = lines[1]
                    start_str, end_str = time_line.split(' --> ')
                    
                    start_time = datetime.strptime(start_str.replace(',', '.'), '%H:%M:%S.%f')
                    end_time = datetime.strptime(end_str.replace(',', '.'), '%H:%M:%S.%f')
                    
                    if start_time >= frame_timestamp and end_time <= end_time:
                        # Junta todas as linhas de texto da legenda
                        subtitle_text = ' '.join(lines[2:])
                        return f"[{language_name}] - {subtitle_text}"
                        
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_ass_subtitle(episode_num: int, frame_number: int, subtitle_file: str) -> str:
    """Extrai o texto da legenda para um frame específico."""
    frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=frame_number / load_configs().get("episodes")[episode_num - 1]["img_fps"])
    
    try:
        with open(subtitle_file, "r", encoding="utf_8_sig") as file:
            content = file.read()
            dialogues = [line for line in content.split('\n') if line.startswith("Dialogue:")]
            
            # Concatena todos os textos das legendas em uma única string para detecção
            subtitle_texts = ' '.join([d.split(',,')[-1] for d in dialogues])
            language_code = detect(subtitle_texts)
            language_name = LANGUAGE_CODES.get(language_code, language_code)
            
            for dialogue in dialogues:
                parts = dialogue.split(",")
                start_time = datetime.strptime(parts[1], "%H:%M:%S.%f")
                end_time = datetime.strptime(parts[2], "%H:%M:%S.%f")

                if start_time >= frame_timestamp and end_time <= end_time:
                    subtitle = f"[{language_name}] - {dialogue.split(',,')[-1]}"
                    
                    return subtitle     
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_subtitle_message(episode_num: int, frame_number: int) -> str:
    """Extrai todas as legendas do episódio para um frame específico."""

    subtitle_dir = subtitles_dir / f"{episode_num:02d}"
    message = ""
    
    for file in sorted(os.listdir(subtitle_dir), reverse=True): # reversed for English come first
        if file.endswith(".ass") or file.endswith(".ssa"):  
            subtitle = extract_ass_subtitle(episode_num, frame_number, os.path.join(subtitle_dir, file))
            if subtitle:
                message += "Subtitles:\n" + subtitle + "\n\n"
        else:
            subtitle = extract_srt_subtitle(episode_num, frame_number, os.path.join(subtitle_dir, file))
            if subtitle:
                message += "Subtitles:\n" + subtitle + "\n\n"

    if not message:
        return None
    

    # Remove códigos de formatação ASS/SSA entre chaves
    message = re.sub(r'{[^}]*}', '', message, flags=re.IGNORECASE)

    # Substitui \N e \n por espaço
    message = re.sub(r'\\[N]', ' ', message)

    # Remove múltiplas quebras de linha
    message = re.sub(r'\\[N]+', ' ', message)

    # Remove tags de idioma entre colchetes
    message = re.sub(r'\[[^\]]+\]', ' ', message)

    return message
        

def get_frame_timestamp(episode_num: int, frame_number: int) -> str:
    frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=frame_number / load_configs().get("episodes")[episode_num - 1]["img_fps"])
    
    hr, min, sec, ms = frame_timestamp.hour, frame_timestamp.minute, frame_timestamp.second, frame_timestamp.microsecond // 10000
    return f"{hr:01d}:{min:02d}:{sec:02d}:{ms:02d}"
