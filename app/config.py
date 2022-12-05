from pathlib import Path
from typing import NamedTuple

from environs import Env


class Config(NamedTuple):
    __env = Env()
    __env.read_env()

    BASE_DIR = Path(__name__).resolve().parent.parent
    LOCALES_PATH = 'locales'

    BOT_TOKEN = __env.str("BOT_TOKEN")

    ADMINS = __env.list("ADMIN_ID")

    CHANNEL_TITLE = __env.str("CHANNEL_TITLE")[1:-1]
    CHANNEL_LINK = __env.str("CHANNEL_LINK")
    CHANNEL_FEEDBACK_USERNAME = __env.str("CHANNEL_FEEDBACK_USERNAME")
    GROUP_ID = __env.str("GROUP_ID")

    POSTGRES_DB = __env.str("POSTGRES_DB")
    POSTGRES_USER = __env.str("POSTGRES_USER")
    POSTGRES_PASSWORD = __env.str("POSTGRES_PASSWORD")
    DB_PORT = __env.str("DB_PORT")
    DB_HOST = __env.str("DB_HOST")

    POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
