from ruamel.yaml import YAML
from pathlib import Path
from utils.tools.logger import get_logger

logger = get_logger(__name__)

yaml: YAML = YAML()  # Criando a instância primeiro
yaml.preserve_quotes = True  # Configurando preserve_quotes separadamente
yaml.indent(mapping=2, sequence=4, offset=2)  # Corrigindo a indentação corretamente
yaml.default_flow_style = False


def load_configs(configs_path: Path) -> dict:
    if not configs_path.exists():
        logger.error(f"Config file not found: {configs_path}")
        return {}

    try:
        with open(configs_path, "r") as file:
            return yaml.load(file)
    except Exception as e:
        logger.error(f"Error while loading configs: {e}", exc_info=True)
        return {}


def load_counter(counter_path: Path) -> dict:
    if not counter_path.exists():
        logger.error(f"Counter file not found: {counter_path}")
        return {}

    try:
        with open(counter_path, "r") as file:
            return yaml.load(file)
    except Exception as e:
        logger.error(f"Error while loading counter: {e}", exc_info=True)
        return {}


def save_counter(counter: dict, counter_path: Path) -> None:
    try:
        with open(counter_path, "w") as file:
            yaml.dump(counter, file)
    except Exception as e:
        logger.error(f"Error while saving counter: {e}", exc_info=True)


def update_counter(counter: dict, counter_path: Path, args: dict) -> None:
    counter.update(args)
    save_counter(counter, counter_path)
