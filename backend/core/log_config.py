from typing import ClassVar

from pydantic import BaseModel


class LogConfig(BaseModel):
    """structlog configuration to be set for the server"""

    LOGGER_NAME: str = "mycoolapp"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "NOTSET"

    # structlog config
    version: ClassVar[int] = 1
    disable_existing_loggers: ClassVar[bool] = False
    formatters: ClassVar[dict] = {
        "default": {
            "()": "uvicorn.structlog.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: ClassVar[dict] = {
        "default": {
            "formatter": "default",
            "class": "structlog.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: ClassVar[dict] = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }
