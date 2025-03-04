from datetime import datetime, timedelta, timezone
import time
from scripts.load_configs import load_configs
from scripts.logger import get_logger

logger = get_logger(__name__)


def get_local_time() -> str:
    """
    Retorna a hora local usando o offset do config.yaml

    Args:
        configs (dict): Dicionário de configuração contendo TIME_ZONE_OFFSET

    Returns:
        str: String datetime formatada (YYYY-MM-DD HH:MM:SS), vazia se ocorrer erro
    """
    try:
        if "timezone_offset" not in load_configs().keys():
            raise KeyError("timezone_offset não encontrado nas configurações")

        time_zone = (
            load_configs()["timezone_offset"]
            if load_configs()["timezone_offset"]
            else 0
        )
        return datetime.now(timezone(timedelta(hours=int(time_zone)))).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except (KeyError, ValueError, TypeError) as error:
        logger.error(f"Erro ao processar timezone: {error}", exc_info=True)

    return ""


def sleeper_function(seconds: int) -> None:
    """
    Mostra um timer de contagem regressiva para o próximo post.

    Args:
        seconds (int): Tempo em segundos

    Returns:
        None
    """
    for i in range(seconds, 0, -1):
        print(f"\n\tWaiting for the next post: {i:2d}", end="\033[F", flush=True)
        time.sleep(1)
    
    print("\n" + " " * 50, end="\r", flush=True)


