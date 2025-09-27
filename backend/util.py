import logging
import sys
from os import getpid
from typing import Dict, Literal, TextIO

import psutil
import structlog

LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
EXTERNAL_LOGGERS = {
    "transformers", "uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"
}


def configure_logger(
    log_level: LOG_LEVELS = "INFO", render_json: bool = False, stream: TextIO = sys.stdout
):
    """
    Configures the logger for the package.

    Args:
        log_level: The log level to use for the logger. It should be one of the following strings:
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        render_json: Whether to render log messages in JSON format. Default is False.
        stream: The stream to write log messages to. Default is sys.stdout.
    """
    formatter = logging.Formatter('%(asctime)s %(filename)s %(levelname)s %(message)s')

    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)

    logging.basicConfig(
        # format="%(message)s",
        # format="%(asctime)s %(levelname)s %(filename)s %(message)s",
        level=log_level,
        # stream=stream
        handlers=[handler]
    )

    log_level_to_int = {
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "ERROR": logging.ERROR,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    render_processors = [structlog.dev.ConsoleRenderer()]
    if render_json:
        render_processors = [structlog.processors.JSONRenderer()]

    structlog.configure(
        context_class=dict,
        wrapper_class=structlog.make_filtering_bound_logger(log_level_to_int[log_level]),
        logger_factory=structlog.PrintLoggerFactory(stream),
        cache_logger_on_first_use=False,
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.dict_tracebacks,
            structlog.processors.CallsiteParameterAdder(
                [structlog.processors.CallsiteParameter.FILENAME,
                 structlog.processors.CallsiteParameter.LINENO
                 ],
            ),
        ] + render_processors,
    )

    for log_name in EXTERNAL_LOGGERS:
        logging.getLogger(log_name).setLevel(logging.WARNING)


def get_resource_utilization() -> Dict:
    """
    Returns the current resource utilization of the system.

    Returns:
        A dictionary containing the current resource utilization of the system.
    """

    process = psutil.Process(getpid())
    # A float representing the current system-wide CPU utilization as a percentage
    cpu_percent = process.cpu_percent()
    # A float representing process memory utilization as a percentage
    memory_percent = process.memory_percent()
    # Total physical memory
    total_memory_bytes = psutil.virtual_memory().total

    return {
        "cpu_utilization_percent": cpu_percent,
        "memory_utilization_percent": memory_percent,
        "total_memory_available_bytes": total_memory_bytes,
    }
