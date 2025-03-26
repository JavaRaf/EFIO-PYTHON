from utils.tools.logger import get_logger
from utils.tools.frame_util import counter_frames_from_this_episode
from utils.tools.subtitles import frame_to_timestamp, get_subtitle_message
from utils.tools.workflow import get_workflow_execution_interval

logger = get_logger(__name__)

def format_message(message: str, frame_number: int, total_frames_posted: int, frame_counter: dict, configs: dict) -> str:
    """
    Formata uma mensagem com atributos de quadro e página.

    Substitui placeholders na mensagem com valores de atributos de quadro e página.

    Args:
        episode_number (int): Número do episódio
        frame_number (int): Número do quadro atual
        message (str): Mensagem com placeholders
        frame_counter (dict): Contador de quadros contendo dados do episódio
        configs (dict): Configurações gerais

    Returns:
        str: Mensagem formatada ou string vazia em caso de erro
    """

    try:
        # Obtendo valores seguros com `.get()` para evitar KeyError
        season = frame_counter.get("season", "N/A")
        current_episode = frame_counter.get("current_episode", "N/A")
        episode_total_frames = counter_frames_from_this_episode(current_episode)
        frame_timestamp = frame_to_timestamp(current_episode, frame_number)
        # Evita erro caso "episodes" ou "episode_number" não existam
        episode_config = configs.get("episodes", {}).get(current_episode, {})
        img_fps = episode_config.get("img_fps", "N/A")

        # Evita erro caso "posting" não exista
        posting_config = configs.get("posting", {})
        fph = posting_config.get("fph", "N/A")
        posting_interval = posting_config.get("posting_interval", "N/A")

        page_name = configs.get("page_name", "N/A")
        execution_interval = get_workflow_execution_interval()

        # Obtendo legenda apenas uma vez (evita atribuição dentro do dicionário)
        subtitle_message = get_subtitle_message(frame_number, current_episode, configs)
        subtitle_text = subtitle_message if subtitle_message else ""
        print(subtitle_text)

        # Dicionário de placeholders
        attrs = {
            "season": season,
            "episode": current_episode,
            "current_frame": frame_number,
            "episode_total_frames": episode_total_frames,
            "frame_timestamp": frame_timestamp,
            "subtitle_text": subtitle_text,
            "fph": fph,
            "page_name": page_name,
            "execution_interval": execution_interval,
            "total_frames_posted": total_frames_posted,
            "img_fps": img_fps,
            "posting_interval": posting_interval,
        }

        return message.format(**attrs)

    except Exception as e:
        logger.error(f"Erro ao formatar a mensagem: {e}", exc_info=True)
        return ""
    