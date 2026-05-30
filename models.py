from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Prompt:
    id: int | None
    title: str
    category: str
    tags: str
    body: str
    favorite: bool = False
    created_at: str | None = None
    updated_at: str | None = None


@dataclass(slots=True)
class Note:
    id: int | None
    prompt_id: int
    content: str
    created_at: str | None = None
    updated_at: str | None = None


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()

