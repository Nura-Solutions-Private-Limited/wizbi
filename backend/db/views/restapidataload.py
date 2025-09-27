import json
import sys
import time
from datetime import datetime
from urllib.parse import urlencode, urljoin

import pandas as pd
import requests
import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.models.models import Rest_Api_Db_Conn
from db.views.job import add_update_job_status
from db.views.restapi import RestApiConnector

logger = structlog.getLogger(__name__)


class RestAPIDataLoad:
    def __init__(self,
                 method: str,
                 url: str,
                 params: dict,
                 authorization: dict,
                 headers: dict,
                 body: str,
                 sub_type: str):
        self.method: str = method
        self.url: str = url
        self.params: dict = params
        self.authorization: dict = authorization
        self.headers: dict = headers
        self.body: str = body
        self.sub_type: str = sub_type

    def get_api_response_preview(self):
        restApiConnector = RestApiConnector(method=self.method,
                                            url=self.url,
                                            params=self.params,
                                            authorization=self.authorization,
                                            headers=self.headers,
                                            body=self.body)
        response = restApiConnector.get_api_response()
        if self.sub_type == 'PACT_GET':
            # logic to process data
            logger.info('Getting data for preview for type PACT_GET')

            # TODO: Add logic to read only 10 rows
            json_data = response.json()
            df = pd.DataFrame(json_data.get('ReportData').get('Message').get('Document_Details').get('Row'))
            # restrict data to only 10 rows
            df = df.head(10)
            return df.to_dict(orient='records')
