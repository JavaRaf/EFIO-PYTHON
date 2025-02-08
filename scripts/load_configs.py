import yaml

from scripts.logger import get_logger
from scripts.paths import configs_path, frame_couter_path

logger = get_logger(__name__)


def load_frame_couter() -> dict:
    """
    Carrega o contador de quadros a partir do arquivo frame_couter.txt.

    Returns:
        dict: Dicionário com os valores do contador de quadros.
    """
    frame_couter_json = {}
    try:
        with open(frame_couter_path, "r", encoding="utf-8") as file:
            frame_couter = file.readlines()

        for line in frame_couter:
            if not line.startswith("#"):
                key, value = line.split(":")
                frame_couter_json[key.strip()] = int(value.strip())
        return frame_couter_json

    except Exception as e:
        logger.error(f"Error loading frame counter: {e}", exc_info=True)
        return {}


def update_frame_couter(frame_couter_json: dict) -> None:
    """
    Atualiza o contador de quadros no arquivo frame_couter.txt.

    Args:
        frame_couter_json (dict): Dicionário com os valores do contador de quadros.
    """
    try:
        with open(frame_couter_path, "w", encoding="utf-8") as file:
            file.write(f"season: {frame_couter_json['season']}\n")
            file.write(f"current_episode: {frame_couter_json['current_episode']}\n")
            file.write("# \n")
            file.write("# \n")
            file.write("# \n")
            file.write(f"frame_iterator: {frame_couter_json['frame_iterator']}\n")
            file.write(
                f"total_frames_posted: {frame_couter_json['total_frames_posted']}\n"
            )
    except Exception as e:
        logger.error(f"Error updating frame counter: {e}", exc_info=True)


def load_configs() -> dict:
    """
    Carrega as configurações a partir do arquivo configs.yaml.

    Returns:
        dict: Dicionário com as configurações.
    """
    try:
        with open(configs_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading configs: {e}", exc_info=True)
        return {}
