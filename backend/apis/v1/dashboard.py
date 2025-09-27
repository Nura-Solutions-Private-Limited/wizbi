from typing import List

import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.dashboard import UserDashboard
from schemas.dashboard import CreateDashboard, DeleteDashboard, ShowDashboard

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/dashboard", response_model=ShowDashboard)
def create_dashboard(createDashboard: CreateDashboard,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    '''
    Create new dashboard
    '''
    userDashboard = UserDashboard(db=db)
    return userDashboard.add_dashboard(createDashboard=createDashboard,
                                       user_id=current_user.id)


@router.get("/dashboard", response_model=List[ShowDashboard])
def get_all_dashboards(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user_from_token)):
    '''
    List all dashboard for the user group
    '''
    userDashboard = UserDashboard(db=db)
    return userDashboard.show_dashboard(user_id=current_user.id)


@router.patch("/activedashboard/{id}", response_model=List[ShowDashboard])
def update_active_dashboard(id: int,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user_from_token)):
    '''
    Update active status to true for the dashboard id
    and disable all other dashboard for the user group
    '''
    userDashboard = UserDashboard(db=db)
    return userDashboard.enable_dashboard(dashboard_id=id,
                                          user_id=current_user.id)


@router.patch("/dashboard/{id}", response_model=ShowDashboard)
def update_dashboard(id: int,
                     updateDashboard: CreateDashboard,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    '''
    Update Dashboard
    '''
    userDashboard = UserDashboard(db=db)
    return userDashboard.update_dashboard(dashboard_id=id,
                                          updateDashboard=updateDashboard,
                                          user_id=current_user.id)


@router.delete("/dashboard/{id}", response_model=DeleteDashboard)
def delete_db_connection(id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user_from_token)):
    '''
    Delete dashboard
    '''
    userDashboard = UserDashboard(db=db)
    return userDashboard.delete_dashboard(dashboard_id=id)
