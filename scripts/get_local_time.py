from datetime import datetime, timedelta, timezone
import time
from scripts.load_configs import load_configs
from scripts.logger import get_logger

logger = get_logger(__name__)


def get_local_time() -> str:
    """
    Returns the local time using the offset from config.yaml

    Args:
        configs (dict): Configuration dictionary containing TIME_ZONE_OFFSET

    Returns:
        str: Formatted datetime string (YYYY-MM-DD HH:MM:SS), empty if error occurs
    """
    try:
        if "timezone_offset" not in load_configs().keys():
            raise KeyError("timezone_offset not found in configurations")

        time_zone = (
            load_configs()["timezone_offset"]
            if load_configs()["timezone_offset"]
            else 0
        )
        return datetime.now(timezone(timedelta(hours=int(time_zone)))).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except (KeyError, ValueError, TypeError) as error:
        logger.error(f"Error processing timezone: {error}", exc_info=True)

    return ""


