import logging
from logging.config import dictConfig
from pathlib import Path
from pydantic import AnyHttpUrl, BaseSettings, Field
from core.logger import logging_conf


class Redis(BaseSettings):
    HOST: str = "redis"
    PORT: int = 6379

    class Config:
        env_prefix = "REDIS_"

    def build_url(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}"


class Wildberries(BaseSettings):
    X_USER_ID: str = ""
    X_SUPPLIER_ID: str = ""
    X_SUPPLIER_ID_EXTERNAl: str = ""
    WB_TOKEN: str = ""


class RabbitMQ(BaseSettings):
    HOST: str = "rabbitmq"
    PORT: int = 5672
    LOGIN: str = "rabbit_mq_login"
    PASSWORD: str = "rabbit_mq_password"
    EXCHANGE: str = "exchange"
    SENDER_KEY: str = "wba"

    class Config:
        env_prefix = "RABBITMQ_"


class Settings(BaseSettings):
    PROJECT_NAME: str = "wb-adapter"
    REDIS: Redis = Redis()
    RABBITMQ: RabbitMQ = RabbitMQ()
    WILDBERRIES: Wildberries = Wildberries()
    LOG_LEVEL: str = "INFO"
    BASE_DIR = Path(__file__).absolute().parent.parent
    TOKEN_MANAGER_URL: AnyHttpUrl = Field(default="http://token_manager:8888")


settings = Settings()

dictConfig(logging_conf.dict())

logger: logging.Logger = logging.getLogger(logging_conf.logger_name)
logger.setLevel(settings.LOG_LEVEL)
