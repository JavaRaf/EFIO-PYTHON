import random
from time import sleep
from pathlib import Path

from random_post.filters import (
    mirror_image,
    negative_filter,
    two_panel,
    brightness_and_contrast,
    None_filter,
)
from random_post.paths_utils import get_random_frame
from scripts.load_configs import load_configs, load_frame_counter
from scripts.logger import get_logger
from scripts.subtitle_handler import get_subtitle_message, frame_to_timestamp
from scripts.facebook import fb_posting
from scripts.frame_utils import random_crop_generator


logger = get_logger(__name__)
configs: dict = load_configs()
frame_counter: dict = load_frame_counter()


filters_functions = {
    "None_filter": None_filter,
    "two_panel": two_panel,
    "mirror_image": mirror_image,
    "negative_filter": negative_filter,
    "brightness_and_contrast": brightness_and_contrast,
}

enable_filters = [
    filter
    for filter, value in configs.get("random_posting").get("filters").items()
    if value.get("enabled")
]

percentages = [
    value.get("percentage")
    for filter, value in configs.get("random_posting").get("filters").items()
    if value.get("enabled")
]

if not enable_filters:
    enable_filters = ["None_filter"]

def post_frame(message: str, episode_number: int, frame_number: int, frame_path: Path):
    """Posta um frame."""

    post_id = fb_posting(message, frame_path)
    print(
        f"\n\n├──Random Frame has been posted",
        flush=True,
    )
    return post_id

def handle_subtitles(episode_number, frame_number, post_id, configs):
    """Posta legendas"""
    if configs.get("posting").get("posting_subtitles"):
        subtitle_message, frame_timestamp = get_subtitle_message(
            episode_number, frame_number
        )
        if subtitle_message:
            fb_posting(subtitle_message, None, post_id)
            print(
                f"├──Subtitle has been posted, timestamp: {frame_timestamp}", flush=True
            )
            sleep(2)


def handle_random_crop(frame_path, post_id, configs):
    """Posta um recorte aleatório"""
    if configs.get("posting").get("random_crop").get("enabled"):
        crop_path, crop_message = random_crop_generator(frame_path)
        fb_posting(crop_message, crop_path, post_id)
        print("└──Random Crop has been posted", flush=True)
        sleep(2)




def random_main():

    paths: list = []
    chosen_filter = random.choices(enable_filters, weights=percentages)[0]
    filter_function = filters_functions.get(chosen_filter)
   
    print(f"\n\n├──Selected filter: {chosen_filter}", flush=True)

    if chosen_filter == "two_panel":
        for _ in range(2):
            path, frame_number, episode_number = get_random_frame()
            subtitle_message, _ = get_subtitle_message(
                episode_number, frame_number
            )
            paths.append(
                {
                    "frame_path": path,
                    "frame_number": frame_number,
                    "episode_number": episode_number,
                    "subtitle_message": subtitle_message,
                    "frame_timestamp": frame_to_timestamp(episode_number, frame_number),
                }
            )

        filter_path = two_panel(paths)  # apply two panel filter

        message = (
            "[Random Frames]\n\n"
            f"Season {frame_counter.get('season')}, "
            f"Episodes ({paths[0]['episode_number']} | {paths[1]['episode_number']})\n"
            f"Frames ({paths[0]['frame_number']} | {paths[1]['frame_number']})\n"
            f"timestamp: ({paths[0]['frame_timestamp']} | {paths[1]['frame_timestamp']})\n"
            f"-\n"
            f"-\n"
            f"Filter: {chosen_filter}\n"
        )


    else:
        path, frame_number, episode_number = get_random_frame()
        subtitle_message, _ = get_subtitle_message(
            episode_number, frame_number
        )
        paths.append(
            {
                "frame_path": path,
                "frame_number": frame_number,
                "episode_number": episode_number,
                "subtitle_message": subtitle_message,
                "frame_timestamp": frame_to_timestamp(episode_number, frame_number),
            }
        )

        filter_path = filter_function(paths)  # apply filter

        message = (
            "[Random Frame]\n\n"
            f"Season {frame_counter.get('season')}, "
            f"Episode {paths[0]['episode_number']}, "
            f"Frame {paths[0]['frame_number']}\n"
            f"timestamp: {paths[0]['frame_timestamp']}\n"
            f"-\n"
            f"-\n"
            f"Filter: {chosen_filter}\n"
        )

    # post
    post_id = post_frame(
        message,
        paths[0]["episode_number"],
        paths[0]["frame_number"],
        filter_path,
    )
    # subtitle
    if chosen_filter == "two_panel":
        handle_subtitles(paths[0]["episode_number"], paths[0]["frame_number"], post_id, configs)
        handle_subtitles(paths[1]["episode_number"], paths[1]["frame_number"], post_id, configs)
    
    else:
        handle_subtitles(paths[0]["episode_number"], paths[0]["frame_number"], post_id, configs)
    
    # random crop
    handle_random_crop(filter_path, post_id, configs)