import structlog


class CustomFormatter(structlog.Formatter):
    """structlog colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            structlog.DEBUG: self.grey + self.fmt + self.reset,
            structlog.info: self.blue + self.fmt + self.reset,
            structlog.WARNING: self.yellow + self.fmt + self.reset,
            structlog.ERROR: self.red + self.fmt + self.reset,
            structlog.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = structlog.Formatter(log_fmt)
        return formatter.format(record)
