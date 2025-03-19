from scripts.frame_utils import get_total_episode_frames
from scripts.logger import get_logger
from scripts.subtitle_handler import frame_to_timestamp
from scripts.workflow_utils import get_workflow_execution_interval
from scripts.subtitle_handler import get_subtitle_message

logger = get_logger(__name__)

# - {season}              : Número da temporada atual
# - {episode}             : Número do episódio atual
# - {current_frame}       : Número do frame atual
# - {episode_total_frames}: Total de frames do episódio
# - {frame_timestamp}     : Timestamp do frame
# - {subtitle_text}       : Subtitle in frame tittle
# - {fph}                 : Frames por intervalo
# - {page_name}           : Nome da página
# - {execution_interval}  : Intervalo entre postagens
# - {posting_interval}    : Intervalo entre posts (in minutes) (default: 2 minutes) (format: integer)
# - {total_frames_posted} : Total de frames já postados

# - {img_fps}             :


def format_message(
    episode_number: int,
    frame_number: int,
    message: str,
    frame_counter: dict,
    configs: dict,
) -> str:
    """
    Formata uma mensagem com atributos de quadro e página.

    Substitui placeholders na mensagem com valores de atributos de quadro e página.

    Args:
        frame_number (int): Número do quadro atual
        message (str): Mensagem com placeholders

    Returns:
        str: Mensagem formatada
    """

    try:
        attrs = {
            "season": frame_counter.get("season", "N/A"),
            "episode": frame_counter.get("current_episode", "N/A"),
            "current_frame": frame_number,
            "episode_total_frames": get_total_episode_frames(episode_number),
            "frame_timestamp": frame_to_timestamp(
                frame_counter.get("current_episode", 0), frame_number
            ),
            "subtitle_text": (
                subtitle_message[0]
                if (
                    subtitle_message := get_subtitle_message(
                        episode_number, frame_number
                    )
                )
                else ""
            ),
            "fph": configs.get("posting", {}).get("fph", "N/A"),
            "page_name": configs.get("your_page_name", "N/A"),
            "execution_interval": get_workflow_execution_interval(),
            "total_frames_posted": frame_counter.get("total_frames_posted", 0),
            "img_fps": configs.get("episodes")
            .get(episode_number)
            .get("img_fps", "N/A"),
            "posting_interval": configs.get("posting", {}).get(
                "posting_interval", "N/A"
            ),
        }
        return message.format(**attrs)

    except KeyError as e:
        logger.error(f"Key error formatting message: {e}", exc_info=True)
        return ""
    except Exception as e:
        logger.error(f"Error formatting message: {e}", exc_info=True)
        return ""
