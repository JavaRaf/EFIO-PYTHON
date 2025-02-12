from time import sleep
from scripts.frame_utils import (
    build_frame_file_path,
    random_crop_generator,
    get_total_episode_frames,
)
from scripts.load_configs import load_configs, load_frame_counter, save_frame_counter
from scripts.facebook import fb_posting, fb_update_bio, repost_images_in_album
from scripts.logger import get_logger, update_fb_log
from scripts.messages import format_message
from scripts.subtitle_handler import get_subtitle_message


logger = get_logger(__name__)


def post_frame(episode_number, frame_number, frame_path, configs, frame_counter):
    """Posta um frame."""
    post_message = format_message(
        episode_number,
        frame_number,
        configs.get("post_message"),
        frame_counter,
        configs,
    )
    post_id = fb_posting(post_message, frame_path)
    print(
        f"\n├──Episode {episode_number} frame {frame_number} has been posted",
        flush=True,
    )
    return post_id, post_message


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






def main():
    """Main function"""
    frame_counter = load_frame_counter()
    configs = load_configs()
    posts_data = []

    for i in range(1, configs.get("posting").get("fph") + 1):
        frame_number = frame_counter.get("frame_iterator") + i
        frame_path, episode_number, total_frames_in_episode_dir = build_frame_file_path(
            frame_number
        )

        if not total_frames_in_episode_dir:
            print("All frames in this episode were posted", flush=True)
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
            episode_number, frame_number, frame_path, configs, frame_counter
        )

        posts_data.append(
            {"post_id": post_id, "message": post_message, "frame_number": frame_number}
        )

        handle_subtitles(episode_number, frame_number, post_id, configs)
        handle_random_crop(frame_path, frame_number, post_id, configs)
        sleep(
            configs.get("posting").get("posting_interval")
        )  # adicione (* 60) para transformar em minutos

    if len(posts_data) > 0:
        update_fb_log(frame_counter, posts_data)
        update_bio_and_frame_counter(frame_counter, configs, len(posts_data))

        repost_images_in_album(posts_data, configs, frame_counter)


if __name__ == "__main__":
    main()
