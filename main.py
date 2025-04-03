from pathlib import Path
from time import sleep
from copy import deepcopy
from utils.tools.load_configs import load_configs
from utils.tools.subtitles import frame_to_timestamp
from utils.tools.facebook import Facebook
from utils.tools.load_configs import load_configs, load_counter, save_counter
from utils.tools.logger import get_logger, update_fb_log
from utils.tools.frame_util import (
    counter_frames_from_this_episode,
    return_frame_path,
    random_crop,
)
from utils.tools.messages import format_message
from utils.tools.subtitles import get_subtitle_message

from utils.tools.random.main import random_main

logger = get_logger(__name__)


def update_bio_if_needed(facebook: Facebook, CONFIGS: dict, COUNTER: dict, base_COUNTER: dict):
    if COUNTER == base_COUNTER:
        return  # avoid unnecessary execution

    if COUNTER.get("frame_iterator", 0) == counter_frames_from_this_episode(COUNTER.get("current_episode", None)):
        COUNTER["current_episode"] += 1
        COUNTER["frame_iterator"] = 0
        print(f"\n\nEpisode {COUNTER.get('current_episode', 0) -1} has been posted\n"
              f"Updating to next episode {COUNTER.get('current_episode', 0)}\n\n", flush=True)

    facebook.update_bio(
        format_message(
            CONFIGS.get("bio_message", ""),
            COUNTER.get("frame_iterator", 0),
            COUNTER.get("total_frames_posted", 0),
            COUNTER,
            CONFIGS,
        )
    )
    save_counter(COUNTER, Path("counter.yml"))

def post_frame(frame_path: Path, frame_number: int, message: str, CONFIGS: dict, COUNTER: dict, facebook: Facebook) -> str | None:
    try:
        post_id = facebook.post(message, frame_path)
        if not post_id:
            logger.error(f"Failed to post frame {frame_number} - No post_id returned")
            return None

        timestamp = frame_to_timestamp(
            CONFIGS.get("episodes", {}).get(COUNTER.get("current_episode", 0), {}).get("img_fps", None),
            frame_number,
        )

        print(f"\n\n├──Episode {COUNTER.get('current_episode', 0)} frame {frame_number} posted | timestamp: {timestamp}", flush=True)
        return post_id

    except Exception as e:
        logger.error(f"Error posting frame {frame_number}: {str(e)}", exc_info=True)
        return None


def post_subtitles(post_id: str, frame_number: int, CONFIGS: dict, COUNTER: dict, facebook: Facebook) -> str | None:

    if not CONFIGS.get("posting", {}).get("posting_subtitles", False):
        return None

    subtitle_message = get_subtitle_message(
        frame_number, COUNTER.get("current_episode", 0), CONFIGS
    )
    if subtitle_message:
        subtitle_post_id = facebook.post(subtitle_message, None, post_id)
        print(
            f"├──Subtitle has been posted",
            flush=True,
        )
        sleep(2)
        return subtitle_post_id
    return None


def post_random_crop(
    post_id: str, frame_path: Path, frame_number: int, CONFIGS: dict, facebook: Facebook
) -> str | None:
    if not CONFIGS.get("posting", {}).get("random_crop", {}).get("enabled", False):
        return None

    crop_path, crop_message = random_crop(frame_path, CONFIGS)
    if crop_path and crop_message:
        crop_post_id = facebook.post(crop_message, crop_path, post_id)
        print(
            f"└──Random Crop has been posted",
            flush=True,
        )
        sleep(2)
        return crop_post_id
    return None


def ordered_post(CONFIGS: dict, COUNTER: dict, posting_interval: int, facebook: Facebook):
    frame_iterator: int = COUNTER.get("frame_iterator", 0)
    current_episode: int = COUNTER.get("current_episode", 0)
    total_frames_posted: int = COUNTER.get("total_frames_posted", 0)
    fph: int = CONFIGS.get("posting", {}).get("fph", 15)

    for i in range(1, fph + 1):
        frame_number = frame_iterator + i
        total_frames_posted += 1

        frames_from_this_episode = counter_frames_from_this_episode(current_episode)

        if frame_number > frames_from_this_episode:
            print(
                f"current frame_number is {frame_number}"
                f" and counter_frames_from_this_episode is {frames_from_this_episode}",
                flush=True,
            )
            print(
                f"\n\nAll frames from episode {current_episode} have been posted\n\n",
                flush=True,
            )
            break

        if (
            not CONFIGS.get("episodes", {})
            .get(current_episode, {})
            .get("img_fps", None)
        ):
            logger.error(
                f"Error, img_fps not set for episode {current_episode},"
                f"please define img_fps in the CONFIGS.yml file",
                exc_info=True,
            )
            break

        message = format_message(
            CONFIGS.get("post_message", ""),
            frame_number,
            total_frames_posted,
            COUNTER,
            CONFIGS,
        )
        if not message:
            logger.error("Post message not found in CONFIGS")
            break  # after the break, it saves everything in main and closes the program

        frame_path: Path | None = return_frame_path(frame_number, current_episode)

        if not frame_path:
            logger.error(f"Frame {frame_number} not found in episode {current_episode}")
            break

        post_id = post_frame(
            frame_path, frame_number, message, CONFIGS, COUNTER, facebook
        )

        if not post_id:
            logger.error(
                f"Failed to post frame {frame_number} in episode {current_episode}"
            )
            break

        facebook.repost_to_album(message, frame_path, CONFIGS, COUNTER)

        post_subtitles(post_id, frame_number, CONFIGS, COUNTER, facebook)
        post_random_crop(post_id, frame_path, frame_number, CONFIGS, facebook)

        COUNTER["frame_iterator"] += 1
        COUNTER["total_frames_posted"] += 1

        update_fb_log(COUNTER.get("season", 0), current_episode, frame_number, post_id)

        print("\nsleeping...\n")
        sleep(posting_interval * 60)  # 2 minutes


def random_post(fph: int = 15, posting_interval: int = 2):
    for _ in range(1, fph + 1):
        random_main()
        sleep(posting_interval * 60)  # 2 minutes


def validate_configs(CONFIGS: dict) -> bool:
    required_keys = ['episodes', 'posting', 'post_message', 'bio_message']

    for key in required_keys:
        if key not in CONFIGS:
            logger.error(f"Missing required config key: {key}")
            return False

    if not CONFIGS.get('episodes'):
        logger.error("No episodes configured")
        return False

    return True

def main():
    CONFIGS: dict = load_configs(Path("configs.yml"))
    if not validate_configs(CONFIGS):
        logger.error("Invalid configuration")
        return
    COUNTER: dict = load_counter(Path("counter.yml"))
    base_COUNTER = deepcopy(COUNTER)  # copy counter for comparison

    facebook = Facebook(CONFIGS, COUNTER)
    fph = CONFIGS.get("posting", {}).get("fph", 15)
    posting_interval = CONFIGS.get("posting", {}).get("posting_interval", 2)

    if CONFIGS.get("random_posting", {}).get("enabled", False):
        random_post(fph, posting_interval)
    else:
        ordered_post(CONFIGS, COUNTER, posting_interval, facebook)

    # update bio if needed
    update_bio_if_needed(facebook, CONFIGS, COUNTER, base_COUNTER)


if __name__ == "__main__":
    main()
