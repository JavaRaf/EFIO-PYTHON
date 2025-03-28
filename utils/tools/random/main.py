import random
from pathlib import Path
from time import sleep
from typing import Optional

from utils.tools.facebook import Facebook
from utils.tools.load_configs import load_configs, load_counter
from utils.tools.logger import get_logger
from utils.tools.subtitles import get_subtitle_message, frame_to_timestamp
from utils.tools.frame_util import random_crop
from utils.tools.random.filters import get_random_frame
from utils.tools.random.filters import (
    None_filter,
    two_panel,
    mirror_image,
    negative_filter,
    brightness_and_contrast,
)

# Carregar configurações e contador
CONFIGS: dict = load_configs(Path.cwd() / "configs.yml")
COUNTER: dict = load_counter(Path.cwd() / "counter.yml")

# Inicializar logger e Facebook
logger = get_logger(__name__)
fb = Facebook(CONFIGS, COUNTER)

# Dicionário de funções de filtros
filters_functions = {
    "None_filter": None_filter,
    "two_panel": two_panel,
    "mirror_image": mirror_image,
    "negative_filter": negative_filter,
    "brightness_and_contrast": brightness_and_contrast,
}

# Obtém os filtros configurados
random_posting_filters = CONFIGS.get("random_posting", {}).get("filters", {})

# Filtra apenas os filtros habilitados
enabled_filters_data = {
    name: data for name, data in random_posting_filters.items() if data.get("enabled")
}

enable_filters = list(enabled_filters_data) or ["None_filter"]
percentages = [data["percentage"] for data in enabled_filters_data.values()]


def post_frame(message: str, frame_path: Path) -> Optional[str]:
    """Posta um frame e retorna o ID do post."""

    post_id = fb.post(message, frame_path)
    if not post_id:
        logger.error("Failed to post frame")
        return None

    print(f"\n\n├── Random Frame has been posted", flush=True)
    sleep(2)
    return post_id


def post_subtitles(post_id: str, frame_number: int, current_episode: int) -> Optional[str]:
    """Posta as legendas associadas ao frame."""
    if not CONFIGS.get("posting", {}).get("posting_subtitles", False):
        return None

    subtitle_message = get_subtitle_message(frame_number, current_episode, CONFIGS)

    if subtitle_message:
        formated_message = f"Episode {current_episode} Frame {frame_number}\n\n{subtitle_message}"
        subtitle_post_id = fb.post(formated_message, None, post_id)
        print(f"└── Subtitle has been posted", flush=True)
        sleep(2)
        return subtitle_post_id
    return None


def post_random_crop(post_id: str, frame_path: Path, frame_number: int, current_episode: int) -> Optional[str]:
    """Posta uma versão recortada do frame aleatório."""
    if not CONFIGS.get("posting", {}).get("random_crop", {}).get("enabled", False):
        return None

    crop_path, crop_message = random_crop(frame_path, CONFIGS)
    if crop_path and crop_message:
        crop_post_id = fb.post(crop_message, crop_path, post_id)
        print(f"└── Random Crop has been posted", flush=True)
        sleep(2)
        return crop_post_id
    return None


def random_main():
    """Executa o processo de postagem de um frame aleatório com filtro."""
    
    paths: list = []
    output_path: Path = None
    chosen_filter = random.choices(enable_filters, weights=percentages)[0]
    IMG_FPS = CONFIGS.get("episodes", {}).get(COUNTER.get("current_episode", 0), {}).get("img_fps", 2)

    if not chosen_filter:
        logger.error("Failed to apply filter")
        return

    if chosen_filter not in filters_functions:
        logger.error(f"Filter {chosen_filter} not found")
        return

    if chosen_filter == "two_panel":
        print(f"\n\n├── Selected filter: {chosen_filter}", flush=True)

        for _ in range(2):
            frame_data = get_random_frame()
            if not frame_data or frame_data[0] is None:
                logger.error("Failed to get frame")
                return  # Interrompe a execução se não conseguir obter 2 frames

            path, frame_number, episode_number = frame_data
            subtitle_message = get_subtitle_message(frame_number, episode_number, CONFIGS)
            paths.append(
                {
                    "frame_path": path,
                    "frame_number": frame_number,
                    "episode_number": episode_number,
                    "subtitle_message": subtitle_message,
                    "frame_timestamp": frame_to_timestamp(IMG_FPS, frame_number),
                }
            )

        if len(paths) < 2:
            logger.error("Failed to obtain enough frames for two_panel")
            return

        # Verifica se os caminhos das imagens são válidos antes de aplicar o filtro
        if not all(p["frame_path"] for p in paths):
            logger.error("Invalid frame path detected")
            return

        output_path = filters_functions[chosen_filter](paths)  # Aplica o filtro two_panel

        message = (
            "[Random Frames]\n\n"
            f"Season {COUNTER.get('season')}, "
            f"Episodes ({paths[0]['episode_number']} | {paths[1]['episode_number']})\n"
            f"Frames ({paths[0]['frame_number']} | {paths[1]['frame_number']})\n"
            f"Timestamp: ({paths[0]['frame_timestamp']} | {paths[1]['frame_timestamp']})\n"
            f"-\n"
            f"Filter: {chosen_filter}\n"
        )

    else:
        frame_data = get_random_frame()
        if not frame_data or frame_data[0] is None:
            logger.error("Failed to get frame")
            return

        path, frame_number, episode_number = frame_data
        subtitle_message = get_subtitle_message(frame_number, episode_number, CONFIGS)

        if not path:
            logger.error("Invalid frame path")
            return

        output_path = filters_functions[chosen_filter]([{"frame_path": path}])  # Aplica o filtro

        message = (
            "[Random Frames]\n\n"
            f"Season {COUNTER.get('season')}, "
            f"Episode {episode_number}\n"
            f"Frame {frame_number}\n"
            f"Timestamp: {frame_to_timestamp(IMG_FPS, frame_number)}\n"
            f"-\n"
            f"Filter: {chosen_filter}\n"
        )

    post_id = post_frame(message, output_path)

    if not post_id:
        logger.error("Failed to post frame")
        return

    if chosen_filter == "two_panel":
        post_subtitles(post_id, paths[0]['frame_number'], paths[0]['episode_number'])
        post_subtitles(post_id, paths[1]['frame_number'], paths[1]['episode_number'])
        post_random_crop(post_id, paths[0]['frame_path'], paths[0]['frame_number'], paths[0]['episode_number'])
    else:
        post_subtitles(post_id, frame_number, episode_number)
        post_random_crop(post_id, path, frame_number, episode_number)
