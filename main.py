import time
import os
from src.config.config_loader import load_config
from src.config.time_utils import get_local_time
from src.integrations.facebook import fb_post, fb_update_bio
from src.utils.subtitle_handler import combine_episode_subtitles
from src.utils.frame_utils import generate_random_frame_crop
from src.utils.message_formatter import format_post_message
from src.services.frame_service import build_frame_file_path
from src.managers.episode_manager import update_episode_progress

def main():
    config = load_config("configs.yaml")
    current_time = get_local_time(config)

    fph = config.get("posting")["fph"]  
    current_frame = config.get("episodes")[config.get("current_episode") - 1].get("frame_iterator")

    for frame in range(current_frame + 1, current_frame + fph + 1):
        print(f"Posting frame {frame} of {current_frame + fph}", flush=True)
        frame_path = build_frame_file_path(frame_number=frame, config=config)          
        post_message = format_post_message(frame_number=frame, message=config.get("templates")["post_message"], config=config)
        
        post_id = fb_post(message=post_message, frame_path=frame_path, config=config)
        time.sleep(2)

        if config.get("posting")["posting_subtitles"]:
            subtitle_text = combine_episode_subtitles(frame_number=frame, config=config)
            if subtitle_text:
                fb_post(message=subtitle_text, parent_id=post_id, config=config)
        time.sleep(2)

        if config.get("posting")["random_crop"].get("enabled"):
            crop_path, crop_message = generate_random_frame_crop(frame_path=frame_path, frame_number=frame, config=config)
            fb_post(message=crop_message, frame_path=crop_path, parent_id=post_id, config=config)

        time.sleep(config.get("posting")["posting_interval"] * 60) # intervalo entre posts(em minutos)

    # update episode progress
    update_episode_progress(config=config)

    # update page biography
    biography_text = format_post_message(frame_number=frame, message=config.get("templates")["page_bio"], config=config)
    fb_update_bio(biography_text=biography_text, config=config)


    # save_logs(config=config)


if __name__ == "__main__":
    main()





    
