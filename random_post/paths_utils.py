from pathlib import Path
from scripts.paths import frames_dir
import os
import random


def get_random_frame() -> tuple[Path, int, int]:
    """
    Returns:
        tuple[Path, int, int]: (caminho do arquivo, número do frame, número do episódio)
    """
    list_episodes = os.listdir(frames_dir)
    random_episode = random.choice(list_episodes)

    frame_number = random.choice(
        [
            int(x.split("_")[1].split(".")[0])
            for x in os.listdir(f"{frames_dir}/{random_episode}")
            if x.startswith("frame_") and x.endswith(".jpg")
        ]
    )
    frame_path = Path(frames_dir) / random_episode / f"frame_{frame_number}.jpg"

    return frame_path, frame_number, int(random_episode)
