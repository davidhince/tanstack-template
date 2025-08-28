from __future__ import annotations

from datetime import datetime, timezone
import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from ..models import Todo, CreateTodo, UpdateTodo
from ..services.memory import todo_store


router = APIRouter()


@router.get("/todos", response_model=List[Todo])
async def list_todos() -> List[Todo]:
    return sorted(todo_store.list(), key=lambda t: t.created_at, reverse=True)


@router.post("/todos", response_model=Todo)
async def create_todo(body: CreateTodo) -> Todo:
    now = datetime.now(timezone.utc)
    todo = Todo(
        id=str(uuid.uuid4()),
        title=body.title,
        completed=False,
        created_at=now,
        updated_at=now,
        due_at=body.due_at,
    )
    todo_store.upsert(todo)
    return todo


@router.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, body: UpdateTodo) -> Todo:
    items = {t.id: t for t in todo_store.list()}
    if todo_id not in items:
        raise HTTPException(status_code=404, detail="Todo not found")
    existing = items[todo_id]
    updated = existing.model_copy(update={
        "title": body.title if body.title is not None else existing.title,
        "completed": body.completed if body.completed is not None else existing.completed,
        "due_at": body.due_at if body.due_at is not None else existing.due_at,
        "updated_at": datetime.now(timezone.utc),
    })
    todo_store.upsert(updated)
    return updated


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str) -> dict:
    ok = todo_store.delete(todo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"ok": True}

