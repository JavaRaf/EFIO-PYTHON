import random
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
        tuple[Path, int, int]: (caminho do arquivo, número do episódio, total de quadros no episódio)
    """

    frame_counter = load_frame_counter()
    episode_number = frame_counter.get("current_episode", None)

    if episode_number is None:
        return None, None, None

    episode_dir = frames_dir / f"{episode_number:02d}"

    if not episode_dir.exists():
        return None, None, None

    frame_path = episode_dir / f"frame_{frame_number}.jpg"

    if not frame_path.exists():
        frame_path = episode_dir / f"frame_{frame_number:04d}.jpg"

    if not frame_path.exists():
        return None, None, None

    return frame_path, episode_number, get_total_episode_frames(episode_number)


def random_crop_generator(frame_path: str, frame_number: int) -> tuple[str, str]:
    """
    Gera um recorte aleatório de um frame.

    Args:
        frame_path: Caminho do arquivo do frame
        frame_number: Número do frame

    Returns:
        tuple[str, str]: (caminho do arquivo gerado, mensagem descritiva)
    """

    min_x = load_configs().get("posting")["random_crop"].get("min_x")
    min_y = load_configs().get("posting")["random_crop"].get("min_y")

    crop_width = crop_height = random.randint(min_x, min_y)  # min_x = 200, min_y = 600

    with Image.open(frame_path) as img:
        image_width, image_height = img.size

        # Calculando o recorte aleatório
        crop_x = random.randint(0, image_width - crop_width)
        crop_y = random.randint(0, image_height - crop_height)

        # Realizando o recorte
        cropped_img = img.crop(
            (crop_x, crop_y, crop_x + crop_width, crop_y + crop_height)
        )

        # Caminho para salvar a imagem recortada
        output_crop_path = Path(episodes_dir) / "temp_crop.jpg"

        # Salvando a imagem recortada
        cropped_img.save(output_crop_path)

        message = (
            f"Random Crop. [{crop_width}x{crop_height} ~ X: {crop_x}, Y: {crop_y}]"
        )
        return str(output_crop_path), message


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
