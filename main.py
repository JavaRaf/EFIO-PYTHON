from pathlib import Path
from time import sleep
from copy import deepcopy
from utils.tools.subtitles import frame_to_timestamp
from utils.tools.facebook import Facebook
from utils.tools.load_configs import load_configs, load_counter, save_counter
from utils.tools.logger import get_logger
from utils.tools.frame_util import counter_frames_from_this_episode, return_frame_path, random_crop
from utils.tools.messages import format_message
from utils.tools.subtitles import get_subtitle_message

logger = get_logger(__name__)



def post_frame(
    frame_path: Path, 
    frame_number: int,
    message: str, 
    configs: dict, 
    counter: dict, 
    facebook: Facebook
) -> str | None:
    """
    posta uma frame no facebook e atualiza o contador
    """
    
    post_id = facebook.post(message, frame_path)

    if not post_id:
        logger.error("Failed to post frame")
        return None

    timestamp = frame_to_timestamp(
        configs.get('episodes', {}).get(counter.get('current_episode', 0), {}).get('img_fps', None),
        frame_number
    )

    print(
        f"\n\n├──Episode {counter.get('current_episode', 0)} "
        f"frame {frame_number} has been posted | "
        f"timestamp: {timestamp}",
        flush=True,
    )
    sleep(2)
    return post_id

def post_subtitles(post_id: str, frame_number: int, configs: dict, counter: dict, facebook: Facebook) -> str | None:

    if not configs.get("posting", {}).get("posting_subtitles", False):
        return None

    subtitle_message = get_subtitle_message(
        frame_number,
        counter.get("current_episode", 0),
        configs
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

def post_random_crop(post_id: str, frame_path: Path, frame_number: int, configs: dict, facebook: Facebook) -> str | None:
    if not configs.get("posting", {}).get("random_crop", {}).get("enabled", False):
        return None
    
    crop_path, crop_message = random_crop(frame_path, configs)
    if crop_path and crop_message:
        crop_post_id = facebook.post(crop_message, crop_path, post_id)
        print(
            f"└──Random Crop has been posted",
            flush=True,
        )
        sleep(2)
        return crop_post_id
    return None

def ordered_post(configs: dict, counter: dict, facebook: Facebook):
    frame_iterator: int = counter.get("frame_iterator", 0)
    current_episode: int = counter.get("current_episode", 0)
    total_frames_posted: int = counter.get("total_frames_posted", 0)
    fph: int = configs.get("posting", {}).get("fph", 15)
    
    for i in range(1, fph + 1):
        frame_number = frame_iterator + i
        total_frames_posted += 1

        if frame_number > counter_frames_from_this_episode(current_episode):
            print(f"current frame_number is {frame_number} and counter_frames_from_this_episode is {counter_frames_from_this_episode(current_episode)}", flush=True)
            print(f"\n\nAll frames from episode {current_episode} have been posted\n\n", flush=True)
            break

        if not configs.get("episodes", {}).get(current_episode, {}).get("img_fps", None):
            logger.error(
                f"Error, img_fps not set for episode {current_episode}, please define img_fps in the configs.yml file",
                exc_info=True
            )
            break

        message = format_message(
            configs.get("post_message", ""),
            frame_number,
            total_frames_posted,
            counter,
            configs
        )
        if not message:
            logger.error("Post message not found in configs")
            break  # apos o break, ele salva tudo na main e fecha o programa

        frame_path: Path | None = return_frame_path(frame_number, current_episode)


        if not frame_path:
            logger.error(f"Frame {frame_number} not found in episode {current_episode}")
            break

        post_id = post_frame(frame_path, frame_number, message, configs, counter, facebook)
        
        if not post_id:
            logger.error(f"Failed to post frame {frame_number} in episode {current_episode}")
            break

        repost_id = facebook.repost_to_album(message, frame_path, configs, counter)
        if not repost_id:
            logger.error(f"Failed to repost frame {frame_number} in episode {current_episode}")
            break

        post_subtitles(post_id, frame_number, configs, counter, facebook)
        post_random_crop(post_id, frame_path, frame_number, configs, facebook)
        
        counter["frame_iterator"] += 1
        counter["total_frames_posted"] += 1

        sleep(configs.get("posting", {}).get("posting_interval", 2) * 60) # 2 minutes

        
def random_post():
    pass

def main():
    configs = load_configs(Path("configs.yml"))
    counter = load_counter(Path("counter.yml"))
    base_counter = deepcopy(counter) # copia o contador para comparação

    facebook = Facebook(configs, counter)

    if configs.get("random_posting", {}).get("enabled", False):
        random_post()
    else:
        ordered_post(configs, counter, facebook)

    # Atualiza o bio apenas se houver alterações no contador
    if counter != base_counter:

        if counter.get("frame_iterator", 0) == counter_frames_from_this_episode(counter.get("current_episode", None)):
            counter["current_episode"] += 1
            counter["frame_iterator"] = 0
            print(
                f"\n\nEpisode {counter.get('current_episode', 0) -1} has been posted\n"
                f"updating to next episode {counter.get('current_episode', 0)}\n\n", flush=True)

        facebook.update_bio(format_message(configs.get("bio_message", ""),
            counter.get("frame_iterator", 0),
            counter.get("total_frames_posted", 0),
            counter,
            configs
        ))
        save_counter(counter, Path("counter.yml"))


if __name__ == "__main__":
    main()