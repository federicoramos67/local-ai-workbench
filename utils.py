from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "Local AI Workbench"


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def data_dir() -> Path:
    path = app_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def database_path() -> Path:
    custom = os.environ.get("LOCAL_AI_WORKBENCH_DB")
    if custom:
        path = Path(custom).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return data_dir() / "workbench.db"


def resource_path(relative_path: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", app_root()))
    return base / relative_path


def split_tags(tags: str) -> list[str]:
    return [tag.strip() for tag in tags.replace(";", ",").split(",") if tag.strip()]


def markdown_safe_filename(name: str) -> str:
    allowed = []
    for char in name.strip():
        if char.isalnum() or char in (" ", "-", "_"):
            allowed.append(char)
    value = "".join(allowed).strip().replace(" ", "_")
    return value or "prompt"

