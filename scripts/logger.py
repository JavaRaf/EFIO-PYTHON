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


logger = get_logger(__name__)

def update_fb_log(frame_counter, posts_data):
    """Atualiza o arquivo de log do Facebook."""

    try:
        if not fb_log_path.exists():
            fb_log_path.touch(exist_ok=True)

        season = frame_counter.get("season")
        episode = frame_counter.get("current_episode")

        with open(fb_log_path, "a", encoding="utf-8") as f:
            for post in posts_data:
                post_id = post.get("post_id")
                frame_number = post.get("frame_number")

                f.write(
                    f"season: {season}, episode: {episode}, frame: {frame_number} https://facebook.com/{post_id}\n"
                )
    except Exception as e:
        logger.error(f"Erro ao atualizar o log do Facebook: {e}", exc_info=True)
        return None