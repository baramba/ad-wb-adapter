import logging

from pydantic import BaseModel


class LogConfig(BaseModel):
    logger_name: str = "ad-logger"
    log_format: str = "%(levelname)-6s %(path)-30s  %(message)s"
    # log_format: str = "%(asctime)s.%(msecs)03d %(levelname)-6s %(path)-30s  %(message)s"
    log_level: str = "INFO"

    version: int = 1
    disable_existing_loggers: bool = False

    formatters = {
        "default": {
            "class": "logging.Formatter",
            "format": log_format,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "root": {
            "class": "logging.Formatter",
            # "format": "%(asctime)s.%(msecs)03d %(levelname)-6s %(module)s.%(funcName)s  %(message)s",
            "format": "%(levelname)-6s %(module)s.%(funcName)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "ad.console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "root.console": {
            "class": "logging.StreamHandler",
            "formatter": "root",
            "stream": "ext://sys.stdout",
        },
    }
    root = {
        "level": "INFO",
        "formatter": ["root"],
        "handlers": ["root.console"],
    }

    loggers = {
        logger_name: {
            "handlers": ["ad.console"],
            "level": log_level,
            "propagate": False,
        },
        "arq": {
            "handlers": ["ad.console"],
            "level": log_level,
            "propagate": False,
        },
    }


logging_conf = LogConfig()


factory = logging.getLogRecordFactory()


# добавляем LogRecord  аттрибут path
def record_factory(*args: tuple, **kwargs: dict) -> logging.LogRecord:
    record = factory(*args, **kwargs)
    # превращаем /path/to/file.py в path.to.file
    path_parts = record.pathname.split("/")
    path_parts[-1] = path_parts[-1].split(".")[0]
    record.path = ".".join(path_parts[-4:])
    return record


logging.setLogRecordFactory(record_factory)
