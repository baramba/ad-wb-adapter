from pydantic import BaseModel


class LogConfig(BaseModel):
    logger_name: str = "ad-logger"
    log_format: str = (
        "%(asctime)s.%(msecs)03d %(levelname)-6s %(module)s.%(funcName)s  %(message)s"
    )
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
            "format": "%(asctime)s.%(msecs)03d %(levelname)-6s %(module)s.%(funcName)s  %(message)s",
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
