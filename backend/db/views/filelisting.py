import os
import boto3
from fastapi import status
from fastapi.responses import JSONResponse


class FileListing:
    def __init__(self) -> None:
        pass

    def s3_bucket_file_list(self,
                            s3Connection):
        '''
        Access s3 bucket using given details and return file list
        '''
        service_name: str = 's3'
        try:
            # Create s3 resource
            s3 = boto3.resource(service_name=service_name,
                                region_name=s3Connection.s3_bucket_region,
                                aws_access_key_id=s3Connection.s3_access_key_id,
                                aws_secret_access_key=s3Connection.s3_secret_access_key)

            bucket = s3.Bucket(s3Connection.s3_bucket)

            # filter bucket object based on user input
            if s3Connection.s3_bucket_path:
                all_objs = bucket.objects.filter(Prefix=s3Connection.s3_bucket_path)
            else:
                all_objs = bucket.objects.all()

            # Put all file name (excluding folder) and extenstion in a list and return it
            files = []
            for obj in all_objs:
                if not str(obj.key).endswith('/'):
                    file_name = obj.key
                    file_type = os.path.splitext(obj.key)[-1].replace('.', '')
                    files.append({'file_name': file_name, 'file_type': file_type})
            return files
        except Exception as ex:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(ex)})

    def gdrive_file_list(self,
                         gdrive_client_id: str,
                         gdrive_client_secret: str,
                         gdrive_access_token: str,
                         gdrive_refresh_token: str,
                         gdrive_token_uri: str,
                         gdrive_scopes: str,
                         gdrive_path: str,
                         gdrive_prefix: str):
        pass

    def drive_file_list(self,
                        fileSystemConnection):
        all_files = os.listdir(fileSystemConnection.lfs_path)
        files = []
        try:
            for file in all_files:
                file_extn = os.path.splitext(file)[-1].replace('.', '')
                if not str(file).endswith('/') and file_extn == 'csv':
                    file_name = file
                    file_type = file_extn
                    files.append({'file_name': file_name, 'file_type': file_type})
            return files
        except Exception as ex:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(ex)})
