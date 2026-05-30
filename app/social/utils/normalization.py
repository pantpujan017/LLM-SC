"""Normalization helpers shared across the social network layer."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from app.social.config.constants import NORMALIZE_ENTITY_NAMES


def normalize_entity_name(name: Any) -> str:
    """Normalize entity labels consistently for graph keys."""
    value = "" if name is None else str(name)
    return value.lower().strip() if NORMALIZE_ENTITY_NAMES else value.strip()


def normalize_label(value: Any, default: str = "unknown") -> str:
    """Normalize categorical labels without forcing a domain-specific mapping."""
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    text = str(value).strip()
    return text if text else default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert scalar values to finite floats."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(result) or np.isinf(result):
        return default
    return result

