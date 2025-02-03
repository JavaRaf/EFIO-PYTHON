from time import sleep
from scripts.load_configs import load_frame_couter, update_frame_couter, load_configs
from scripts.frame_utils import build_frame_file_path
from scripts.facebook import fb_posting
from scripts.subtitle_handler import get_subtitle_message
from scripts.frame_utils import random_crop_generator
from scripts.messages import format_message



def main():
    frame_couter = load_frame_couter()
    configs = load_configs()


    for i in range(1, configs.get("posting").get("fph") + 1):
    
        frame_number = frame_couter.get("frame_iterator") + i
        frame_path, episode_number = build_frame_file_path(frame_number)


        if not frame_path.exists():
            print(f"Episode {episode_number} frame {frame_number} not found", flush=True)
            break
            # adicionar log de erro aqui
        

        print(f"Posting episode {episode_number} frame {frame_number}", flush=True)
        post_message = format_message(frame_number, configs.get("post_message"))
        post_id = fb_posting(post_message, frame_path)
        
        if configs.get("posting").get("posting_subtitles"):
            subtitle_message = get_subtitle_message(episode_number, frame_number)
            fb_posting(subtitle_message, None, post_id)

            sleep(1)

        if configs.get("posting").get("random_crop").get("enabled"):
            crop_path, crop_message = random_crop_generator(frame_path, frame_number)
            fb_posting(crop_message, crop_path, post_id)

            sleep(1)




if __name__ == "__main__":
    main()

