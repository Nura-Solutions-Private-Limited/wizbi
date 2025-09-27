from typing import List

from fastapi import HTTPException, status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from db.models.models import Notification, User


# Function to list all notifications for a user
def list_notifications(db: Session, user_id: int) -> List[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).all()


# Function to list paginated notifications for a user
def list_notifications_paginated(db: Session, user_id: int) -> Page[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).paginate()


# Function to get a specific notification by ID
def list_notification(db: Session, user_id: int, id: int) -> Notification:
    notification = db.query(Notification).filter(Notification.id == id, Notification.user_id == user_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notification with ID {id} not found.")
    return notification


# Function to create a new notification
def create_notification(db: Session, user_id: int, description: str, source: str) -> Notification:
    db_notification = Notification(
        user_id=user_id,
        description=description,
        source=source,
        viewed=False  # Default value for viewed
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification
