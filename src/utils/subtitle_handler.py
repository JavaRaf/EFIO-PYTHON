from datetime import datetime, timedelta
import os

def extract_subtitle_text_for_frame(frame_number: int, subtitle_file: str, config: dict) -> str:
    """
    Extrai o texto da legenda correspondente a um frame específico.
    
    Args:
        frame_number: Número do frame
        subtitle_file: Caminho do arquivo de legendas
        config: Dicionário de configuração
        
    Returns:
        str: Texto da legenda correspondente ao frame, ou None se não encontrado
    """
    # Converte o frame para timestamp
    img_fps = config.get("episodes")[config.get("current_episode")].get("img_fps")
    frame_timestamp = datetime(1900, 1, 1, 0, 0, 0, 0) + timedelta(seconds=frame_number / img_fps)
    
    try:
        with open(subtitle_file, "r", encoding="utf_8_sig") as file:
            for line in file:
                if line.startswith("Dialogue:"):
                    start_time, end_time = line.split(",")[1:3]
                    start_time = datetime.strptime(start_time, "%H:%M:%S.%f")
                    end_time = datetime.strptime(end_time, "%H:%M:%S.%f")
                    if frame_timestamp >= start_time and frame_timestamp <= end_time:
                        return line.split(",,")[-1]
    except Exception as e:
        print(f"Error: {e}")
        return None

def combine_episode_subtitles(frame_number: int, config: dict) -> str:
    """
    Combina as legendas primária e secundária do episódio.
    
    Args:
        frame_number: Número do frame
        config: Dicionário de configuração
        
    Returns:
        str: Texto combinado das legendas
    """
    subtitle_message = ""
    secondary_subtitle_file = None  # Inicializa a variável como None
    
    subtitle_file = os.listdir(f"episodes/subtitles/{config.get('current_episode'):02d}")
    
    if len(subtitle_file) == 2:
        primary_subtitle_file = os.path.join("episodes/subtitles", f"{config.get('current_episode'):02d}", subtitle_file[0])
        secondary_subtitle_file = os.path.join("episodes/subtitles", f"{config.get('current_episode'):02d}", subtitle_file[1])
    else:
        primary_subtitle_file = os.path.join("episodes/subtitles", f"{config.get('current_episode'):02d}", subtitle_file[0])
        
    if primary_subtitle_file:
        primary_text = extract_subtitle_text_for_frame(frame_number, primary_subtitle_file, config=config)
        if primary_text:  # Verifica se o texto não é None
            subtitle_message = primary_text

    if secondary_subtitle_file:  # Agora é seguro verificar
        secondary_text = extract_subtitle_text_for_frame(frame_number, secondary_subtitle_file, config=config)
        if secondary_text:  # Verifica se o texto não é None
            subtitle_message += "\n\n\n" + secondary_text

    return subtitle_message
