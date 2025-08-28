from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


class Todo(BaseModel):
    id: str
    title: str
    completed: bool = False
    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime] = None


class CreateTodo(BaseModel):
    title: str
    due_at: Optional[datetime] = None


class UpdateTodo(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    due_at: Optional[datetime] = None


class Reminder(BaseModel):
    id: str
    text: str
    due_at: datetime
    created_at: datetime
    completed: bool = False


class CreateReminder(BaseModel):
    text: str
    due_at: datetime


class Notification(BaseModel):
    id: str
    text: str
    fired_at: datetime

