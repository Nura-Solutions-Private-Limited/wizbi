from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class CreateNotification(BaseModel):
    user_id: int
    description: str
    source: str


class ShowNotification(BaseModel):
    id: int
    user_id: int
    description: str
    source: str
    viewed: bool
    alert_datetime: datetime

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


# Pydantic model for Redash webhook payload
class AlertPayload(BaseModel):
    description: str
    updated_at: str
    id: int
    last_triggered_at: str
    user_id: int
    name: str
    rearm: int
    title: str
    created_at: str
    state: str
    query_id: int
    options: dict


class RedashWebhookRequest(BaseModel):
    url_base: str
    event: str
    alert: AlertPayload
