from scripts.logger import get_logger
from scripts.subtitle_handler import get_frame_timestamp
from scripts.workflow_utils import get_workflow_execution_interval

logger = get_logger(__name__)

# - {season}              : Número da temporada atual
# - {episode}             : Número do episódio atual
# - {current_frame}       : Número do frame atual
# - {episode_total_frames}: Total de frames do episódio
# - {frame_timestamp}     : Timestamp do frame
# - {fph}                 : Frames por intervalo
# - {page_name}           : Nome da página
# - {execution_interval}  : Intervalo entre postagens
# - {total_frames_posted} : Total de frames já postados

# - {img_fps}             :


def format_message(
    frame_number: int, message: str, frame_counter: dict, configs: dict
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
            "season": frame_counter["season"],
            "episode": frame_counter["current_episode"],
            "current_frame": frame_number,
            "episode_total_frames": configs.get("episodes")[
                frame_counter["current_episode"] - 1
            ]["episode_total_frames"],
            "frame_timestamp": get_frame_timestamp(
                frame_counter["current_episode"], frame_number
            ),
            "fph": configs.get("posting").get("fph"),
            "page_name": configs.get("your_page_name"),
            "execution_interval": get_workflow_execution_interval(),
            "total_frames_posted": frame_counter["total_frames_posted"],
            "img_fps": configs.get("episodes")[
                frame_counter["current_episode"] - 1
            ].get("img_fps"),
        }
        return message.format(**attrs)

    except Exception as e:
        logger.error(f"Error formatting message: {e}", exc_info=True)
        return message
