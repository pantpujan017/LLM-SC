"""Visualization utilities for story-map network rendering."""

from __future__ import annotations

import math
from typing import Any

from app.social.config.constants import COLOR_PALETTE, ENTITY_DESCRIPTIONS


HERITAGE_PALETTE = {
    "ritual": "#C5A059",
    "religious_actor": "#B22222",
    "sacred_space": "#4682B4",
    "spiritual_emotion": "#7C3AED",
    "cultural_rule": "#8FBC8F",
    "problem": "#CD5C5C",
    "facility_service": "#6B7280",
    "scenic_spot": "#60A5FA",
    "dual_valence": "#A855F7",
    "festival_event": "#DB2777",
    "sacred_object": "#DAA520",
    "general_sentiment": "#9CA3AF",
}


def node_color(entity_type: str) -> str:
    """Return a stable professional color for an entity type."""
    return HERITAGE_PALETTE.get(entity_type, COLOR_PALETTE.get(entity_type, "#8A8F98"))


def power_law_size(prominence: float, degree: int, min_size: int = 8, max_size: int = 34) -> float:
    """Scale nodes by prominence without letting hubs overwhelm the graph."""
    signal = max(prominence, 0.0) * 120 + max(degree, 0) / 60
    size = min_size + (math.sqrt(signal) * 8)
    return max(min_size, min(max_size, size))


def node_tooltip(node: str, attrs: dict[str, Any], degree: int) -> str:
    """Rich HTML tooltip for graph nodes."""
    entity_type = attrs.get("entity_type", "unknown")
    description = ENTITY_DESCRIPTIONS.get(entity_type, "Visitor idea")
    community = attrs.get("community_name", "Unassigned theme")
    sentiment = attrs.get("sentiment_overall", 0)
    prominence = attrs.get("degree_centrality", 0)
    return (
        f"<div style='font-family:Inter,Arial,sans-serif;line-height:1.45;max-width:280px'>"
        f"<strong style='font-size:14px'>{node}</strong><br>"
        f"<span>{description}</span><br><br>"
        f"<strong>Theme:</strong> {community}<br>"
        f"<strong>Connections:</strong> {degree}<br>"
        f"<strong>Prominence:</strong> {prominence:.4f}<br>"
        f"<strong>Feeling score:</strong> {float(sentiment or 0):.2f}"
        f"</div>"
    )

