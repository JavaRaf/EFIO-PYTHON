from ruamel.yaml import YAML
from pathlib import Path

def load_config(file_path: str) -> dict:
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