import logging
from logging.config import dictConfig
from pathlib import Path

from pydantic import AnyHttpUrl, BaseSettings, Field

from core.logger import LogConfig


class Redis(BaseSettings):
    HOST: str = "redis"
    PORT: int = 6379
    DATABASE: str = "1"
    JOB_RESULT_EX_TIME: int = 86400

    class Config:
        env_prefix = "REDIS_"

    def build_url(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.DATABASE}"


class RabbitMQ(BaseSettings):
    HOST: str = "rabbitmq"
    PORT: int = 5672
    LOGIN: str = "rabbit_mq_login"
    PASSWORD: str = "rabbit_mq_password"
    EXCHANGE: str = "wba-exchange"
    SENDER_KEY: str = "wba"

    class Config:
        env_prefix = "RABBITMQ_"


class WBAdapter(BaseSettings):
    MAX_RETRY_TIME: int = 10
    WB_OFFICIAL_API_ADV_URL = "https://advert-api.wb.ru/adv/v0"
    BASE_DIR = Path(__file__).absolute().parent.parent
    PROXY_URL: AnyHttpUrl | None = None
    LOG_FORMAT: str = "json"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_prefix = "WBADAPTER_"


class Settings(BaseSettings):
    PROJECT_NAME: str = "wb-adapter"
    REDIS: Redis = Redis()
    RABBITMQ: RabbitMQ = RabbitMQ()
    WBADAPTER: WBAdapter = WBAdapter()

    TOKEN_MANAGER_URL: AnyHttpUrl = Field(default="http://token_manager:8888")

    CONTEXT: str = "/api/ad"


settings = Settings()

log_config = LogConfig().dict()
for handler in log_config["handlers"].values():
    handler["formatter"] = settings.WBADAPTER.LOG_FORMAT


dictConfig(config=log_config)

logger: logging.Logger = logging.getLogger(log_config["logger_name"])

logger.setLevel(settings.WBADAPTER.LOG_LEVEL)
