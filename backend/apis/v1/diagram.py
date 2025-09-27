import structlog
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.auth.dbconnection import DatabaseConnection
from db.models.models import Db_Conn, Pipeline, User
from db.session import get_db
from db.views.diagram import Diagram
from schemas.database import DatabaseConn

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/erdiagram/{pipeline_id}", response_class=FileResponse)
def generate_er_diagram(pipeline_id: int,
                        source_target: str = Query("S",
                                                   description="Source or Destination database (S/D)", ),
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate er diagram from database for pipeline_id and return it
    '''
    # Query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if source_target.upper() == 'S':
        # Query source database connection
        source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

        # Create database connection
        databaseConnection = DatabaseConnection(database_type=source_db_conn.db_type,
                                                username=source_db_conn.db_username,
                                                password=source_db_conn.db_password,
                                                host=source_db_conn.db_host,
                                                port=source_db_conn.db_port,
                                                # schemas=pipeline.source_schema_name
                                                schemas=source_db_conn.db_name)
        chosen_schema = pipeline.source_schema_name
        type="source"
    if source_target.upper() == 'D':
        # Query destination database connection
        dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()

        # Create database connection
        databaseConnection = DatabaseConnection(database_type=dest_db_conn.db_type,
                                                username=dest_db_conn.db_username,
                                                password=dest_db_conn.db_password,
                                                host=dest_db_conn.db_host,
                                                port=dest_db_conn.db_port,
                                                schemas=pipeline.dest_schema_name)
        chosen_schema = pipeline.dest_schema_name
        type="dest"
    engine = databaseConnection.get_engine()
    diagram = Diagram(engine=engine,
                      schema=chosen_schema,
                        type=type)
    image_file = diagram.generate_diagram()

    return FileResponse(image_file)

#generate json for source diagram

@router.post("/source-diagram-json/{pipeline_id}", response_class=FileResponse)
def generate_source_diagram_json(pipeline_id: int,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate er diagram from database for pipeline_id and return it
    '''
    # Query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    # Query source database connection
    source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

    # Create database connection
    databaseConnection = DatabaseConnection(database_type=source_db_conn.db_type,
                                            username=source_db_conn.db_username,
                                            password=source_db_conn.db_password,
                                            host=source_db_conn.db_host,
                                            port=source_db_conn.db_port,
                                            schemas=source_db_conn.db_name)
    chosen_schema = pipeline.source_schema_name
    engine = databaseConnection.get_engine()
    db_type=source_db_conn.db_type
    diagram = Diagram(engine=engine,
                      schema=chosen_schema,
                      db_type=db_type,
                      type="source")

    json_file= diagram.generate_diagram_json()

    return FileResponse(json_file)

#generate json for destinaton diagram
@router.post("/dest-diagram-json/{pipeline_id}", response_class=FileResponse)
def generate_dest_diagram_json(pipeline_id: int,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate er diagram from database for pipeline_id and return it
    '''
    # Query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    
    # Query destination database connection
    dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()

    # Create database connection
    databaseConnection = DatabaseConnection(database_type=dest_db_conn.db_type,
                                            username=dest_db_conn.db_username,
                                            password=dest_db_conn.db_password,
                                            host=dest_db_conn.db_host,
                                            port=dest_db_conn.db_port,
                                            schemas=pipeline.dest_schema_name)
    chosen_schema = pipeline.dest_schema_name

    engine = databaseConnection.get_engine()
    db_type=dest_db_conn.db_type

    diagram = Diagram(engine=engine,
                      schema=chosen_schema,
                      db_type=db_type,
                      type="dest")

    json_file= diagram.generate_diagram_json()

    return FileResponse(json_file)


@router.post("/source-erdiagram/{pipeline_id}", response_class=FileResponse)
def generate_source_er_diagram(pipeline_id: int,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate er diagram from database for pipeline_id and return it
    '''
    # Query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    # Query source database connection
    source_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_source_id).first()

    # Create database connection
    databaseConnection = DatabaseConnection(database_type=source_db_conn.db_type,
                                            username=source_db_conn.db_username,
                                            password=source_db_conn.db_password,
                                            host=source_db_conn.db_host,
                                            port=source_db_conn.db_port,
                                            schemas=source_db_conn.db_name)
    chosen_schema = pipeline.source_schema_name
    engine = databaseConnection.get_engine()
    db_type=source_db_conn.db_type
    diagram = Diagram(engine=engine,
                      schema=chosen_schema,
                      db_type=db_type,
                      type="source")

    image_file = diagram.generate_diagram()

    return FileResponse(image_file)


@router.post("/dest-erdiagram/{pipeline_id}", response_class=FileResponse)
def generate_dest_er_diagram(pipeline_id: int,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user_from_token)):
    '''
    Generate er diagram from database for pipeline_id and return it
    '''
    # Query pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    # Query destination database connection
    dest_db_conn = db.query(Db_Conn).filter(Db_Conn.id == pipeline.db_conn_dest_id).first()

    # Create database connection
    if dest_db_conn.db_type == 'redshift':
        schema= dest_db_conn.db_name
    else:
        schema= pipeline.dest_schema_name
    databaseConnection = DatabaseConnection(database_type=dest_db_conn.db_type,
                                            username=dest_db_conn.db_username,
                                            password=dest_db_conn.db_password,
                                            host=dest_db_conn.db_host,
                                            port=dest_db_conn.db_port,
                                            schemas=schema)
    chosen_schema = pipeline.dest_schema_name

    engine = databaseConnection.get_engine()
    db_type=dest_db_conn.db_type

    diagram = Diagram(engine=engine,
                      schema=chosen_schema,
                      db_type=db_type,
                      type="dest")
    image_file = diagram.generate_diagram()

    return FileResponse(image_file)
