from pathlib import Path

from time import sleep

from scripts.facebook import fb_posting, fb_update_bio, repost_in_album
from scripts.frame_utils import (
    build_frame_file_path,
    get_total_episode_frames,
    random_crop_generator,
)
from scripts.load_configs import load_configs, load_frame_counter, save_frame_counter
from scripts.logger import get_logger, update_fb_log
from scripts.messages import format_message
from scripts.subtitle_handler import get_subtitle_message
from scripts.get_local_time import sleeper_function

from random_post.random_main import random_main

logger = get_logger(__name__)


def post_frame(
    episode_number: int,
    type_message: str,
    frame_number: int,
    frame_path: Path,
    configs: dict,
    frame_counter: dict,
):
    """Posta um frame."""
    post_message = format_message(
        episode_number,
        frame_number,
        configs.get(type_message),
        frame_counter,
        configs,
    )
    post_id = fb_posting(post_message, frame_path)
    print(
        f"\n\n├──Episode {episode_number} frame {frame_number} has been posted",
        flush=True,
    )
    return post_id, post_message


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


def update_bio_and_frame_counter(frame_counter, configs, number_of_frames_posted):
    """Atualiza a bio e o contador de frames"""
    frame_counter["frame_iterator"] += number_of_frames_posted
    frame_counter["total_frames_posted"] += number_of_frames_posted

    bio_message = format_message(
        frame_counter.get("current_episode", None),
        frame_counter["frame_iterator"],
        configs.get("bio_message"),
        frame_counter,
        configs,
    )
    fb_update_bio(bio_message)

    try:
        if frame_counter["frame_iterator"] >= get_total_episode_frames(
            frame_counter["current_episode"]
        ):
            if not configs.get("episodes").get(frame_counter["current_episode"] + 1):
                print("\n\n", "All episodes were posted!!!\n", flush=True)
            frame_counter["current_episode"] += 1
            frame_counter["frame_iterator"] = 0
        save_frame_counter(frame_counter)
    except Exception:
        logger.error("Error updating frame counter", exc_info=True)


# posta frames específicos (sequenciais)
def post_frame_by_number(fph, frame_iterator, frame_counter, configs, posting_interval):
    """Posta um frame específico"""
    posts_data = []

    for i in range(1, fph + 1):
        frame_number = frame_iterator + i
        frame_path, episode_number, total_frames_in_episode_dir = build_frame_file_path(
            frame_number
        )

        if not total_frames_in_episode_dir:
            print("\n\n", "All frames in this episode were posted", flush=True)
            break

        if not episode_number or not total_frames_in_episode_dir:
            logger.error(
                "Episode not found in configs, check frame_counter.txt and frames folder"
            )
            break

        if not frame_path.exists():
            print("Frame not found, check if episdoe exists", flush=True)
            break

        post_id, post_message = post_frame(
            episode_number,
            "post_message",
            frame_number,
            frame_path,
            configs,
            frame_counter,
        )

        posts_data.append(
            {
                "post_id": post_id,
                "message": post_message,
                "episode_number": episode_number,
                "frame_number": frame_number,
                "frame_path": frame_path,
            }
        )

        handle_subtitles(episode_number, frame_number, post_id, configs)
        handle_random_crop(frame_path, post_id, configs)

        sleeper_function(posting_interval)  # print a timer in the terminal

    if len(posts_data) > 0:

        repost_in_album(posts_data)  # repost in album if enabled

        update_fb_log(frame_counter, posts_data)
        update_bio_and_frame_counter(frame_counter, configs, len(posts_data))


# posta frames aleatórios (only if random_posting is enabled)
def random_posting(fph):
    """Posta frames aleatórios"""
    for i in range(1, fph + 1):
        random_main()


# main function
def main():
    """Main function"""
    frame_counter: dict = load_frame_counter()
    configs: dict = load_configs()
    frame_counter: dict = load_frame_counter()
    configs: dict = load_configs()

    posting_interval: int = int(
        configs.get("posting").get("posting_interval", 2)
    )  # default 2 minutes
    fph: int = configs.get("posting").get("fph", 15)  # default 15 frames per hour
    frame_iterator: int = frame_counter.get("frame_iterator", 0)  # default 0

    if configs.get("random_posting").get("enabled", False):
        random_posting(
            fph,
            frame_counter,
            configs,
            frame_iterator,
            posting_interval,
        )

    else:
        post_frame_by_number(
            fph,
            frame_iterator,
            frame_counter,
            configs,
            posting_interval,
        )


if __name__ == "__main__":
    main()
