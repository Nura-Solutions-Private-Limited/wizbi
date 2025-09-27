from typing import List

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import Notification, User
from db.session import get_db
from db.views.notifications import (
    create_notification,
    list_notification,
    list_notifications,
    list_notifications_paginated,
)
from schemas.notifications import (
    CreateNotification,
    RedashWebhookRequest,
    ShowNotification,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


# Endpoint to list all notifications (deprecated)
@router.get("/notifications", response_model=List[ShowNotification], deprecated=True)
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return list_notifications(db=db, user_id=current_user.id)


# Endpoint to list paginated notifications
@router.get("/notifications-paginated", response_model=Page[ShowNotification])
def get_paginated_notifications(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_token)
):
    return list_notifications_paginated(db=db, user_id=current_user.id)


# Endpoint to get a specific notification by ID
@router.get("/notifications/{id}", response_model=ShowNotification)
def get_notification(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_token)
):
    return list_notification(db=db, user_id=current_user.id, id=id)


# Endpoint to create a new notification
@router.post("/notifications", response_model=ShowNotification, status_code=status.HTTP_201_CREATED)
def create_new_notification(
    notification: CreateNotification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    return create_notification(db=db,
                               user_id=current_user.id,
                               description=notification.description,
                               source="User Action")


# Endpoint to handle Redash webhook
@router.post("/notifications/redash-webhook", status_code=status.HTTP_201_CREATED)
def redash_webhook(payload: RedashWebhookRequest, db: Session = Depends(get_db)):
    """
    Webhook endpoint for Redash to send alert notifications.

    - **payload**: The JSON payload sent by Redash.
    """
    try:
        # Extract data from the Redash payload
        # pipeline_id = payload.alert.query_id  # Use query_id as pipeline_id
        description = f"Alert {payload.alert.name} has changed state to {payload.alert.state}"
        source = "Redash"
        user_id = 1002  # Use alert's user_id as the notification's user_id
        # Create a new notification using the existing create_notification function
        notification = create_notification(db, user_id=user_id, description=description, source=source)
        return {"message": "Webhook received and saved successfully", "id": notification.id}
    except Exception as e:
        logger.error(f"Failed to save Redash webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save notification to the database"
        )


@router.put("/notifications/{id}/mark-viewed", status_code=status.HTTP_200_OK)
def mark_viewed(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    """
    Mark a notification as viewed.

    - **id**: ID of the notification to update.
    """
    notification = (
        db.query(
            Notification
            ).filter(
            Notification.id == id, Notification.user_id == current_user.id
            ).first()
    )

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notification with ID {id} not found.")

    notification.viewed = True
    db.commit()
    return {"message": "Notification marked as viewed successfully"}
