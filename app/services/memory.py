from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models import Todo, Reminder, Notification


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


class _JsonListStore:
    def __init__(self, filename: str) -> None:
        self._file_path = os.path.join(DATA_DIR, filename)
        self._lock = threading.RLock()
        # Initialize file if missing
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read(self) -> List[Dict[str, Any]]:
        with self._lock:
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []

    def _write(self, items: List[Dict[str, Any]]) -> None:
        with self._lock:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2, default=str)


class TodoStore(_JsonListStore):
    def list(self) -> List[Todo]:
        return [Todo(**x) for x in self._read()]

    def upsert(self, todo: Todo) -> None:
        items = self._read()
        items = [x for x in items if x.get("id") != todo.id]
        items.append(todo.model_dump())
        self._write(items)

    def delete(self, todo_id: str) -> bool:
        items = self._read()
        new_items = [x for x in items if x.get("id") != todo_id]
        self._write(new_items)
        return len(items) != len(new_items)


class ReminderStore(_JsonListStore):
    def list(self) -> List[Reminder]:
        return [Reminder(**x) for x in self._read()]

    def upsert(self, reminder: Reminder) -> None:
        items = self._read()
        items = [x for x in items if x.get("id") != reminder.id]
        items.append(reminder.model_dump())
        self._write(items)

    def delete(self, reminder_id: str) -> bool:
        items = self._read()
        new_items = [x for x in items if x.get("id") != reminder_id]
        self._write(new_items)
        return len(items) != len(new_items)


class NotificationStore(_JsonListStore):
    def list(self) -> List[Notification]:
        return [Notification(**x) for x in self._read()]

    def add(self, notification: Notification) -> None:
        items = self._read()
        items.append(notification.model_dump())
        self._write(items)

    def clear_older_than(self, since: datetime) -> None:
        items = [n.model_dump() for n in self.list() if n.fired_at >= since]
        self._write(items)


todo_store = TodoStore("todos.json")
reminder_store = ReminderStore("reminders.json")
notification_store = NotificationStore("notifications.json")

