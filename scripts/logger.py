import logging
import os
from scripts.paths import fb_log_path

# Cria o diretório sys se não existir
os.makedirs("sys", exist_ok=True)

# Configuração básica do logger
logging.basicConfig(
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sys/Error.log"), logging.StreamHandler()],
)


# Função para obter o logger
def get_logger(name):
    return logging.getLogger(name)


def update_fb_log(frame_counter, frames, post_ids):
    """Atualiza o arquivo de log do Facebook."""
    season = frame_counter.get("season")
    episode = frame_counter.get("current_episode")

    with open(fb_log_path, "a", encoding="utf-8") as f:
        for post_id, frame in zip(post_ids, frames):
            f.write(
                f"season: {season} episode: {episode} frame: {frame} https://graph.facebook.com/{post_id}\n"
            )
