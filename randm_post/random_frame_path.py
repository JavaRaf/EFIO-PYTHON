import os
import random

from scripts.logger import get_logger

logger = get_logger(__name__)


def get_random_episode_and_frame() -> tuple[int, int]:
    """Retorna um frame aleatório de um episódio aleatório"""
    episodes_list = os.listdir("episodes/frames")
    if not episodes_list:
        logger.error("Nenhum episódio encontrado", exc_info=True)
        return None, None

    chosen_episode = random.choice(list(episodes_list))
    frames_list = os.listdir(f"episodes/frames/{chosen_episode}")
    if not frames_list:
        logger.error(f"Episódio {chosen_episode} não tem frames", exc_info=True)
        return None, None

    chosen_frame = random.choice(list(frames_list))

    return int(chosen_episode), int(chosen_frame)
