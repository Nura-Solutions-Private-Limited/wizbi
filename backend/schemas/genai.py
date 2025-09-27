import json
import uuid
from datetime import datetime
from typing import Annotated, Dict, Optional, TypedDict

from pydantic import BaseModel, Field


class FactQuestion(BaseModel):
    pipeline_id: int


class FollowUpQuestion(BaseModel):
    pipeline_id: int
    question: str
    algorithm: str


class FactResponse(BaseModel):
    type: str
    questions: Optional[Dict] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class OtherQuestion(BaseModel):
    question: str


class OtherResponse(BaseModel):
    type: str
    answer: str

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class GenDashQuery(BaseModel):
    pipeline_id: str
    prompt: str | None


class OtherResponseType(TypedDict):
    type: str
    answer: str


class Conversation(BaseModel):
    id: int
    user_id: int
    data_context: dict | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class message(BaseModel):
    id: int
    conversation_id: int
    user_id: str
    question: dict[str, str]
    response: dict[str, str] = Field(default=None)

    model_config = {"from_attributes": True}  # replaces orm_mode=True in Pydantic v2


class QueryConversation(BaseModel):
    conversation_id: int
    question: str


class QueryConversationResponse(BaseModel):
    conversation_id: int
    question: str
    answer: str


class ConnectionQuestion(BaseModel):
    db_conn_id: int
    question: str
