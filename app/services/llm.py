import os
from typing import List, Dict, Any
import httpx


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class LLMClient:
    async def generate_reply(self, messages: List[Dict[str, str]]) -> str:
        if OPENAI_API_KEY:
            try:
                return await self._openai_chat(messages)
            except Exception:
                # Fallback to offline if API errors
                return self._offline_reply(messages)
        else:
            return self._offline_reply(messages)

    async def _openai_chat(self, messages: List[Dict[str, str]]) -> str:
        payload: Dict[str, Any] = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OPENAI_API_BASE}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def _offline_reply(self, messages: List[Dict[str, str]]) -> str:
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        content = (last_user or {}).get("content", "").lower()
        if "todo" in content:
            return (
                "I can track todos. Use the Todos panel to add an item, or tell me "
                'like: "Add a todo to call Alex tomorrow".'
            )
        if "remind" in content or "reminder" in content:
            return (
                "I can set reminders. Use the Reminders panel with a specific time, "
                'or tell me like: "Remind me at 5pm to submit the report".'
            )
        return (
            "I'm your assistant. I can chat, manage todos, and set reminders. "
            "What would you like to do?"
        )


llm_client = LLMClient()

