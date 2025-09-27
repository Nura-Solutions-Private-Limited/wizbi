from typing import List

import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.dimension_metric import DimensionMetric
from schemas.dimension_metric import (
    CreateDimension,
    CreateDimensionMetric,
    GaAuth,
    ShowDimension,
    ShowDimensionMetric,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


# @router.post("/dimension", response_model=ShowDimension)
# def create_dimension(createDimension: CreateDimension,
#                      db: Session = Depends(get_db),
#                      current_user: User = Depends(get_current_user_from_token)):
#     '''
#     Create new dimension
#     '''
#     dimensionMetric = DimensionMetric(db=db)
#     return dimensionMetric.add_dimension(createDimension=createDimension,
#                                          user_id=current_user.id)


@router.post("/dimensions", response_model=List[ShowDimension])
def get_all_dimension(gaAuth: GaAuth,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    List all dimension
    '''
    dimensionMetric = DimensionMetric(db=db, ga_property_id=gaAuth.ga_property_id, ga_auth_json=gaAuth.ga_auth_json)
    return dimensionMetric.show_dimension(user_id=current_user.id)


# @router.patch("/dimension/{id}", response_model=ShowDimension)
# def update_dimension(id: int,
#                      updateDimension: CreateDimension,
#                      db: Session = Depends(get_db),
#                      current_user: User = Depends(get_current_user_from_token)):
#     '''
#     Update Dimension
#     '''
#     dimensionMetric = DimensionMetric(db=db)
#     return dimensionMetric.update_dimension(dimension_id=id,
#                                             updateDimension=updateDimension,
#                                             user_id=current_user.id)


# @router.post("/metric", response_model=ShowDimensionMetric)
# def create_dimensionmetric(createDimensionMetric: CreateDimensionMetric,
#                            db: Session = Depends(get_db),
#                            current_user: User = Depends(get_current_user_from_token)):
#     '''
#     Create new dimension's metric
#     '''
#     dimensionMetric = DimensionMetric(db=db)
#     return dimensionMetric.add_dimension_metric(createDimensionMetric=createDimensionMetric,
#                                                 user_id=current_user.id)


@router.post("/metrics/{dimension_code}", response_model=List[ShowDimensionMetric])
def get_all_dimensionmetric(dimension_code: str,
                            gaAuth: GaAuth,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user_from_token)):
    '''
    List all dimension's metric
    '''
    dimensionMetric = DimensionMetric(db=db, ga_property_id=gaAuth.ga_property_id, ga_auth_json=gaAuth.ga_auth_json)
    return dimensionMetric.show_dimension_metric(dimension_code=dimension_code,
                                                 user_id=current_user.id)


# @router.patch("/metric/{id}", response_model=ShowDimension)
# def update_dimensionmetric(id: int,
#                            updateDimensionMetric: CreateDimensionMetric,
#                            db: Session = Depends(get_db),
#                            current_user: User = Depends(get_current_user_from_token)):
#     '''
#     Update Dimension
#     '''
#     dimensionMetric = DimensionMetric(db=db)
#     return dimensionMetric.update_dimension_metric(metric_id=id,
#                                                    updateDimensionMetric=updateDimensionMetric,
#                                                    user_id=current_user.id)
