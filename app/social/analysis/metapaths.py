"""Semantic meta-path analysis for visitor trajectories."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product
from typing import Dict, Iterable, List, Sequence, Tuple

import networkx as nx
import pandas as pd
from loguru import logger

from app.social.models.results import MetaPathAnalysisResult, MetaPathMetric, NetworkContext
from app.social.utils.normalization import normalize_entity_name, normalize_label


DEFAULT_SEMANTIC_PATHS: List[Tuple[str, str, str]] = [
    ("ritual", "sacred_space", "spiritual_emotion"),
    ("sacred_space", "ritual", "spiritual_emotion"),
    ("sacred_object", "sacred_space", "spiritual_emotion"),
    ("religious_actor", "ritual", "spiritual_emotion"),
    ("scenic_spot", "sacred_space", "general_sentiment"),
    ("facility_service", "problem", "general_sentiment"),
    ("problem", "facility_service", "general_sentiment"),
    ("problem", "sacred_space", "dual_valence"),
]

PILGRIM_TYPES = {"solo", "couples"}
TOURIST_TYPES = {"family", "friends", "business"}


class MetaPathAnalyzer:
    """Count research-interest semantic paths in graph and review groups."""

    name = "metapaths"

    def __init__(self, semantic_paths: Sequence[Tuple[str, str, str]] | None = None):
        self.semantic_paths = list(semantic_paths or DEFAULT_SEMANTIC_PATHS)

    def analyze(self, context: NetworkContext) -> MetaPathAnalysisResult:
        logger.info("Analyzing semantic meta-path trajectories...")
        G = context.graph
        graph_counts = self._count_graph_paths(G)
        group_counts = self._count_group_paths(context.data.entities)
        total = sum(graph_counts.values())
        metrics = []
        for path in self.semantic_paths:
            path_key = self._path_key(path)
            frequency = graph_counts[path]
            prevalence = frequency / total if total else 0.0
            group_total = sum(group_counts[path].values())
            expected = total / len(self.semantic_paths) if self.semantic_paths and total else 0.0
            significance = (frequency - expected) / expected if expected else 0.0
            metrics.append(
                MetaPathMetric(
                    path=path_key,
                    node_types=list(path),
                    frequency=int(frequency),
                    prevalence=float(prevalence),
                    significance=float(significance),
                    group_frequencies={**group_counts[path], "group_total": int(group_total)},
                )
            )

        comparison = {
            self._path_key(path): dict(group_counts[path])
            for path in self.semantic_paths
        }
        return MetaPathAnalysisResult(
            paths=sorted(metrics, key=lambda metric: (-metric.frequency, metric.path)),
            total_observed_paths=int(total),
            pilgrim_vs_tourist=comparison,
        )

    def _count_graph_paths(self, G: nx.Graph) -> Counter[Tuple[str, str, str]]:
        counts: Counter[Tuple[str, str, str]] = Counter({path: 0 for path in self.semantic_paths})
        path_set = set(self.semantic_paths)
        nodes_by_type: Dict[str, set[str]] = defaultdict(set)
        for node, attrs in G.nodes(data=True):
            nodes_by_type[attrs.get("entity_type", "unknown")].add(node)

        for path in self.semantic_paths:
            first_nodes = nodes_by_type.get(path[0], set())
            middle_nodes = nodes_by_type.get(path[1], set())
            last_nodes = nodes_by_type.get(path[2], set())
            if not first_nodes or not middle_nodes or not last_nodes:
                continue
            for middle in middle_nodes:
                first_neighbors = set(G.neighbors(middle)) & first_nodes
                last_neighbors = set(G.neighbors(middle)) & last_nodes
                if path[0] == path[2]:
                    counts[path] += sum(1 for u, v in product(first_neighbors, last_neighbors) if u != v)
                else:
                    counts[path] += len(first_neighbors) * len(last_neighbors)
        return counts

    def _count_group_paths(self, entities_df: pd.DataFrame) -> Dict[Tuple[str, str, str], Dict[str, int]]:
        counts = {path: {"pilgrim": 0, "tourist": 0, "solo": 0, "couples": 0, "family": 0, "friends": 0} for path in self.semantic_paths}
        if entities_df.empty:
            return counts
        for (_, trip_type), review_entities in entities_df.groupby(["review_id", "trip_type"]):
            trip_type = normalize_label(trip_type)
            type_counts = Counter(normalize_label(entity_type) for entity_type in review_entities["entity_type"])
            for path in self.semantic_paths:
                frequency = 1
                for entity_type in path:
                    frequency *= type_counts.get(entity_type, 0)
                if frequency <= 0:
                    continue
                if trip_type in counts[path]:
                    counts[path][trip_type] += frequency
                if trip_type in PILGRIM_TYPES:
                    counts[path]["pilgrim"] += frequency
                elif trip_type in TOURIST_TYPES:
                    counts[path]["tourist"] += frequency
        return counts

    @staticmethod
    def _path_key(path: Iterable[str]) -> str:
        return " -> ".join(path)

