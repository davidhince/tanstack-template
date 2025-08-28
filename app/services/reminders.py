from __future__ import annotations

from datetime import datetime, timezone
import uuid
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from ..models import Reminder, Notification
from .memory import reminder_store, notification_store


_scheduler: Optional[AsyncIOScheduler] = None


async def start_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone=timezone.utc)
        _scheduler.start()
        # Reschedule existing reminders
        for reminder in reminder_store.list():
            if not reminder.completed and reminder.due_at > datetime.now(timezone.utc):
                _schedule(reminder)


async def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def _schedule(reminder: Reminder) -> None:
    assert _scheduler is not None
    _scheduler.add_job(
        func=_fire_notification,
        trigger=DateTrigger(run_date=reminder.due_at),
        id=f"reminder-{reminder.id}",
        replace_existing=True,
        kwargs={"reminder": reminder},
    )


def _fire_notification(reminder: Reminder) -> None:
    # Mark as completed when fired
    completed_reminder = Reminder(**{**reminder.model_dump(), "completed": True})
    reminder_store.upsert(completed_reminder)
    notification = Notification(id=str(uuid.uuid4()), text=reminder.text, fired_at=datetime.now(timezone.utc))
    notification_store.add(notification)


def add_or_update_reminder(reminder: Reminder) -> None:
    reminder_store.upsert(reminder)
    if _scheduler:
        _schedule(reminder)


def cancel_reminder(reminder_id: str) -> None:
    if _scheduler:
        job_id = f"reminder-{reminder_id}"
        job = _scheduler.get_job(job_id)
        if job:
            job.remove()

