
from gc import enable
from random_post.filters import two_panel_base, mirror_image_base, negative_filter_base, generate_palette_base, warp_in_base, warp_out_base
from random_post.random_frame import get_random_frame
from pathlib import Path
import random
from time import sleep

from scripts.load_configs import load_configs, load_frame_counter
from scripts.messages import format_message
from scripts.facebook import fb_posting
from scripts.subtitle_handler import frame_to_timestamp
from scripts.subtitle_handler import get_subtitle_message
from scripts.frame_utils import random_crop_generator
from scripts.get_local_time import sleeper_function


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


def handle_random_crop(frame_path, frame_number, post_id, configs):
    """Posta um recorte aleatório"""
    if configs.get("posting").get("random_crop").get("enabled"):
        crop_path, crop_message = random_crop_generator(frame_path, frame_number)
        fb_posting(crop_message, crop_path, post_id)
        print("└──Random Crop has been posted", flush=True)
        sleep(2)


filter_functions ={
    "two_panel": two_panel_base,
    "mirror_image": mirror_image_base,
    "negative_filter": negative_filter_base,
    "generate_palette": generate_palette_base,
    "warp_in": warp_in_base,
    "warp_out": warp_out_base
}

# {episode}, Frame {current_frame}, timestamp {frame_timestamp}

def random_main():
    configs = load_configs()
    frame_counter = load_frame_counter()
    posting_interval: int = int(
        configs.get("posting").get("posting_interval", 2)
    )  # default 2 minutes
    base_message: str = configs.get("random_post_message")
    enable_filters = [ filter for filter, value in  configs.get("random_posting").get("filters").items() if value]

    frame_path, frame_number, random_episode = get_random_frame()
    chosen_filter = random.choice(enable_filters)
    filtered_frame_path = filter_functions[chosen_filter](frame_path)
    
    base_message = base_message.format(
        episode = random_episode,
        current_frame = frame_number,
        frame_timestamp = frame_to_timestamp(random_episode, frame_number),
        chosen_filter = chosen_filter
    )

    print(base_message)
    
    post_id = fb_posting(base_message, filtered_frame_path)
    print(f"\n\n├──Random frame {frame_number} has been posted", flush=True)
    
    subtitle_msg, frame_timestamp = get_subtitle_message(random_episode, frame_number)
    if subtitle_msg:
        fb_posting(subtitle_msg, None, post_id)
        print(f"├──Subtitle has been posted, timestamp: {frame_timestamp}", flush=True)
        sleep(2)
    
    handle_subtitles(random_episode, frame_number, post_id, configs)
    handle_random_crop(filtered_frame_path, frame_number, post_id, configs)

    sleeper_function(posting_interval)  # print a timer in the terminal
    
    
