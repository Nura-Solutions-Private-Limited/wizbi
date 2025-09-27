from typing import Annotated, Dict, Optional

from pydantic import BaseModel, Field, Json


class S3Connection(BaseModel):
    s3_access_key_id: Optional[str] = Field(default=None)
    s3_secret_access_key: Optional[str] = Field(default=None)
    s3_bucket: Optional[str] = Field(default=None)
    s3_bucket_path: Optional[str] = Field(default=None)
    s3_bucket_region: Optional[str] = Field(default=None)


class FileSystemConnection(BaseModel):
    lfs_path: str
    lfs_prefix: Optional[str] = Field(default=None)
    lfs_mount_point: Optional[str] = Field(default=None)


class AllFiles(BaseModel):
    file_name: Optional[str] = Field(default=None)
    file_type: Optional[str] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2
