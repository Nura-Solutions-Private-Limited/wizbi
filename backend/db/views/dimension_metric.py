import json
import os
import tempfile
from datetime import datetime

import structlog
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import GetMetadataRequest, MetricType
from sqlalchemy.orm import Session

from db.models.models import Dimension, Metric, User
from schemas.dimension_metric import (
    CreateDimension,
    CreateDimensionMetric,
    ShowDimension,
    ShowDimensionMetric,
)

logger = structlog.getLogger(__name__)


class DimensionMetric:
    '''
    Manage google analytics dimension and metric
    '''

    def __init__(self,
                 db: Session,
                 ga_property_id,
                 ga_auth_json) -> None:
        self.db = db
        self.property_id = ga_property_id
        self.ga_auth_json = ga_auth_json
        self.auth_file = tempfile.NamedTemporaryFile(suffix=".json", mode="w+")
        json.dump(self.ga_auth_json, self.auth_file)
        self.auth_file.flush()
        logger.info(self.auth_file.name)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.auth_file.name
        self.client = BetaAnalyticsDataClient()

    def add_dimension(self,
                      createDimension: CreateDimension,
                      user_id: int):
        '''
        Create dimension
        '''
        try:
            # user = self.db.query(User).filter(User.id == user_id).first()
            dimension = Dimension(dimension=createDimension.dimension,
                                  status=createDimension.status)

            self.db.add(dimension)
            self.db.commit()
            self.db.refresh(dimension)
            return dimension
        except Exception as ex:
            logger.error(f"Error in creating dimension : {str(ex)}")
            raise ex

    def show_dimension(self, user_id):
        '''
        Get all dashboard for the user group
        '''
        try:
            request = GetMetadataRequest(name=f"properties/{self.property_id}/metadata")
            response = self.client.get_metadata(request)
            dimension_metadata = []
            for dimension in response.dimensions:
                dimension_metadata.append({
                    "type": "Dimension",
                    "dataType": "STRING",
                    "code": dimension.api_name,
                    "name": dimension.ui_name,
                    "description": dimension.description,
                    "customDefinition": dimension.custom_definition
                })
            # dimension = self.db.query(Dimension).all()
            return dimension_metadata
        except Exception as ex:
            logger.error(f"Error in getting dimension :{str(ex)}")
            raise ex

    def update_dimension(self,
                         dimension_id: int,
                         updateDimension: CreateDimension,
                         user_id: int):
        try:
            dimension = self.db.query(Dimension).filter(Dimension.id == dimension_id).first()
            # user = self.db.query(User).filter(User.id == user_id).first()
            dimension.dimension = updateDimension.dimension
            dimension.status = updateDimension.status

            self.db.commit()
            self.db.refresh(dimension)
            return dimension
        except Exception as ex:
            logger.error(f"Error in getting dimension :{str(ex)}")
            raise ex

    def add_dimension_metric(self,
                             createDimensionMetric: CreateDimensionMetric,
                             user_id: int):
        '''
        Create dimension's metric
        '''
        try:
            # user = self.db.query(User).filter(User.id == user_id).first()
            dimensionMetric = Metric(metric=createDimensionMetric.metric,
                                     status=createDimensionMetric.status,
                                     dimension_id=createDimensionMetric.dimension_id)

            self.db.add(dimensionMetric)
            self.db.commit()
            self.db.refresh(dimensionMetric)
            return dimensionMetric
        except Exception as ex:
            logger.error(f"Error in creating dimensionMetric : {str(ex)}")
            raise ex

    def show_dimension_metric(self, dimension_code, user_id):
        '''
        Get all metric of a dimension
        '''
        try:
            request = GetMetadataRequest(name=f"properties/{self.property_id}/metadata")
            response = self.client.get_metadata(request)

            metric_metadata = []
            for metric in response.metrics:
                metric_metadata.append({
                    "type": "Metric",
                    "dataType": MetricType(metric.type_).name,
                    "code": metric.api_name,
                    "name": metric.ui_name,
                    "description": metric.description,
                    "customDefinition": metric.custom_definition
                })
            return metric_metadata
        except Exception as ex:
            logger.error(f"Error in getting dimensionMetric :{str(ex)}")
            raise ex

    def update_dimension_metric(self,
                                metric_id: int,
                                updateDimensionMetric: CreateDimensionMetric,
                                user_id: int):
        try:
            dimensionMetric = self.db.query(Metric).filter(Metric.id == metric_id).first()
            # user = self.db.query(User).filter(User.id == user_id).first()
            dimensionMetric.metric = updateDimensionMetric.metric
            dimensionMetric.status = updateDimensionMetric.status
            dimensionMetric.dimension_id = updateDimensionMetric.dimension_id

            self.db.commit()
            self.db.refresh(dimensionMetric)
            return dimensionMetric
        except Exception as ex:
            logger.error(f"Error in updating dimensionMetric :{str(ex)}")
            raise ex
