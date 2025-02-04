from time import sleep
from scripts.load_configs import load_frame_couter, update_frame_couter, load_configs
from scripts.frame_utils import build_frame_file_path
from scripts.facebook import fb_posting, fb_update_bio
from scripts.subtitle_handler import get_subtitle_message
from scripts.frame_utils import random_crop_generator
from scripts.messages import format_message



def main():
    frame_couter = load_frame_couter()
    configs = load_configs()
    frames_posted = 0


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

        frames_posted += 1
        
        if configs.get("posting").get("posting_subtitles"):
            subtitle_message = get_subtitle_message(episode_number, frame_number)
            if subtitle_message:
                fb_posting(subtitle_message, None, post_id)

                sleep(1)

        if configs.get("posting").get("random_crop").get("enabled"):
            crop_path, crop_message = random_crop_generator(frame_path, frame_number)
            fb_posting(crop_message, crop_path, post_id)

            sleep(1)


    if frames_posted != 0:
        
        frame_couter["frame_iterator"] += frames_posted
        frame_couter["total_frames_posted"] += frames_posted

        # Atualiza a biografia
        bio_message = format_message(frame_number, configs.get("bio_message"))
        fb_update_bio(bio_message)

        # Atualiza o episodio se todos os frames foram postados
        if frame_couter.get("frame_iterator") >= configs.get("episodes")[frame_couter.get("current_episode") - 1]["episode_total_frames"]:
            if frame_couter.get("current_episode") >= len(configs.get("episodes")):
                print("All episodes were posted!!!", flush=True)
            
            else:
                frame_couter["current_episode"] += 1
                frame_couter["frame_iterator"] = 0
        
        update_frame_couter(frame_couter)



if __name__ == "__main__":
    main()

