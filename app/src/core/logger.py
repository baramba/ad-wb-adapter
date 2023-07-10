import logging

from pydantic import BaseModel


class LogConfig(BaseModel):
    logger_name: str = "wbadapter-logger"
    log_format: str = "%(asctime)s.%(msecs)03d %(levelname)-6s [%(correlation_id)s] %(logger_name)-30s  %(message)s"
    log_level: str = "INFO"
    version: int = 1
    disable_existing_loggers: bool = False

    logger = {
        "handlers": ["ad"],
        "level": log_level,
        "propagate": False,
    }

    filters = {
        "extra_log_params": {"()": "core.utils.filters.ExtraParamsFilter"},
    }

    formatters = {
        "default": {
            "()": "core.utils.formatter.VerboseJSONFormatter",
        },
        "text": {
            "class": "logging.Formatter",
            "format": log_format,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "core.utils.formatter.VerboseJSONFormatter",
        },
        "root": {
            "()": "core.utils.formatter.VerboseJSONFormatter",
        },
    }

    handlers = {
        "ad": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["extra_log_params"],
            "stream": "ext://sys.stdout",
        },
        "root": {
            "class": "logging.StreamHandler",
            "formatter": "root",
            "stream": "ext://sys.stdout",
        },
    }

    root = {
        "level": "INFO",
        "formatter": "root",
        "handlers": ["root"],
    }

    loggers = {
        logger_name: logger,
        "arq": logger,
        "uvicorn": logger,
        "gunicorn": logger,
        "gunicorn.access": logger,
        "gunicorn.error": logger,
    }


factory = logging.getLogRecordFactory()


# добавляем LogRecord  аттрибут logger_name
def record_factory(*args: tuple, **kwargs: dict) -> logging.LogRecord:
    record = factory(*args, **kwargs)
    # превращаем /path/to/file.py в path.to.file
    path_parts = record.pathname.split("/")
    path_parts[-1] = path_parts[-1].split(".")[0]
    record.logger_name = ".".join(path_parts[-3:])

    return record


logging.setLogRecordFactory(record_factory)
