from ruamel.yaml import YAML
from pathlib import Path
from src.config.time_utils import get_local_time

def get_necessary_data(config: dict) -> tuple:
    fph = config.get("posting")["fph"]
    current_frame = config.get("episodes")[config.get("current_episode") - 1].get("frame_iterator")
    interval = config.get("posting")["posting_interval"]
    return fph, current_frame, interval


def validate_config(config):
    """
    Valida as configurações necessárias para a execução do programa.
    
    Args:
        config (dict): Configurações carregadas do arquivo YAML
        
    Raises:
        ValueError: Se alguma configuração obrigatória estiver faltando
    """
    required_keys = ['posting', 'episodes', 'current_episode', 'templates']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Configuração obrigatória '{key}' não encontrada")



def parse_config(file_path: str) -> dict:
    """
    Carrega as configurações do arquivo YAML
    
    Args:
        file_path (str): Caminho para o arquivo de configuração YAML
        
    Returns:
        dict: Dicionário de configurações, vazio se ocorrer erro
    """

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 1000

    try:
        file_path = Path(file_path)
        if not file_path.exists():
            file_path.touch()
            
        with open(file_path, "r") as file:
           return yaml.load(file) or {}
        

    except (OSError, yaml.YAMLError) as error:
        print(f"Erro ao ler arquivo de configuração: {error}", flush=True)

    return {} 


def load_necessary_configs(config: dict) -> tuple:
    validate_config(config)
    fph, frame_iterator, interval = get_necessary_data(config)
    return fph, frame_iterator, interval, get_local_time(config)

