import collections
import json
from datetime import datetime, timedelta

import structlog
from fastapi import HTTPException, status
from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    String,
    Table,
    inspect,
    text,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy_utils import create_database, database_exists, get_tables

from db.models.models import Pipeline
from db.views.report import create_report
from schemas.report import CreateReport

logger = structlog.getLogger(__name__)


class CreateDatawarehouse:
    def __init__(self,
        
                 url) -> None:
        
            self.url=url
            

    def createDW(self, dwName):
        if not database_exists(self.url):
            create_database(self.url)
        # existing_databases=mycursor.fetchall()
            logger.info("Database schema:-{} created".format(dwName))
        else:
            logger.info("Using the existing data warehouse. \
                        Database schema with name:- {} exits in database".format(dwName))
            # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            # detail="Database schema with name:- {} exits in database".format(dwName))
