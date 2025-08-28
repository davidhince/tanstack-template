from __future__ import annotations

from datetime import datetime, timezone
import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from ..models import Reminder, CreateReminder, Notification
from ..services.memory import reminder_store, notification_store
from ..services.reminders import add_or_update_reminder, cancel_reminder


router = APIRouter()


@router.get("/reminders", response_model=List[Reminder])
async def list_reminders() -> List[Reminder]:
    return sorted(reminder_store.list(), key=lambda r: r.due_at)


@router.post("/reminders", response_model=Reminder)
async def create_reminder(body: CreateReminder) -> Reminder:
    now = datetime.now(timezone.utc)
    reminder = Reminder(
        id=str(uuid.uuid4()),
        text=body.text,
        due_at=body.due_at,
        created_at=now,
        completed=False,
    )
    add_or_update_reminder(reminder)
    return reminder


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str) -> dict:
    ok = reminder_store.delete(reminder_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reminder not found")
    cancel_reminder(reminder_id)
    return {"ok": True}


@router.get("/notifications", response_model=List[Notification])
async def list_notifications() -> List[Notification]:
    # Return most recent first
    return sorted(notification_store.list(), key=lambda n: n.fired_at, reverse=True)

