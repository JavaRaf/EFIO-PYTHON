from datetime import datetime, timedelta
from PIL import Image
import random
import subprocess
import os
from pathlib import Path

def convert_frame_to_timestamp(frame_number: int, config: dict) -> datetime:
    """
    Converte número do frame para timestamp.
    
    Args:
        frame_number: Número do frame
        config: Dicionário de configuração
        
    Returns:
        datetime: Timestamp correspondente ao frame
    """
    img_fps = config.get("episodes")[config.get("current_episode") - 1].get("img_fps")
    return datetime(1900, 1, 1, 0, 0, 0, 0) + timedelta(seconds=frame_number / img_fps)

def generate_random_frame_crop(frame_path: str, frame_number: int, config: dict) -> tuple[str, str]:
    """
    Gera um recorte aleatório de um frame.
    
    Args:
        frame_path: Caminho do arquivo do frame
        frame_number: Número do frame
        config: Dicionário de configuração
        
    Returns:
        tuple[str, str]: (caminho do arquivo gerado, mensagem descritiva)
    """

    min_x = config.get("posting")["random_crop"].get("min_x")
    min_y = config.get("posting")["random_crop"].get("min_y")
    
    crop_width = crop_height = random.randint(min_x, min_y) # min_x = 200, min_y = 600
    

    with Image.open(frame_path) as img:
        image_width = img.width
        image_height = img.height

    crop_x = random.randint(0, 65535) % (image_width - crop_width)
    crop_y = random.randint(0, 65535) % (image_height - crop_height)
    

    output_crop_path = os.path.join(
        "episodes", "temp_crops",
        f"{config.get('current_episode'):02d}_frame_{frame_number:04d}.jpg"
    )

    command = [
        "magick" if os.name == "nt" else "convert",
        frame_path,
        "-crop",
        f"{crop_width}x{crop_height}+{crop_x}+{crop_y}",
        output_crop_path
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)

        message = f"Random Crop. [{crop_width}x{crop_height} ~ X: {crop_x}, Y: {crop_y}]"
        return output_crop_path, message
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar ImageMagick: {e.stderr}")
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None 