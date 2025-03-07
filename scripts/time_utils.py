from datetime import datetime, timedelta, timezone

from scripts.logger import get_logger

logger = get_logger(__name__)


def get_local_time(configs: dict) -> str:
    """
    Retorna a hora local usando o offset do config.yaml

    Args:
        configs (dict): Dicionário de configuração contendo TIME_ZONE_OFFSET

    Returns:
        str: String datetime formatada (YYYY-MM-DD HH:MM:SS), vazia se ocorrer erro
    """
    try:
        if "timezone_offset" not in configs:
            raise KeyError("timezone_offset não encontrado nas configurações")

        time_zone = configs["timezone_offset"] if configs["timezone_offset"] else 0
        return datetime.now(timezone(timedelta(hours=int(time_zone)))).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except (KeyError, ValueError, TypeError) as error:
        logger.error(f"Erro ao processar timezone: {error}", exc_info=True)

    return ""
