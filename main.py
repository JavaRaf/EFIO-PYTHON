from time import sleep
from scripts.facebook import fb_posting, fb_update_bio
from scripts.frame_utils import build_frame_file_path, random_crop_generator, get_total_episode_frames
from scripts.load_configs import load_configs, load_frame_counter, update_frame_counter
from scripts.logger import get_logger
from scripts.messages import format_message
from scripts.subtitle_handler import get_subtitle_message


logger = get_logger(__name__)


def post_frame(episode_number, frame_number, frame_path, configs, frame_counter):
    """Posta um frame."""
    post_message = format_message(episode_number, frame_number, configs.get("post_message"), frame_counter, configs)
    post_id = fb_posting(post_message, frame_path)
    print(
        f"\n├──Episode {episode_number} frame {frame_number} has been posted",
        flush=True,
    )
    return post_id


def handle_subtitles(episode_number, frame_number, post_id, configs):
    """Posta legendas"""
    if configs.get("posting").get("posting_subtitles"):
        subtitle_message = get_subtitle_message(episode_number, frame_number)
        if subtitle_message:
            fb_posting(subtitle_message, None, post_id)
            print("├──Subtitle has been posted", flush=True)
            sleep(1)


def handle_random_crop(frame_path, frame_number, post_id, configs):
    """Posta um recorte aleatório"""
    if configs.get("posting").get("random_crop").get("enabled"):
        crop_path, crop_message = random_crop_generator(frame_path, frame_number)
        fb_posting(crop_message, crop_path, post_id)
        print("└──Random Crop has been posted", flush=True)
        sleep(1)

def update_bio_and_frame_counter(episode_number, frame_counter, configs, frames_posted):
    """Atualiza a bio e o contador de frames"""
    frame_counter["frame_iterator"] += frames_posted
    frame_counter["total_frames_posted"] += frames_posted
    bio_message = format_message(episode_number, frame_counter["frame_iterator"], configs.get("bio_message"), frame_counter, configs)
    fb_update_bio(bio_message)
    if frame_counter["frame_iterator"] >= get_total_episode_frames(episode_number):
        if frame_counter["current_episode"] >= len(configs["episodes"]):
            print("All episodes were posted!!!", flush=True)
        frame_counter["current_episode"] += 1
        frame_counter["frame_iterator"] = 0
    update_frame_counter(frame_counter)


def main():
    """Main function"""
    frame_counter = load_frame_counter()
    configs = load_configs()
    frames_posted = 0

    for i in range(1, configs.get("posting").get("fph") + 1):
        frame_number = frame_counter.get("frame_iterator") + i
        frame_path, episode_number, length_of_episode = build_frame_file_path(
            frame_number
        )

        if not frame_path or not episode_number or not length_of_episode:
            logger.error("Error building frame path", exc_info=True)
            break

        if not frame_path.exists():
            logger.error(
                f"Episode {episode_number} Frame {frame_number} not found",
                exc_info=True,
            )
            break

        if frame_number > length_of_episode:
            print(f"Episode {episode_number} finished", flush=True)
            break

        post_id = post_frame(
            episode_number, frame_number, frame_path, configs, frame_counter
        )
        frames_posted += 1
        handle_subtitles(episode_number, frame_number, post_id, configs)
        handle_random_crop(frame_path, frame_number, post_id, configs)
        sleep(configs.get("posting").get("posting_interval") * 60) # adicione (* 60) para minutos

    if frames_posted != 0:
        update_bio_and_frame_counter(episode_number, frame_counter, configs, frames_posted)

if __name__ == "__main__":
    main()
