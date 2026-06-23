from ..settings import SETTINGS
from .logger import get_logger, getLogger

LOG = get_logger(
    level=SETTINGS.config.get("deploy", {}).get("log_level", 10),  # 10 = logging.DEBUG
)
__all__ = ("LOG", "get_logger", "getLogger")
