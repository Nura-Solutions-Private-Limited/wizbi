import re
import os
import boto3
import logging
import pandas as pd
from datetime import datetime

from wizbi_dataload.db.models.models import Source_Db_Mapping
from wizbi_dataload.db.views.job import add_update_job_status

logger = logging.getLogger(__name__)


class FileDataUpload:
    def __init__(self,
                 db=None,
                 file_conn=None,
                 db_conn=None,
                 engine=None,
                 file_list=None,
                 source_type=None,
                 pipeline_id=None) -> None:
        self.db = db
        self.db_conn = db_conn
        self.engine = engine
        self.file_conn = file_conn
        self.file_list = file_list
        self.source_type = source_type
        self.pipeline_id = pipeline_id

    def read_file_data(self, file):
        '''
        Read file data using pandas
        '''
        chunksize = 10 ** 6
        chunks = []
        # return pd.read_csv(file)
        for chunk in pd.read_csv(file, chunksize=chunksize):
            chunks.append(chunk)

        df = pd.concat(chunks, axis=0)
        return df

    def get_colnames_dtypes(self):
        '''
        Read file to fetch column names and data types
        '''
        file_columns = []
        try:
            for file in self.file_list:
                # Read file from s3
                if self.source_type == 's3':
                    file_name, file_obj = self.read_s3conn_file(file.file_name)
                elif self.source_type == 'lfs':
                    file_name, file_obj = self.read_lfs_file(file.file_name)

                df = pd.read_csv(file_obj, nrows=1000)

                file_columns.append({"file_name": file_name, "file_columns": df.dtypes.astype(str).to_dict()})
            return file_columns
        except Exception as ex:
            logger.error(f'Error in reading file column names: {str(ex)}')
            raise Exception(f'Error in reading file column names: {str(ex)}')

    def remove_sp_ch_column(self, df):
        '''
        Remove special character and change column name case
        1. Remove white space from column name start and end
        2. Remove special characters from dataframe column heading and replace it with _
        3. Change column names to lower case
        '''
        # df.columms = df.columns.str.lstrip()
        # df.columns = df.columns.str.rstrip()
        df.rename(columns=lambda x: x.strip(), inplace=True)

        cols = [re.sub("[^0-9a-zA-Z$]+", "_", i) for i in df.columns]
        df.columns = cols

        # df.colummns = map(str.lower, df.columns)
        df.rename(columns=str.lower, inplace=True)

        return df

    def read_s3conn_file(self, file_name):
        '''
        Read data file from aws s3
        '''
        try:
            s3 = boto3.resource(service_name='s3',
                                region_name=self.file_conn.s3_bucket_region,
                                aws_access_key_id=self.file_conn.s3_access_key_id,
                                aws_secret_access_key=self.file_conn.s3_secret_access_key)

            bucket = s3.Bucket(self.file_conn.s3_bucket)
            file_objs = bucket.objects.filter(Prefix=file_name)

            file_name = None
            file_obj = None
            for obj in file_objs:
                file_name = obj.key
                # print(key, os.path.splitext(key)[-1])
                file_obj = obj.get()['Body']
            return file_name, file_obj
        except Exception as ex:
            logger.error(f"Error in reading file from s3:{ex}")
            raise Exception(f"Error in reading file from s3:{ex}")

    def convert_data_types(self, df, data_types):
        """
        Converts column data types in a DataFrame based on a dictionary input.

        Args:
            df (pandas.DataFrame): The DataFrame to convert.
            data_types (dict): A dictionary mapping column names to
            desired data types (e.g., {'col1': 'int', 'col2': 'float'})

        Returns:
            pandas.DataFrame: The DataFrame with converted data types.
        """
        for col, dtype in data_types.items():
            try:
                df[col.lower()] = df[col.lower()].astype(dtype)
            except (ValueError, TypeError):
                logger.error(f"Error converting column {col} to type {dtype}.")
                raise ValueError(f"Error converting column {col} to type {dtype}.")
        return df

    def change_data_type(self, df, file_name):
        '''
        Read data type mapping from source_db_mapping table and change data type
        '''
        source_db_mapping = self.db.query(Source_Db_Mapping).\
            filter(Source_Db_Mapping.pipeline_id == self.pipeline_id).first()

        all_files = source_db_mapping.user_input

        file_data_mappings = all_files.get('files')

        data_types = {}

        df.rename(columns=str.lower, inplace=True)

        for files in file_data_mappings:
            if files.get('file_name') == file_name:
                file_columns = files.get('file_columns')
                for file_column in file_columns:
                    column_name = file_column["column_name"]
                    column_data_type = file_column["data_type"]
                    data_types[column_name] = column_data_type

                # Convert data types based on user input
                df_converted = self.convert_data_types(df.copy(), data_types)
        return df_converted

    def read_lfs_file(self, file_name):
        '''
        Join full file path and validate it and return
        '''
        return file_name, os.path.join(self.file_conn.lfs_path, file_name)

    def load_file_data(self, job_id):
        '''
        Load file data in database table
        '''
        logger.info('file data load started')
        data_load = {}
        try:
            for file in self.file_list:
                # Read file from s3
                if self.source_type == 's3':
                    file_name, file_obj = self.read_s3conn_file(file.file_name)
                elif self.source_type == 'lfs':
                    file_name, file_obj = self.read_lfs_file(file.file_name)
                data_load['file_name'] = file_name
                original_file_name = file_name
                file_extn = os.path.splitext(file_name)[-1]
                file_name = file_name.replace(file_extn, '')
                logger.info(f'file name, {file_name}, source type, {self.source_type}')
                # Read file data using pandas
                # file_df = self.read_file_data(file=file_obj)

                # Remove special characters from column headings
                # file_df = self.remove_sp_ch_column(df=file_df)

                # data_load['total_row'] = file_df.shape[0]
                # file_name = re.sub("[^A-Z]", "", file_name, 0, re.IGNORECASE)
                file_name = re.sub("[^0-9a-zA-Z]+", "_", file_name, 0, re.IGNORECASE)
                # date_string = datetime.now().strftime("%m%d%Y")

                # Prepare table name by removing special characters and limit string to 30 digit and add todays datetime
                # table_name = file_name[0:30] + '_' + date_string
                table_name = file_name[0:30]

                if self.source_type == 'lfs':
                    if self.file_conn:
                        if self.file_conn.lfs_prefix:
                            table_name = self.file_conn.lfs_prefix + table_name
                data_load['table_name'] = table_name

                # check if any table exist with same name and drop it
                with self.engine.connect() as conn:
                    # check if table exist
                    try:
                        conn.execute(f"drop table if exists {table_name}")
                        logger.info(f"dropping table {table_name} if exist")
                    except Exception:
                        logger.error(f'Error in dropping table :{table_name}')
                        raise Exception(f'Error in dropping table :{table_name}')

                chunksize = 10 ** 6
                # chunks = []
                # return pd.read_csv(file)
                logger.info("file data read starting")
                for chunk in pd.read_csv(file_obj, chunksize=chunksize):
                    file_df = self.change_data_type(df=chunk, file_name=original_file_name)

                    # Remove special characters from column headings
                    file_df = self.remove_sp_ch_column(df=file_df)

                    # Read file data using pandas
                    data_load['total_row'] = file_df.shape[0]
                    logger.info(f"Read {file_df.shape[0]} rows from file")

                    # Create table using dataframe schema with auto generated primary key st_id
                    with self.engine.connect() as conn:
                        # conn.execute(f"drop table if exists {table_name}")
                        # check if table exist
                        try:
                            table_exist_query = f"SELECT count(*) FROM {table_name}"
                            conn.execute(table_exist_query)
                            logger.info(f"existing table:{table_name}, data will be appended")
                        except Exception:
                            logger.info(f'table does not exist, creating new table :{table_name} based on file name')
                            table_script = pd.io.sql.get_schema(file_df, table_name, con=self.engine)
                            table_script = table_script.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
                            conn.execute(table_script)
                            # conn.execute(f"ALTER TABLE {table_name} DROP COLUMN `Index`;")
                            conn.execute(
                                f"ALTER TABLE {table_name} ADD COLUMN wizbi_st_id BIGINT PRIMARY KEY AUTO_INCREMENT;")

                    file_df.to_sql(table_name,
                                   con=self.engine,
                                   index=False,
                                   if_exists="append")

                    # data_load_record_df = pd.DataFrame([data_load])
                    logger.info(f'Loaded data in table:{table_name} with records: {file_df.shape[0]}')

                # data_load_record_df.to_sql('file_data_load', con=self.engine, index=True, if_exists='append')

            # Update job status to success
            current_time = datetime.now()
            job_status = 'Success'
            add_update_job_status(self.db,
                                  status=job_status,
                                  job_id=job_id,
                                  pipeline_id=self.pipeline_id,
                                  job_date_time=current_time)
        except Exception as ex:
            logger.error(f"Error in loading file data: {ex}")
            current_time = datetime.now()
            job_status = 'Completed with errors'
            add_update_job_status(self.db,
                                  status=job_status,
                                  job_id=job_id,
                                  pipeline_id=self.pipeline_id,
                                  job_date_time=current_time)
            raise Exception(f"Error in loading file data: {ex}")


if __name__ == '__main__':
    pass
