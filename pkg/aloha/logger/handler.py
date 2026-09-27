import time
from logging import StreamHandler
from logging.handlers import BaseRotatingHandler


class MultiProcessSafeDailyRotatingFileHandler(BaseRotatingHandler):
    """Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported
    """

    def __init__(
        self,
        filename: str,
        encoding="utf8",
        delay=False,
        utc=False,
        date_format="%Y-%m%d",
        filename_suffix="",
        **kwargs,
    ):
        self.utc = utc
        self.date_format = date_format
        self.filename_suffix = filename_suffix
        self.baseFilename = filename
        self.currentFileName = self._compute_fn()
        BaseRotatingHandler.__init__(self, filename, "a", encoding, delay)

    def shouldRollover(self, record):
        return self.currentFileName != self._compute_fn()

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.currentFileName = self._compute_fn()
        if not self.delay:
            self.stream = self._open()

    def _compute_fn(self):
        return (
            self.baseFilename.removesuffix(".log")
            + "_"
            + time.strftime(self.date_format, time.localtime())
            + self.filename_suffix
            + ".log"
        )

    def _open(self):
        return open(self.currentFileName, mode=self.mode, encoding=self.encoding)

    def close(self):
        """Closes the stream."""
        self.acquire()
        try:
            try:
                if self.stream:
                    try:
                        self.flush()
                    finally:
                        stream = self.stream
                        self.stream = None
                        if hasattr(stream, "close"):
                            # print('ttt')
                            stream.close()
            finally:
                # Issue #19523: call unconditionally to prevent a handler leak when delay is set
                StreamHandler.close(self)
        finally:
            self.release()
