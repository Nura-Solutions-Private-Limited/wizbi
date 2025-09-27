from datetime import datetime

import structlog
from sqlalchemy.orm import Session

from db.models.models import Dashboard, User, User_Group
from db.views.permission_checker import PermissionChecker
from schemas.dashboard import CreateDashboard, ShowDashboard

logger = structlog.getLogger(__name__)


class UserDashboard:
    """
    Manage dashboard based on user group
    """

    def __init__(self, db: Session):
        self.db = db

    def add_dashboard(self, createDashboard: CreateDashboard, user_id: int):
        """
        Create dashboard
        """
        try:
            group_id = (
                self.db.query(User_Group.group_id)
                .join(User, User.id == User_Group.user_id)
                .filter(User.id == user_id)
                .first()
            )
            dashboard = Dashboard(
                group_id=group_id[0],
                name=createDashboard.name,
                link=createDashboard.link,
                isactive=createDashboard.isactive,
                updated_date=datetime.now(),
            )

            self.db.add(dashboard)
            self.db.commit()
            self.db.refresh(dashboard)
            return dashboard
        except Exception as ex:
            logger.error(f"Error in creating dashboard : {str(ex)}")
            raise ex

    def show_dashboard(self, user_id):
        """
        Get all dashboard for the user group
        """
        permissionChecker = PermissionChecker()
        dashboard_permission, dashboard_ids = permissionChecker.get_permission(
            db=self.db, user_id=user_id, permission_for="dashboards"
        )
        logger.info(f"Userid {user_id} Dashboard permission {dashboard_permission} and ids {dashboard_ids}")
        if dashboard_permission and not dashboard_ids:
            dashboard = self.db.query(Dashboard).all()
        elif dashboard_permission and dashboard_ids:
            dashboard = (
                self.db.query(Dashboard).filter(Dashboard.id.in_(dashboard_ids)).order_by(Dashboard.id.desc()).all()
            )
        return dashboard

    def enable_dashboard(self, dashboard_id: int, user_id: int):
        """
        Enable given dashboard and disable all other dashboard for the user group
        """
        group_id = (
            self.db.query(User_Group.group_id)
            .join(User, User.id == User_Group.user_id)
            .filter(User.id == user_id)
            .first()
        )
        dashboard = self.db.query(Dashboard).filter(Dashboard.group_id == group_id[0]).all()

        for d in dashboard:
            if d.id == dashboard_id:
                d.isactive = True
            else:
                d.isactive = False

        self.db.commit()
        # self.db.refresh(dashboard)
        return dashboard

    def update_dashboard(self, dashboard_id: int, updateDashboard: CreateDashboard, user_id: int):
        try:
            group_id = (
                self.db.query(User_Group.group_id)
                .join(User, User.id == User_Group.user_id)
                .filter(User.id == user_id)
                .first()
            )
            dashboard = self.db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
            # user = self.db.query(User).filter(User.id == user_id).first()
            dashboard.group_id = group_id[0]
            dashboard.name = updateDashboard.name
            dashboard.link = updateDashboard.link
            dashboard.isactive = updateDashboard.isactive
            dashboard.updated_date = datetime.now()

            self.db.commit()
            self.db.refresh(dashboard)
            return dashboard
        except Exception as ex:
            logger.error(f"Error in getting dashboard for the user:{user_id} :{str(ex)}")
            raise ex

    def delete_dashboard(self, dashboard_id: int):
        """
        Delete dashboard
        """
        existing_dashboard = self.db.query(Dashboard).filter(Dashboard.id == dashboard_id)
        if not existing_dashboard.first():
            return 0
        existing_dashboard.delete(synchronize_session=False)
        self.db.commit()
        return 1
