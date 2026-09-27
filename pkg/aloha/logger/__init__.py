from ..settings import SETTINGS
from .logger import get_formatter, get_logger, getLogger

LOG = get_logger(
    level=SETTINGS.config.get("deploy", {}).get("log_level", 10),  # 10 = logging.DEBUG
    log_format_file=SETTINGS.config.get("deploy", {}).get("log_format_file", "json"),
    log_format_stream=SETTINGS.config.get("deploy", {}).get("log_format_stream", "plain"),
)
__all__ = ("LOG", "getLogger", "get_formatter", "get_logger")
