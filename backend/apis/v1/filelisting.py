from typing import List

import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.filelisting import FileListing
from schemas.filelisting import AllFiles, FileSystemConnection, S3Connection

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/s3files", response_model=List[AllFiles])
def get_s3files(s3Connection: S3Connection,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user_from_token)):
    '''
    List all s3 bucket files
    '''
    fileListing = FileListing()
    return fileListing.s3_bucket_file_list(s3Connection=s3Connection)


@router.post("/localfiles", response_model=List[AllFiles])
def get_localfiles(fileSystemConnection: FileSystemConnection,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    '''
    List all files from local path
    '''
    fileListing = FileListing()
    return fileListing.drive_file_list(fileSystemConnection=fileSystemConnection)
