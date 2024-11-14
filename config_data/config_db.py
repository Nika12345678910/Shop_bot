from dataclasses import dataclass
from environs import Env


@dataclass
class DataBaseConfig:
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DATABASE: str

    def create_url(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"


@dataclass
class Config:
    db: DataBaseConfig



def load_config_db():
    env = Env()
    env.read_env()
    return Config(
        db=DataBaseConfig(
            DATABASE=env('DATABASE'),
            HOST=env('HOST'),
            USER=env('USER'),
            PASSWORD=env('PASSWORD'),
            PORT=env('PORT')
        )
    )