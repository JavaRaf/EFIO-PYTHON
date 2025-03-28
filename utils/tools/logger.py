import logging
import os
from pathlib import Path

os.makedirs("utils/logs", exist_ok=True)

# Configuração básica do logger
logging.basicConfig(
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("utils/logs/error.log"), logging.StreamHandler()],
)


# Função para obter o logger
def get_logger(name):
    return logging.getLogger(name)


logger = get_logger(__name__)


def update_fb_log(season: int, episode: int, frame_number: int, post_id: str):
    
    try:
        if not os.path.exists(Path.cwd() / "fb"):
            os.makedirs(Path.cwd() / "fb", exist_ok=True)
        
        if not os.path.exists(Path.cwd() / "fb" / "fb.log"):
            Path.touch(Path.cwd() / "fb" / "fb.log")

        with open(Path.cwd() / "fb" / "fb.log", "a") as f:
            f.write(
                    f"season: {season}, episode: {episode}, frame: {frame_number} https://facebook.com/{post_id}\n"
                )
    except Exception as e:
        logger.error(f"Failed to update fb log: {e}")
        return