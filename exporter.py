from __future__ import annotations

import json
from pathlib import Path

from database import WorkbenchDatabase
from models import Prompt
from utils import markdown_safe_filename


def prompt_to_markdown(prompt: Prompt, note: str = "") -> str:
    favorite = "Yes" if prompt.favorite else "No"
    parts = [
        f"# {prompt.title}",
        "",
        f"- Category: {prompt.category}",
        f"- Tags: {prompt.tags or 'None'}",
        f"- Favorite: {favorite}",
        "",
        "## Prompt",
        "",
        prompt.body.strip(),
    ]
    if note.strip():
        parts.extend(["", "## Notes", "", note.strip()])
    return "\n".join(parts).rstrip() + "\n"


def export_prompt_markdown(db: WorkbenchDatabase, prompt_id: int, directory: Path) -> Path:
    prompt = db.get_prompt(prompt_id)
    if not prompt:
        raise ValueError("Prompt not found")
    note = db.get_note(prompt_id)
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / f"{markdown_safe_filename(prompt.title)}.md"
    file_path.write_text(prompt_to_markdown(prompt, note.content if note else ""), encoding="utf-8")
    return file_path


def export_library_json(db: WorkbenchDatabase, file_path: Path) -> Path:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(db.export_payload(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return file_path

