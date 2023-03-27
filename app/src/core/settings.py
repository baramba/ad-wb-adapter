from pydantic import BaseSettings


class Redis(BaseSettings):
    HOST: str
    PORT: int

    class Config:
        env_prefix = 'REDIS_'

    def build_url(self) -> str:
        return f'redis://{self.HOST}:{self.PORT}'


class Wildberries(BaseSettings):
    X_USER_ID: str
    X_SUPPLIER_ID: str
    X_SUPPLIER_ID_EXTERNAl: str
    WB_TOKEN: str


class RabbitMQ(BaseSettings):
    HOST: str
    PORT: int
    LOGIN: str
    PASSWORD: str
    EXCHANGE: str

    class Config:
        env_prefix = 'RABBITMQ_'


class Settings(BaseSettings):
    PROJECT_NAME: str
    REDIS: Redis = Redis()
    RABBITMQ: RabbitMQ = RabbitMQ()

    WILDBERRIES: Wildberries = Wildberries()


settings = Settings()
