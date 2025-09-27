import json
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlencode, urljoin

import pandas as pd
import requests
import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.lib.api_connection_factory import APIConnectorFactory
from db.models.models import Pipeline, Rest_Api_Db_Conn
from db.views.job import add_update_job_status

logger = structlog.getLogger(__name__)


class RestApiConnector:
    '''
    Generic class to access rest api
    '''
    def __init__(self,
                 method: str = None,
                 url: str = None,
                 params: dict = None,
                 authorization: dict = None,
                 headers: dict = None,
                 body: str = None,
                 data_url: str = None,
                 is_auth_url: bool = None,
                 session: requests.Session = None,
                 db: Session = None,
                 pipeline_id: int = None,
                 source_db_conn=None,
                 dest_db_conn=None,
                 dest_db_engine=None
                 ) -> None:
        self.__method = method
        self.__url = url
        self.__params = params,
        self.__authorization = authorization
        self.__headers = headers
        self.__body = body
        self.__data_url = data_url
        self.__is_auth_url = is_auth_url
        self.__db = db
        self.__pipeline_id = pipeline_id
        self.__source_db_conn = source_db_conn
        self.__dest_db_conn = dest_db_conn
        self.__dest_db_engine = dest_db_engine

        # Query rest api connection details
        if self.__source_db_conn:
            restapi_conn = self.__db.query(Rest_Api_Db_Conn
                                           ).filter(Rest_Api_Db_Conn.db_conn_id == self.__source_db_conn.id).first()
            if restapi_conn:
                self.__method = restapi_conn.method
                self.__url = restapi_conn.url
                self.__headers = restapi_conn.headers
                self.__body = restapi_conn.body
                self.__authorization = restapi_conn.authorization
                self.__params = urlencode(restapi_conn.params) if restapi_conn.params else None

        if session is None:
            self.__session = requests.Session()
        else:
            self.__session = session

    def load_data_in_db(self, data):
        '''
        Load restapi response in table
        '''
        # Generate table name using pipeline name by taking
        # first 30 character and appending prefix _rest_api
        table_name = None
        pipeline = self.__db.query(Pipeline).filter(Pipeline.id == self.__pipeline_id).first()
        if pipeline:
            # remove space and special character from name
            pipeline_name = str(pipeline.name).lower()
            pipeline_name = re.sub("[^0-9a-zA-Z]+", "_", pipeline_name, 0, re.IGNORECASE)
            table_name = pipeline_name[0:30] + '_rest_api'
        data.to_sql(table_name, con=self.__dest_db_engine, index=False, if_exists="append")

    def load_data(self, job_id):
        '''
        Read restapi response and load in table
        '''
        try:
            connector_name = str(self.__source_db_conn.sub_type).upper() + 'Connector'
            logger.info(f'Connector name {connector_name}')
            logger.info(self.__params)
            apiconnector = APIConnectorFactory.get_connector(connector_name,
                                                             auth_url=self.__is_auth_url,
                                                             method=self.__method,
                                                             params=self.__params,
                                                             headers=self.__headers,
                                                             data=self.__body)

            output = apiconnector.fetch_data(method=self.__method,
                                             url=self.__url)
            logger.info(f'Output: {output}')
            if output:
                parsed_data = apiconnector.parse_data(output)
                logger.info(f'Parsed data: {parsed_data}')
                # if data found then load and update the job status
                if not parsed_data.empty:
                    self.load_data_in_db(parsed_data)

                    # Update job status to success
                    current_time = datetime.now()
                    job_status = "Success"
                    add_update_job_status(
                        self.__db,
                        status=job_status,
                        job_id=job_id,
                        pipeline_id=self.__pipeline_id,
                        job_date_time=current_time
                    )
                    return True
                else:
                    current_time = datetime.now()
                    job_status = "Completed with errors"
                    add_update_job_status(
                        self.__db,
                        status=job_status,
                        job_id=job_id,
                        pipeline_id=self.__pipeline_id,
                        job_date_time=current_time
                    )
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail='Error in getting rest api data')
        except Exception as e:
            current_time = datetime.now()
            job_status = "Completed with errors"
            add_update_job_status(
                self.__db,
                status=job_status,
                job_id=job_id,
                pipeline_id=self.__pipeline_id,
                job_date_time=current_time
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Error in getting rest api data:{e}')

    def validate_connection(self, parse_json=True):
        response = requests.request(method=self.__method,
                                    url=self.__url,
                                    params=self.__params,
                                    headers=self.__headers,
                                    data=self.__body)
        if response.status_code < 400:
            if response.status_code != requests.codes.no_content:
                if parse_json:
                    return response.json()
                return response.content
        else:
            raise HTTPException(status_code=response.status_code,
                                detail=response.text)


if __name__ == "__main__":
    restApiConnector = RestApiConnector(method='GET',
                                        url='https://openlibrary.org/api/books?bibkeys=ISBN:0201558025,LCCN:93005405&format=json') # NOQA
    restApiConnector.load_data('123')
