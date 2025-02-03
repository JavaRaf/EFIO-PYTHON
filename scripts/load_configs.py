from scripts.paths import frame_couter_path, configs_path
import yaml

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
        print(f"Error loading frame counter: {e}")
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
            file.write(f"# \n")
            file.write(f"# \n")
            file.write(f"# \n")
            file.write(f"frame_iterator: {frame_couter_json['frame_iterator']}\n")
            file.write(f"total_frames_posted: {frame_couter_json['total_frames_posted']}\n")
    except Exception as e:
        print(f"Error updating frame counter: {e}")

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
        print(f"Error loading configs: {e}")
        return {}







