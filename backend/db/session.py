from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_recycle=1800,
                       pool_pre_ping=True,
                       pool_size=10,
                       max_overflow=10,
                       echo=False)


def get_db() -> Generator:
    SessionLocal = sessionmaker(autocommit=False,
                                autoflush=False,
                                bind=engine)
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
