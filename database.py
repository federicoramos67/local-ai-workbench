from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from models import Note, Prompt, now_iso
from utils import database_path


class WorkbenchDatabase:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or database_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_schema()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _create_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'General',
                    tags TEXT NOT NULL DEFAULT '',
                    body TEXT NOT NULL DEFAULT '',
                    favorite INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    content TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_prompts_title ON prompts(title);
                CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
                CREATE INDEX IF NOT EXISTS idx_prompts_favorite ON prompts(favorite);
                CREATE INDEX IF NOT EXISTS idx_notes_prompt_id ON notes(prompt_id);
                """
            )

    def seed_if_empty(self) -> None:
        with self.connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
            if count:
                return
        self.save_prompt(
            Prompt(
                id=None,
                title="Daily planning assistant",
                category="Productivity",
                tags="planning, focus, daily",
                body=(
                    "Help me plan my day. Ask for my commitments, deadlines, energy level, "
                    "and top priorities. Then propose a realistic schedule with focus blocks."
                ),
                favorite=True,
            )
        )
        self.save_prompt(
            Prompt(
                id=None,
                title="Code review checklist",
                category="Development",
                tags="code, review, quality",
                body=(
                    "Review this change for correctness, maintainability, security, edge cases, "
                    "and missing tests. Prioritize concrete issues over stylistic preferences."
                ),
            )
        )

    def row_to_prompt(self, row: sqlite3.Row) -> Prompt:
        return Prompt(
            id=row["id"],
            title=row["title"],
            category=row["category"],
            tags=row["tags"],
            body=row["body"],
            favorite=bool(row["favorite"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def row_to_note(self, row: sqlite3.Row) -> Note:
        return Note(
            id=row["id"],
            prompt_id=row["prompt_id"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_prompt(self, prompt_id: int) -> Prompt | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
        return self.row_to_prompt(row) if row else None

    def search_prompts(
        self,
        query: str = "",
        category: str = "All",
        favorites_only: bool = False,
    ) -> list[Prompt]:
        clauses = []
        params: list[Any] = []
        if query.strip():
            term = f"%{query.strip()}%"
            clauses.append("(title LIKE ? OR category LIKE ? OR tags LIKE ? OR body LIKE ?)")
            params.extend([term, term, term, term])
        if category and category != "All":
            clauses.append("category = ?")
            params.append(category)
        if favorites_only:
            clauses.append("favorite = 1")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT * FROM prompts
            {where}
            ORDER BY favorite DESC, updated_at DESC, title COLLATE NOCASE ASC
        """
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self.row_to_prompt(row) for row in rows]

    def list_categories(self) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT category FROM prompts WHERE TRIM(category) <> '' ORDER BY category COLLATE NOCASE"
            ).fetchall()
        return [row[0] for row in rows]

    def save_prompt(self, prompt: Prompt) -> int:
        timestamp = now_iso()
        title = prompt.title.strip() or "Untitled prompt"
        category = prompt.category.strip() or "General"
        with self.connect() as conn:
            if prompt.id is None:
                cursor = conn.execute(
                    """
                    INSERT INTO prompts (title, category, tags, body, favorite, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (title, category, prompt.tags.strip(), prompt.body, int(prompt.favorite), timestamp, timestamp),
                )
                return int(cursor.lastrowid)
            conn.execute(
                """
                UPDATE prompts
                SET title = ?, category = ?, tags = ?, body = ?, favorite = ?, updated_at = ?
                WHERE id = ?
                """,
                (title, category, prompt.tags.strip(), prompt.body, int(prompt.favorite), timestamp, prompt.id),
            )
            return prompt.id

    def delete_prompt(self, prompt_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))

    def toggle_favorite(self, prompt_id: int) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE prompts SET favorite = CASE favorite WHEN 1 THEN 0 ELSE 1 END, updated_at = ? WHERE id = ?",
                (now_iso(), prompt_id),
            )

    def get_note(self, prompt_id: int) -> Note | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM notes WHERE prompt_id = ? LIMIT 1", (prompt_id,)).fetchone()
        return self.row_to_note(row) if row else None

    def save_note(self, prompt_id: int, content: str) -> int:
        timestamp = now_iso()
        existing = self.get_note(prompt_id)
        with self.connect() as conn:
            if existing:
                conn.execute(
                    "UPDATE notes SET content = ?, updated_at = ? WHERE prompt_id = ?",
                    (content, timestamp, prompt_id),
                )
                return existing.id or 0
            cursor = conn.execute(
                "INSERT INTO notes (prompt_id, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (prompt_id, content, timestamp, timestamp),
            )
            return int(cursor.lastrowid)

    def export_payload(self) -> dict[str, Any]:
        prompts = self.search_prompts()
        items = []
        for prompt in prompts:
            note = self.get_note(prompt.id or 0)
            items.append(
                {
                    "title": prompt.title,
                    "category": prompt.category,
                    "tags": prompt.tags,
                    "body": prompt.body,
                    "favorite": prompt.favorite,
                    "created_at": prompt.created_at,
                    "updated_at": prompt.updated_at,
                    "note": note.content if note else "",
                }
            )
        return {"version": 1, "exported_at": now_iso(), "prompts": items}

    def import_payload(self, payload: dict[str, Any]) -> int:
        prompts = payload.get("prompts")
        if not isinstance(prompts, list):
            raise ValueError("Invalid library file: missing prompts list")
        imported = 0
        for item in prompts:
            if not isinstance(item, dict):
                continue
            prompt_id = self.save_prompt(
                Prompt(
                    id=None,
                    title=str(item.get("title") or "Untitled prompt"),
                    category=str(item.get("category") or "General"),
                    tags=str(item.get("tags") or ""),
                    body=str(item.get("body") or ""),
                    favorite=bool(item.get("favorite")),
                )
            )
            note = str(item.get("note") or "")
            if note:
                self.save_note(prompt_id, note)
            imported += 1
        return imported

    def import_json_file(self, path: Path) -> int:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return self.import_payload(payload)
