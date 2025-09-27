from typing import Dict, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.enums import DbType
from db.models.models import Db_Conn, Pipeline, User
from db.session import get_db
from db.views.metadata import Metadata
from schemas.database import DatabaseConn
from schemas.metadata import DataType, ShowMetadata

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.get("/metadata/{pipeline_id}", response_class=JSONResponse)
def generate_metadata(pipeline_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate metadata from source database
    '''
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if pipeline:
        source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()
        if source_db_conn:
            if source_db_conn.db_type == "sqlserver":
                schema = source_db_conn.db_name
            else:
                schema = pipeline.source_schema_name

            engine = None
            if str(source_db_conn.db_type).upper() not in [DbType.S3.value,
                                                           'Amazon S3',
                                                           'AMAZON S3',
                                                           DbType.LFS.value,
                                                           'Local System',
                                                           'LOCAL SYSTEM',
                                                           DbType.RESTAPI.value]:
                datbaseconnection = DatabaseConnection(database_type=source_db_conn.db_type,
                                                       username=source_db_conn.db_username,
                                                       password=source_db_conn.db_password,
                                                       host=source_db_conn.db_host,
                                                       port=source_db_conn.db_port,
                                                       # schemas=pipeline.source_schema_name
                                                       # schemas=source_db_conn.db_name
                                                       schemas=schema)
                engine = datbaseconnection.get_engine()
            metadata = Metadata(pipeline_id=pipeline_id,
                                db=db,
                                chosen_schema=pipeline.source_schema_name,
                                database_type=source_db_conn.db_type,
                                engine=engine,
                                )

            data = metadata.get_db_metadata()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Invalid pipeline, source db connection not found")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

    return data


@router.post("/metadata/{pipeline_id}", response_model=ShowMetadata)
def save_metadata(pipeline_id: int,
                  userInput: Dict,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    '''
    Store metadata given metadata
    '''
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if pipeline:
        metadata = Metadata(pipeline_id=pipeline.id, db=db)
        soure_db_mapping = metadata.save_user_input(user_input=userInput)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

    return {"pipeline_id": pipeline_id, "source_db_mapping_id": soure_db_mapping.id}


'''
@router.get("/datatypes", response_model=List[str])
def get_datatypes(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):

    Get all data type supported by rebiz mysql database

    metadata = Metadata(db=db)
    datatpes = metadata.get_datatypes()

    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

    return datatpes
'''


@router.get("/datatypes/{pipeline_id}", response_model=List[str])
def get_datatypes(pipeline_id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user_from_token)):
    '''
    Get all data type supported by the destination datawarehouse
      '''
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if pipeline:
        dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()
        try:
            metadata = Metadata(db=db, database_type=dest_db_conn.db_type)
            data_types = metadata.get_datatypes()
            return data_types
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Invalid pipeline, source db connection not found: {ex}")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")


@router.get("/database-datatypes", response_model=List[DataType])
def get_database_datatypes(db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user_from_token)):
    '''
    Get all data type supported by the pandas dataframe
    '''

    data_types = [
        {"name": "Integer", "value": "int64", "format": "int64", "description": "Integer data type."},
        {"name": "Float", "value": "float64", "format": "float64", "description": "Float data type."},
        {"name": "String", "value": "string", "format": "string", "description": "String data type."},
        {"name": "Date", "value": "datetime64[s]", "format": "datetime64[s]", "description": "Date data type."},
        {
            "name": "Datetime",
            "value": "datetime64[us]",
            "format": "datetime64[us]",
            "description": "Datetime data type.",
        },
        {
            "name": "Timestamp",
            "value": "datetime64[ns]",
            "format": "datetime64[ns]",
            "description": "Timestamp data type.",
        },
        {"name": "Boolean", "value": "bool", "format": "boolean", "description": "Boolean data type."},
        {"name": "Decimal", "value": "decimal", "format": "decimal", "description": "Decimal data type."},
    ]

    return data_types
    # if connection_id:
    #     dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == connection_id).first()
    #     try:
    #         metadata = Metadata(db=db, database_type=dest_db_conn.db_type)
    #         data_types = metadata.get_datatypes()
    #         return data_types
    #     except Exception as ex:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail=f"Invalid pipeline, source db connection not found: {ex}")
    # else:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid database connection")
