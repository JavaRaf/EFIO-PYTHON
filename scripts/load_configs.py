from scripts.logger import get_logger
from scripts.paths import configs_path, frame_counter_path

from ruamel.yaml import YAML

logger = get_logger(__name__)

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


def load_frame_counter() -> dict:
    """
    Carrega o contador de quadros a partir do arquivo frame_counter.yaml.

    Returns:
        dict: Dicionário com os valores do contador de quadros.
    """
    try:
        with open(frame_counter_path, "r", encoding="utf-8") as file:
            return yaml.load(file)
    except Exception as e:
        logger.error(f"Error loading frame counter: {e}", exc_info=True)
        return {}


def save_frame_counter(frame_counter_json: dict) -> None:
    """
    Atualiza o contador de quadros no arquivo frame_counter.yaml.

    Args:
        frame_counter_json (dict): Dicionário com os valores do contador de quadros.
    """
    try:
        with open(frame_counter_path, "w", encoding="utf-8") as file:
            yaml.dump(frame_counter_json, file)
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
            return yaml.load(file)
    except Exception as e:
        logger.error(f"Error loading configs: {e}", exc_info=True)
        return {}
