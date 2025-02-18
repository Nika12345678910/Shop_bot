from environs import Env
from dataclasses import dataclass


@dataclass
class Database:
    user: str = None
    database: str = None
    password: str = None
    host: str = None
    port: str = None

    def connect_sqlite(self):
        return f"sqlite+aiosqlite:///{self.database}"

    def connect_postgresql(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class TgBot:
    token: str
    admin_id: list[int]


@dataclass
class Payment:
    PayMaster_token: str


@dataclass
class Config:
    tg_bot: TgBot
    db: Database
    buy: Payment


def load_config(path: str | None = None):
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env("TOKEN"),
            admin_id=list(map(int, env.list('ADMIN_ID')))),
        buy=Payment(
            PayMaster_token=env("PAY_MASTER_TOKEN")
        ),
        db=Database(
            user=env("USER"),
            database=env("DATABASE"),
            password=env("PASSWORD"),
            host=env("HOST"),
            port=env("PORT")
        ))
