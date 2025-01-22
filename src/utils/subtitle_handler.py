from datetime import datetime, timedelta
import os
from langdetect import detect

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
    'ar': 'العربية (Arabic)',
    'hi': 'हिंदी (Hindi)',
    'bn': 'বাংলা (Bengali)',
    'ur': 'اردو (Urdu)',
    'tr': 'Türkçe (Turkish)',
    'vi': 'Tiếng Việt (Vietnamese)',
    'th': 'ภาษาไทย (Thai)',
    'nl': 'Nederlands (Dutch)',
    'sv': 'Svenska (Swedish)',
    'no': 'Norsk (Norwegian)',
    'da': 'Dansk (Danish)',
    'fi': 'Suomi (Finnish)',
    'pl': 'Polski (Polish)',
    'uk': 'Українська (Ukrainian)',
    'el': 'Ελληνικά (Greek)',
    'hu': 'Magyar (Hungarian)',
    'cs': 'Čeština (Czech)',
    'ro': 'Română (Romanian)',
    'sk': 'Slovenčina (Slovak)',
    'he': 'עברית (Hebrew)',
    'id': 'Bahasa Indonesia (Indonesian)',
    'ms': 'Bahasa Melayu (Malay)',
    'fa': 'فارسی (Persian)',
    'tl': 'Tagalog (Filipino)',
    'sw': 'Kiswahili (Swahili)',
    'am': 'አማርኛ (Amharic)',
    'et': 'Eesti (Estonian)',
    'lt': 'Lietuvių (Lithuanian)',
    'lv': 'Latviešu (Latvian)',
    'bg': 'Български (Bulgarian)',
    'sr': 'Српски (Serbian)',
    'hr': 'Hrvatski (Croatian)',
    'sl': 'Slovenščina (Slovenian)',
    'is': 'Íslenska (Icelandic)',
    'mt': 'Malti (Maltese)',
    'ga': 'Gaeilge (Irish)',
    'cy': 'Cymraeg (Welsh)',
    # Adicione mais idiomas conforme necessário
}


def extract_subtitle_text_for_frame(frame_number: int, subtitle_file: str, config: dict) -> str:
    """Extrai o texto da legenda para um frame específico."""

    img_fps = config["episodes"][config["current_episode"] - 1]["img_fps"]
    frame_timestamp = datetime(1900, 1, 1) + timedelta(seconds=frame_number / img_fps)
    
    try:
        with open(subtitle_file, "r", encoding="utf_8_sig") as file:
            content = file.read()
            language_code = detect(content)
            language_name = LANGUAGE_CODES.get(language_code, language_code)
            
            for line in content.split('\n'):
                if not line.startswith("Dialogue:"): continue
                
                parts = line.split(",")
                start_time = datetime.strptime(parts[1], "%H:%M:%S.%f")
                end_time = datetime.strptime(parts[2], "%H:%M:%S.%f")
                
                if start_time <= frame_timestamp <= end_time:
                    return f"--- {language_name} --->\n {line.split(',,')[-1]}"
    except Exception as e:
        print(f"Error: {e}")
    return None

def extract_all_subtitles(frame_number: int, config: dict) -> list:
    """Extrai todas as legendas do episódio para um frame específico."""

    subtitle_dir = f"episodes/subtitles/{config['current_episode']:02d}"
    return [
        text for file in os.listdir(subtitle_dir)
        if (text := extract_subtitle_text_for_frame(
            frame_number,
            os.path.join(subtitle_dir, file),
            config
        ))
    ]
