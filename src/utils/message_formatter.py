from .frame_utils import convert_frame_to_timestamp
from .workflow_utils import get_workflow_execution_interval

def format_post_message(frame_number: int, message: str, config: dict) -> str:
    """
    Formata a mensagem do post com as variáveis apropriadas.
    
    Args:
        frame_number: Número do frame
        message_template: Template da mensagem
        config: Dicionário de configuração
        
    Returns:
        str: Mensagem formatada
    """
    template_vars = {
        "season": config.get("season"),
        "episode": config.get("current_episode"),
        "current_frame": frame_number,
        "episode_total_frames": config.get("episodes")[config.get("current_episode") - 1].get("episode_total_frames"),
        "frame_timestamp": convert_frame_to_timestamp(frame_number, config).strftime("%H:%M:%S.%f")[:-4],
        "img_fps": config.get("episodes")[config.get("current_episode") - 1].get("img_fps"),
        "fph": config.get("posting", {}).get("fph"),
        "page_name": config.get("your_page_name"),
        "execution_interval": get_workflow_execution_interval(),
        "total_frames_posted": config.get("total_frames_posted")
    }
    
    try:
        return message.format(**template_vars)
    except KeyError as e:
        print(f"Erro: Variável {e} não encontrada no template")
        return f"Erro ao formatar mensagem: variável {e} não encontrada" 