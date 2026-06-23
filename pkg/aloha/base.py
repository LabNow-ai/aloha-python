from abc import ABC

from .logger import LOG
from .settings import SETTINGS


class BaseModule(ABC):
    """
    Abstract base class for all modules in aloha.

    Provides common attributes to all modules:
    - config: Global configuration object
    - LOG: Logger instance
    """

    config = SETTINGS.config
    LOG = LOG
