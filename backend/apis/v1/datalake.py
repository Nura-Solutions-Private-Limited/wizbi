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
from db.views.datalake import iceberg_table_preview, validate_iceberg_table
from db.views.dbthelper import DbtHelper
from schemas.datalake import (
    DbtProject,
    DuckDbDbt,
    DuckDbDbtConnStatus,
    IcebergTableConnection,
    IcebergTablePreview,
    IcebergTableValResponse,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/validate-iceberg-table", response_model=IcebergTableValResponse)
def validate_iceberg_table_connection(icebergTableConnection: IcebergTableConnection,
                                      db: Session = Depends(get_db),
                                      current_user: User = Depends(get_current_user_from_token)):
    return validate_iceberg_table(db=db, user_id=current_user.id, icebergTableConnection=icebergTableConnection)


@router.get("/iceberg-table-preview/{pipeline_id}", response_model=List[IcebergTablePreview])
def get_table_preview(pipeline_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    return iceberg_table_preview(db=db, user_id=current_user.id, pipeline_id=pipeline_id)


@router.post('/setup-dbt-project/{pipeline_id}', response_model=DbtProject)
def setup_dbt_project(pipeline_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Setup dbt project for the given pipeline
    '''
    dbtHelper = DbtHelper()
    return dbtHelper.setup_project(db=db,
                                   user_id=current_user.id,
                                   pipeline_id=pipeline_id)


@router.post('/validate-duckdb-dbt-setting', response_model=DuckDbDbtConnStatus)
def validate_duckdb_dbt_setting(duckDbDbt: DuckDbDbt,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user_from_token)):
    return {"status": True}
