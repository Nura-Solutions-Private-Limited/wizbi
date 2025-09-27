from typing import Generator

from airflow.providers.mysql.hooks.mysql import MySqlHook

# from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

mysql_hook = MySqlHook(mysql_conn_id="wizbi")
engine = mysql_hook.get_sqlalchemy_engine()
# engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=1800)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Rebiz database session


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
