from pathlib import Path
from time import sleep
from utils.tools.subtitles import frame_to_timestamp
from utils.tools.facebook import Facebook
from utils.tools.load_configs import load_configs, load_counter, save_counter
from utils.tools.logger import get_logger
from utils.tools.frame_util import return_frame_path, random_crop
from utils.tools.messages import format_message
from utils.tools.subtitles import get_subtitle_message

logger = get_logger(__name__)



def post_frame(
    frame_path: Path, 
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

    print(
        f"\n\n├──Episode {counter.get('current_episode', 0)} "
        f"frame {counter.get('frame_iterator', 0)} has been posted | "
        f"timestamp: {frame_to_timestamp(configs.get('episodes', {}).get(counter.get('current_episode', 0), {}).get('img_fps', 2), counter.get('frame_iterator', 0))}",
        flush=True,
    )
    sleep(2)
    return post_id

def post_subtitles(post_id: str, configs: dict, counter: dict, facebook: Facebook) -> None:

    if not configs.get("posting", {}).get("posting_subtitles", False):
        return None

    subtitle_message = get_subtitle_message(
        counter.get("frame_iterator", 0),
        counter.get("current_episode", 0),
        configs
    )
    if subtitle_message:
        facebook.post(subtitle_message, None, post_id)
        print(
            f"├──Subtitle has been posted",
            flush=True,
        )
        sleep(2)

def post_random_crop(post_id: str, frame_path: Path, configs: dict, facebook: Facebook) -> None:
    if not configs.get("posting", {}).get("random_crop", {}).get("enabled", False):
        return None
    
    crop_path, crop_message = random_crop(frame_path, configs)
    if crop_path and crop_message:
        facebook.post(crop_message, crop_path, post_id)
        print("└──Random Crop has been posted", flush=True)
        sleep(2)
    

def random_post():
    pass

def ordered_post(configs: dict, counter: dict, facebook: Facebook):
    for i in range(1, configs.get("posting", {}).get("fph", 15) + 1):

        current_frame: int = counter.get("frame_iterator", 0)
        current_episode: int = counter.get("current_episode", 0)
        
        message = format_message(configs.get("post_message", ""), counter, configs)
        frame_path: Path | None = return_frame_path(current_frame, current_episode)

        if not message:
            logger.error("Post message not found in configs")
            break  # apos o break, ele salva tudo na main e fecha o programa

        if not frame_path:
            logger.error(f"Frame {current_frame} not found in episode {current_episode}")
            break

        post_id = post_frame(frame_path, message, configs, counter, facebook)
        facebook.repost_to_album(message, frame_path, configs, counter)

        if not post_id:
            logger.error(f"Failed to post frame {current_frame} in episode {current_episode}")
            break
            
        post_subtitles(post_id, configs, counter, facebook)
        post_random_crop(post_id, frame_path, configs, facebook)

        counter["frame_iterator"] += 1
        counter["total_frames_posted"] += 1

def main():
    configs = load_configs(Path("configs.yml"))
    counter = load_counter(Path("counter.yml"))
    base_counter = load_counter(Path("counter.yml"))

    facebook = Facebook(configs, counter)

    if configs.get("random_posting", {}).get("enabled", False):
        random_post()
    else:
        ordered_post(configs, counter, facebook)

    if counter != base_counter:
        facebook.update_bio(format_message(configs.get("bio_message", ""), counter, configs))
        save_counter(counter, Path("counter.yml"))


if __name__ == "__main__":
    main()