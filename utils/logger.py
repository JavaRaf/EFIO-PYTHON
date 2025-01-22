from pathlib import Path
import os

def log_facebook_interaction(current_time: str, logs: list = []) -> None:
    """
    Registra interações do Facebook no arquivo de log.
    
    Args:
        current_time (str): Timestamp da interação
        logs (list): Lista de tuplas contendo (episódio, frame, id_facebook)
    """
    # Criar diretório de logs se não existir
    log_dir = "logs/facebook"
    os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, "fb_logs.txt")
    if not os.path.exists(log_path):
        Path(log_path).touch(exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as file:
        for id in logs:
            file.write(f"episode: {id[0]} frame: {id[1]} - https://www.facebook.com/{id[2]} - {current_time}\n") 