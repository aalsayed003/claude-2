from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path = "config.yaml") -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_env(cfg_value: str | None, *, required: bool = False) -> str | None:
    """Read an environment variable by name. Used for secrets referenced in config.yaml via `*_env` keys."""
    if cfg_value is None:
        if required:
            raise RuntimeError("missing env var reference in config")
        return None
    value = os.environ.get(cfg_value)
    if required and not value:
        raise RuntimeError(f"required environment variable {cfg_value} is not set")
    return value


def iso_week(week: str | None) -> str:
    """Return the ISO week string (e.g. 2026-W16). If week is None, compute current week."""
    if week:
        return week
    from datetime import date
    y, w, _ = date.today().isocalendar()
    return f"{y}-W{w:02d}"
