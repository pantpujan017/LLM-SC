"""Serialization helpers for JSON and GraphML exports."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
import json

import numpy as np
from pydantic import BaseModel


def to_jsonable(value: Any) -> Any:
    """Convert dataclasses, Pydantic models, and numpy scalars to JSON-safe values."""
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, BaseModel):
        return to_jsonable(value.model_dump())
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, payload: Any, indent: int = 2) -> Path:
    """Write a JSON file with a consistent encoder."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_jsonable(payload), f, indent=indent)
    return path

