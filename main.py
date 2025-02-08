from time import sleep

from scripts.facebook import fb_posting, fb_update_bio
from scripts.frame_utils import build_frame_file_path, random_crop_generator
from scripts.load_configs import load_configs, load_frame_couter, update_frame_couter
from scripts.logger import get_logger
from scripts.messages import format_message
from scripts.subtitle_handler import get_subtitle_message

logger = get_logger(__name__)


def main():
    frame_couter = load_frame_couter()
    configs = load_configs()
    frames_posted = 0

    for i in range(1, configs.get("posting").get("fph") + 1):
        frame_number = frame_couter.get("frame_iterator") + i
        frame_path, episode_number, length_of_episode = build_frame_file_path(
            frame_number
        )

        if frame_number > length_of_episode:
            print(f"Episode {episode_number} finished", flush=True)
            break

        if not frame_path.exists():
            logger.error(
                f"Episode {episode_number} Frame {frame_number} not found",
                exc_info=True,
            )
            break

        post_message = format_message(
            frame_number, configs.get("post_message"), frame_couter, configs
        )
        post_id = fb_posting(post_message, frame_path)

        print(f"Posting episode {episode_number} frame {frame_number}", flush=True)

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

        # sleep(configs.get("posting").get("posting_interval"))

    if frames_posted != 0:
        frame_couter["frame_iterator"] += frames_posted
        frame_couter["total_frames_posted"] += frames_posted

        # Atualiza a biografia
        bio_message = format_message(
            frame_number, configs.get("bio_message"), frame_couter, configs
        )
        fb_update_bio(bio_message)

        # Atualiza o episodio se todos os frames foram postados
        if (
            frame_couter.get("frame_iterator")
            >= configs.get("episodes")[frame_couter.get("current_episode") - 1][
                "episode_total_frames"
            ]
        ):
            frame_couter["current_episode"] += 1
            frame_couter["frame_iterator"] = 0

            if frame_couter.get("current_episode") >= len(configs.get("episodes")):
                print("All episodes were posted!!!", flush=True)

        update_frame_couter(frame_couter)


if __name__ == "__main__":
    main()
