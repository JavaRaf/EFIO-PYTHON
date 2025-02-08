import os
import random
import subprocess
from pathlib import Path

from PIL import Image

from scripts.load_configs import load_configs, load_frame_counter
from scripts.logger import get_logger
from scripts.paths import episodes_dir, frames_dir

logger = get_logger(__name__)


def build_frame_file_path(frame_number: int) -> tuple[Path, int, int]:
    """
    Constrói o caminho do arquivo para um frame específico

    Args:
        frame_number: Número do frame desejado
    Returns:
        Path: Caminho do arquivo do frame
        int: Número do episódio
    """

    episode_number = load_frame_counter()["current_episode"]
    frame_path = frames_dir / f"{episode_number:02d}" / f"frame_{frame_number:04d}.jpg"
    length_of_episode = frames_dir / f"{episode_number:02d}"

    if not length_of_episode.exists():
        return None, None, None

    length_of_episode = len(list(length_of_episode.iterdir()))

    if not frame_path.exists():
        frame_path = frames_dir / f"{episode_number:02d}" / f"frame_{frame_number}.jpg"

    return frame_path, episode_number, length_of_episode


def random_crop_generator(frame_path: str, frame_number: int) -> tuple[str, str]:
    """

    Gera um recorte aleatório de um frame.


    Args:
        frame_path: Caminho do arquivo do frame
        frame_number: Número do frame
        config: Dicionário de configuração

    Returns:
        tuple[str, str]: (caminho do arquivo gerado, mensagem descritiva)
    """

    min_x = load_configs().get("posting")["random_crop"].get("min_x")
    min_y = load_configs().get("posting")["random_crop"].get("min_y")

    crop_width = crop_height = random.randint(min_x, min_y)  # min_x = 200, min_y = 600

    with Image.open(frame_path) as img:
        image_width = img.width
        image_height = img.height

    crop_x = random.randint(0, 65535) % (image_width - crop_width)
    crop_y = random.randint(0, 65535) % (image_height - crop_height)

    output_crop_path = episodes_dir / "temp_random_crop.jpg"

    command = [
        "magick" if os.name == "nt" else "convert",
        frame_path,
        "-crop",
        f"{crop_width}x{crop_height}+{crop_x}+{crop_y}",
        output_crop_path,
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)

        message = (
            f"Random Crop. [{crop_width}x{crop_height} ~ X: {crop_x}, Y: {crop_y}]"
        )
        return output_crop_path, message
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar ImageMagick: {e.stderr}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Erro ao executar ImageMagick: {e}", exc_info=True)
        return None


def get_total_episode_frames(episode_number: int) -> int:
    """
    Retorna o total de quadros de um episódio.

    Args:
        episode_number: Número do episódio

    Returns:
        int: Total de quadros do episódio
    """
    episode_path = frames_dir / f"{episode_number:02d}"
    return len(list(episode_path.iterdir()))



