from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Db_Conn, User
from db.session import get_db
from db.views.database import database_type, get_date_format
from schemas.database import Database, DatabaseType, DateFormat, ShowDatabase

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/databases/{db_conn_id}", response_model=ShowDatabase)
def list_databases(db_conn_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    db_conn = db.query(Db_Conn).filter(Db_Conn.id == db_conn_id).first()

    databaseConnection = DatabaseConnection(database_type=db_conn.db_type,
                                            username=db_conn.db_username,
                                            password=db_conn.db_password,
                                            host=db_conn.db_host,
                                            port=db_conn.db_port,
                                            schemas=db_conn.db_name
                                            )
    engine = databaseConnection.get_engine()
    insp = sa.inspect(engine)
    if engine.name == "postgresql":
        db_list = [db_conn.db_name]
    else:
        db_list = insp.get_schema_names()
    return {"databases": db_list}


@router.get("/databasetype",
            response_model=List[DatabaseType],
            deprecated=True,
            description="This will be deprecated in next version, Use /connection/connector-type .")
def get_databasetype(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    return database_type(db=db, user_id=current_user.id)


@router.get("/dateformat", response_model=List[DateFormat])
def get_dateformat(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    return get_date_format(db=db, user_id=current_user.id)
