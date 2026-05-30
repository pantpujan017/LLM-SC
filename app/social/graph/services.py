"""Reusable graph operations for the Heritage Experience Network."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from app.social.config.constants import SACRED_ENTITY_TYPES
from app.social.utils.normalization import normalize_entity_name, safe_float


class GraphMetricsService:
    """Central place for commonly reused graph metrics."""

    @staticmethod
    def weighted_degree(G: nx.Graph, node: str) -> float:
        return float(sum(data.get("weight", 1.0) for _, _, data in G.edges(node, data=True)))

    @staticmethod
    def weighted_degrees(G: nx.Graph) -> Dict[str, float]:
        return {node: GraphMetricsService.weighted_degree(G, node) for node in G.nodes()}

    @staticmethod
    def density(G: nx.Graph) -> float:
        return float(nx.density(G)) if G.number_of_nodes() > 1 else 0.0

    @staticmethod
    def connected_components(G: nx.Graph) -> int:
        return nx.number_connected_components(G) if G.number_of_nodes() else 0

    @staticmethod
    def average_clustering(G: nx.Graph) -> float:
        if G.number_of_nodes() < 3:
            return 0.0
        return float(nx.average_clustering(G, weight="weight"))

    @staticmethod
    def centralization(G: nx.Graph, centrality: Optional[Dict[str, float]] = None) -> float:
        if G.number_of_nodes() <= 2:
            return 0.0
        scores = centrality or nx.degree_centrality(G)
        if not scores:
            return 0.0
        max_score = max(scores.values())
        numerator = sum(max_score - score for score in scores.values())
        denominator = (G.number_of_nodes() - 1) * (G.number_of_nodes() - 2)
        return float(numerator / denominator) if denominator else 0.0

    @staticmethod
    def top_nodes(
        G: nx.Graph,
        scores: Dict[str, float],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        rows = []
        for node, score in sorted(scores.items(), key=lambda item: -item[1])[:limit]:
            rows.append(
                {
                    "node": node,
                    "score": float(score),
                    "entity_type": G.nodes[node].get("entity_type", "unknown"),
                    "degree": int(G.degree(node)),
                    "weighted_degree": GraphMetricsService.weighted_degree(G, node),
                }
            )
        return rows


class GraphAttributeService:
    """Attach analysis outputs to graph nodes through one narrow interface."""

    @staticmethod
    def assign_node_attributes(G: nx.Graph, values: Dict[str, Dict[str, Any]]) -> None:
        for node, attrs in values.items():
            if node in G:
                G.nodes[node].update(attrs)

    @staticmethod
    def assign_communities(G: nx.Graph, assignments: Dict[str, int]) -> None:
        GraphAttributeService.assign_node_attributes(
            G,
            {node: {"community_id": int(community_id)} for node, community_id in assignments.items()},
        )


class TemporalGraphService:
    """Create period-specific graph views from entity tables."""

    def __init__(self, G: nx.Graph, entities_df: pd.DataFrame):
        self.G = G
        self.entities_df = entities_df

    def period_nodes(self, year_start: int, year_end: int) -> set[str]:
        period_entities = self.entities_df[
            (self.entities_df["year"] >= year_start)
            & (self.entities_df["year"] <= year_end)
        ]
        return {
            normalize_entity_name(row["entity_name"])
            for _, row in period_entities.iterrows()
            if normalize_entity_name(row["entity_name"]) in self.G
        }

    def period_subgraph(self, year_start: int, year_end: int) -> nx.Graph:
        return self.G.subgraph(self.period_nodes(year_start, year_end)).copy()

    def review_ids(self, year_start: int, year_end: int) -> np.ndarray:
        period_entities = self.entities_df[
            (self.entities_df["year"] >= year_start)
            & (self.entities_df["year"] <= year_end)
        ]
        return period_entities["review_id"].unique()


class NodeSentimentService:
    """Shared helpers for node-level sentiment values."""

    @staticmethod
    def node_sentiment(G: nx.Graph, node: str, default: float = 0.0) -> float:
        return safe_float(G.nodes[node].get("sentiment_overall", default), default)

    @staticmethod
    def sentiment_label(score: float, neutral_low: float = 0.45, neutral_high: float = 0.55) -> str:
        if score < neutral_low:
            return "negative"
        if score > neutral_high:
            return "positive"
        return "neutral"

    @staticmethod
    def average_sentiment(G: nx.Graph, nodes: Iterable[str]) -> float:
        scores = [NodeSentimentService.node_sentiment(G, node) for node in nodes if node in G]
        return float(np.mean(scores)) if scores else 0.0


class EntityTypeService:
    """Reusable entity-type grouping logic."""

    @staticmethod
    def dominant_type(G: nx.Graph, nodes: Iterable[str]) -> str:
        counts = Counter(G.nodes[node].get("entity_type", "unknown") for node in nodes if node in G)
        return counts.most_common(1)[0][0] if counts else "unknown"

    @staticmethod
    def type_counts(G: nx.Graph, nodes: Iterable[str]) -> Dict[str, int]:
        return dict(Counter(G.nodes[node].get("entity_type", "unknown") for node in nodes if node in G))

    @staticmethod
    def sacred_nodes(G: nx.Graph) -> List[str]:
        return [
            node
            for node, attrs in G.nodes(data=True)
            if attrs.get("entity_type") in SACRED_ENTITY_TYPES
        ]

