from apis.base import api_router
from db.session import get_db
from typing import Any
from typing import Generator
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import warnings
import sys

warnings.simplefilter("ignore")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# this is to include backend dir in sys.path so that we can import from db,main.py

# from db.base import Base

Base = automap_base()


def start_application():
    app = FastAPI()
    app.include_router(api_router)
    return app


SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
SQLALCHEMY_DATABASE_URL = "mysql://root:password@localhost:3306/rebiz"
# DATABASE_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_DB}"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=1800)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_script(engine):
    # print('curdir--', os.path.join(os.getcwd(), 'tests'))
    cur_path = os.path.join(os.getcwd(), 'tests')
    with open(os.path.join(cur_path, 'rebiz_test_db.sql'), 'r') as sql_file:
        sql_script = sql_file.read()

    # print(sql_script)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.executescript(sql_script)
    # cursor.commit()
    insert_user_group = "INSERT INTO USER_GROUP(ID, NAME, DESCRIPTION) VALUES(1000, 'admin', 'admin')"
    cursor.execute(insert_user_group)
    cursor.close()
    connection.commit()


def remove_test_db(db_file):
    print(os.path.join(os.getcwd(), 'testdb.db'))
    # os.remove(os.path.join(os.getcwd(), 'testdb.db'))


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.prepare(autoload_with=engine)
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)  # Create the tables.
    # print(Base.metadata.tables.values())
    run_script(engine)
    _app = start_application()
    yield _app
    # remove_test_db("test")
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(
    app: FastAPI, db_session: SessionTesting
) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
