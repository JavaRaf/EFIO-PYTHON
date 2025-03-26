from pathlib import Path
import random
from utils.tools.logger import get_logger
from PIL import Image

logger = get_logger(__name__)


def counter_frames_from_this_episode(episode_number: int) -> int | None:
    """
    Returns the total number of frames in an episode folder.

    Args:
        episode_number: Episode number (1 digit, e.g. 1, 2, etc.)

    Returns:
        int: Total number of frames in the episode (or 0 if nao encontrado)
    """
    if not isinstance(episode_number, int):
        logger.error("Episode number must be an integer")
        return 0

    frames_dir = Path(__file__).parent.parent.parent / "frames"
    episode_dir = frames_dir / str(episode_number).zfill(2)

    if not episode_dir.exists():
        logger.error(f"Episode {episode_number} not found in frames directory")
        return 0

    return len([f for f in episode_dir.iterdir() if f.is_file()])


def random_crop(frame_path: Path, configs: dict) -> tuple[Path, str] | None:
    """
    Returns a random crop of the frame.

    Args:
        frame_path: Path to the frame image.

    Returns:
        tuple[Path, str]: Tuple containing the path to the cropped image and the crop coordinates.
    """
    if not isinstance(frame_path, Path):
        logger.error("frame_path must be a Path object")
        return None, None

    if not frame_path.is_file():
        logger.error("frame_path must be a file")
        return None, None

    try:
        min_x: int = configs.get("posting", {}).get("random_crop", {}).get("min_x", 200)
        min_y: int = configs.get("posting", {}).get("random_crop", {}).get("min_y", 600)

        #Random crop dimensions. perfect square.
        crop_width = crop_height = random.randint(min_x, min_y)

        with Image.open(frame_path) as img:
            image_width, image_height = img.size

            if image_width < crop_width or image_height < crop_height:
                logger.error(f"Image {frame_path} is too small for the crop size.")
                return None, None

            # Generate random crop coordinates
            crop_x = random.randint(0, image_width - crop_width)
            crop_y = random.randint(0, image_height - crop_height)

            # Crop image
            cropped_img = img.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))

            # Save the cropped image
            cropped_path = Path(__file__).parent.parent / "temp" / f"cropped_{frame_path.stem}{frame_path.suffix}"
            cropped_path.parent.mkdir(exist_ok=True)

            cropped_img.save(cropped_path)
            message = f"Random Crop. [{crop_width}x{crop_height} ~ X: {crop_x}, Y: {crop_y}]"

            return cropped_path, message

    except Exception as e:
        logger.error(f"Failed to crop image: {str(e)}", exc_info=True)
        return None, None


def return_frame_path(frame_number: int, episode_number: int) -> Path | None:
    """
    Returns the path to a specific frame in an episode.

    Args:
        frame_number (int): The frame number.
        episode_number (int): The episode number.

    Returns:
        Path | None: The path to the frame if found, otherwise None.
    """
    # Validação de entrada
    if not all(isinstance(num, int) for num in (frame_number, episode_number)):
        logger.error("Both frame_number and episode_number must be integers")
        return None

    frames_dir = Path(__file__).parent.parent.parent / "frames"
    episode_dir = frames_dir / f"{episode_number:02d}"

    if not episode_dir.exists():
        logger.error(f"Episode {episode_number} not found in frames directory")
        return None

    # Tenta encontrar o frame com diferentes formatos de nome
    possible_paths = [
        episode_dir / f"frame_{frame_number}.jpg",
        episode_dir / f"frame_{frame_number:04d}.jpg"
    ]

    for frame_path in possible_paths:
        if frame_path.exists():
            return frame_path

    logger.error(f"Frame {frame_number} not found in episode {episode_number}")
    return None