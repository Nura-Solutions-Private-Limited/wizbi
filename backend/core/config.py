import os
from pathlib import Path

from sqlalchemy.engine import URL

import constants


class Settings:
    PROJECT_NAME: str = "WizBi"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DIR: os.PathLike[str] = Path(__file__).parent.parent

    DB_USER: str = constants.DB_USER
    DB_PASSWORD: str = constants.DB_PASSWORD
    DB_SERVER: str = constants.DB_SERVER
    DB_PORT: str = constants.DB_PORT
    DB_DB: str = constants.DB_DB
    DB_DRIVER: str = constants.DB_DRIVER

    DATABASE_URL = URL.create(DB_DRIVER,
                              username=DB_USER,
                              password=DB_PASSWORD,
                              host=DB_SERVER,
                              port=DB_PORT,
                              database=DB_DB)
    # DATABASE_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_DB}"

    SECRET_KEY: str = constants.SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins

    TEST_USER_EMAIL = "test@example.com"


settings = Settings()
