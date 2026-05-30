"""Graph construction for the Heritage Experience Network."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Tuple

import networkx as nx
import pandas as pd
from loguru import logger

from app.social.config.constants import ASPECT_TO_ENTITY_TYPE, EDGE_WEIGHT_ALPHA, EDGE_WEIGHT_BETA
from app.social.models.results import SocialDataBundle
from app.social.services.data_service import SocialDataService
from app.social.utils.normalization import normalize_entity_name, normalize_label, safe_float


class GraphBuilder:
    """Build a concept-level weighted HIN from cleaned Phase 2.5 tables."""

    def __init__(self, data_dir: Path | str | None = None, data: SocialDataBundle | None = None):
        self.data_dir = Path(data_dir) if data_dir is not None else None
        self.data = data
        self.entities_df: pd.DataFrame | None = None
        self.relations_df: pd.DataFrame | None = None
        self.sentiments_df: pd.DataFrame | None = None
        self.G: nx.Graph | None = None

    def build(self) -> nx.Graph:
        logger.info("Building Heterogeneous Heritage Experience Network")
        self._ensure_data()
        self.G = nx.Graph()
        self._add_nodes()
        self._add_edges()
        self._attach_sentiments()
        self._attach_review_counts()
        logger.success(
            f"Graph built: {self.G.number_of_nodes():,} nodes, {self.G.number_of_edges():,} edges"
        )
        return self.G

    def _ensure_data(self) -> None:
        if self.data is None:
            if self.data_dir is None:
                raise ValueError("GraphBuilder requires data_dir or SocialDataBundle")
            self.data = SocialDataService(self.data_dir).load()
        self.entities_df = self.data.entities
        self.relations_df = self.data.relations
        self.sentiments_df = self.data.sentiments

    def _add_nodes(self) -> None:
        assert self.G is not None and self.entities_df is not None
        node_types: Dict[str, str] = {}
        first_year: Dict[str, int] = {}
        last_year: Dict[str, int] = {}

        for _, row in self.entities_df.iterrows():
            name = normalize_entity_name(row["entity_name"])
            if not name:
                continue
            node_types.setdefault(name, normalize_label(row.get("entity_type")))
            year = int(row["year"]) if pd.notna(row.get("year")) else 0
            if year:
                first_year[name] = min(first_year.get(name, year), year)
                last_year[name] = max(last_year.get(name, year), year)

        for name, entity_type in node_types.items():
            self.G.add_node(
                name,
                entity_type=entity_type,
                degree=0,
                weighted_degree=0.0,
                degree_centrality=0.0,
                first_appearance_year=first_year.get(name, 0),
                last_appearance_year=last_year.get(name, 0),
            )

    def _add_edges(self) -> None:
        assert self.G is not None and self.relations_df is not None
        cooccur_counts: Counter[Tuple[str, str]] = Counter()
        semantic_counts: Counter[Tuple[str, str]] = Counter()
        relation_types: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(dict)
        first_year: Dict[Tuple[str, str], int] = {}
        last_year: Dict[Tuple[str, str], int] = {}

        for _, row in self.relations_df.iterrows():
            u = normalize_entity_name(row["source_node"])
            v = normalize_entity_name(row["target_node"])
            if not u or not v or u == v or u not in self.G or v not in self.G:
                continue
            edge_key = tuple(sorted((u, v)))
            relation = normalize_label(row.get("relation"))
            if relation == "co_occurrence":
                cooccur_counts[edge_key] += 1
            elif relation in {"causal", "description", "contrast"}:
                semantic_counts[edge_key] += 1
            relation_types[edge_key][relation] = relation_types[edge_key].get(relation, 0) + 1
            if pd.notna(row.get("year")):
                year = int(row["year"])
                first_year[edge_key] = min(first_year.get(edge_key, year), year)
                last_year[edge_key] = max(last_year.get(edge_key, year), year)

        for edge_key in set(cooccur_counts) | set(semantic_counts):
            co_count = cooccur_counts.get(edge_key, 0)
            semantic_count = semantic_counts.get(edge_key, 0)
            weight = EDGE_WEIGHT_ALPHA * co_count + EDGE_WEIGHT_BETA * semantic_count
            if weight <= 0:
                continue
            u, v = edge_key
            self.G.add_edge(
                u,
                v,
                weight=float(weight),
                co_occur=int(co_count),
                causal=int(semantic_count),
                relation_types=relation_types.get(edge_key, {}),
                first_appearance_year=first_year.get(edge_key, 0),
                last_appearance_year=last_year.get(edge_key, 0),
                appearance_count=sum(relation_types.get(edge_key, {}).values()),
            )

    def _attach_sentiments(self) -> None:
        assert self.G is not None and self.entities_df is not None and self.sentiments_df is not None
        review_type_map: Dict[Tuple[str, str], list[str]] = defaultdict(list)
        for _, row in self.entities_df.iterrows():
            review_type_map[(str(row["review_id"]), normalize_label(row.get("entity_type")))].append(
                normalize_entity_name(row["entity_name"])
            )

        aggregates: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {"score_sum": 0.0, "count": 0, "positive": 0, "negative": 0, "neutral": 0})
        )
        for _, row in self.sentiments_df.iterrows():
            review_id = str(row["review_id"])
            aspect = normalize_label(row.get("aspect"), "general")
            score = safe_float(row.get("score"), 0.0)
            sentiment = normalize_label(row.get("sentiment"), "neutral")
            for entity_type in ASPECT_TO_ENTITY_TYPE.get(aspect, []):
                for entity in review_type_map.get((review_id, entity_type), []):
                    if entity not in self.G:
                        continue
                    bucket = aggregates[entity][aspect]
                    bucket["score_sum"] += score
                    bucket["count"] += 1
                    bucket[sentiment if sentiment in {"positive", "negative", "neutral"} else "neutral"] += 1

        for entity, aspects in aggregates.items():
            overall_scores = []
            for aspect, data in aspects.items():
                count = data["count"] or 1
                avg_score = data["score_sum"] / count
                overall_scores.append(avg_score)
                self.G.nodes[entity][f"sentiment_{aspect}"] = {
                    "score": float(avg_score),
                    "positive_ratio": float(data["positive"] / count),
                    "negative_ratio": float(data["negative"] / count),
                    "count": int(data["count"]),
                }
            if overall_scores:
                self.G.nodes[entity]["sentiment_overall"] = float(sum(overall_scores) / len(overall_scores))

    def _attach_review_counts(self) -> None:
        assert self.G is not None and self.entities_df is not None
        counts = self.entities_df.assign(
            entity_name_norm=self.entities_df["entity_name"].map(normalize_entity_name)
        ).groupby("entity_name_norm")["review_id"].nunique()
        for node, count in counts.items():
            if node in self.G:
                self.G.nodes[node]["appearance_count"] = int(count)

