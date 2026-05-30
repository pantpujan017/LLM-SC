"""JSON exporters for network metrics and node-level data."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import networkx as nx
from loguru import logger

from app.social.metrics import compute_global_graph_metrics
from app.social.models.results import AdvancedAnalysisResults, CoreAnalysisResults
from app.social.utils.serialization import to_jsonable, write_json
from app.social.config.constants import PERIOD_LABELS, SACRED_ENTITY_TYPES


class JSONExporter:
    """Exports network metrics and node attributes to JSON."""

    def __init__(self, output_dir: Path | str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_metrics(
        self,
        G: nx.Graph,
        core: CoreAnalysisResults,
        advanced: AdvancedAnalysisResults,
        filename: str = "network_metrics.json",
    ) -> Path:
        logger.info("Exporting network metrics JSON...")
        hub_analysis = self._hub_analysis(G, core)
        temporal_detail = self._temporal_detail(core)
        trip_type_profiles = self._trip_type_profiles(core)
        aspect_sentiment = self._aspect_sentiment(core)
        dual_valence_total = sum(
            stats.get("dual_valence_count", 0)
            for stats in core.temporal.values()
        )
        metrics = {
            "graph": compute_global_graph_metrics(G, core.centrality.degree_centrality),
            "entropy": core.entropy,
            "centrality": {
                "top_20_nodes": [
                    {"node": node, "centrality": score}
                    for node, score in core.centrality.top_nodes[:20]
                ],
                "top_10_hubs": hub_analysis["top_10_hubs"],
                "type_centrality": core.centrality.type_centrality,
                "type_centrality_table": hub_analysis["type_centrality_table"],
            },
            "temporal": core.temporal,
            "temporal_detail": temporal_detail,
            "sacred_secular": core.sacred,
            "trip_type": core.trip_type,
            "trip_type_profiles": trip_type_profiles,
            "aspect_sentiment": aspect_sentiment,
            "story_metrics": {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "entropy_increase_pct": core.entropy.get("improvement_pct", 0.0),
                "dual_valence_instances": dual_valence_total,
            },
            "hub_analysis": hub_analysis,
            "advanced": {
                "communities": {
                    "modularity": advanced.communities.modularity,
                    "community_count": len(advanced.communities.communities),
                    "communities": advanced.communities.communities,
                },
                "metapaths": {
                    "total_observed_paths": advanced.metapaths.total_observed_paths,
                    "paths": advanced.metapaths.paths,
                    "pilgrim_vs_tourist": advanced.metapaths.pilgrim_vs_tourist,
                },
                "sentiment_flow": advanced.sentiment_flow,
                "motifs": advanced.motifs,
            },
            "community_metrics": advanced.communities,
            "meta_path_metrics": advanced.metapaths,
            "sentiment_metrics": advanced.sentiment_flow,
            "motif_metrics": advanced.motifs,
        }
        output_path = self.output_dir / filename
        write_json(output_path, metrics)
        logger.success(f"JSON metrics exported: {output_path}")
        return output_path

    def _hub_analysis(self, G: nx.Graph, core: CoreAnalysisResults) -> Dict[str, Any]:
        top_hubs = []
        for rank, (node, centrality) in enumerate(core.centrality.top_nodes[:10], 1):
            attrs = G.nodes[node]
            entity_type = attrs.get("entity_type", "unknown")
            top_hubs.append(
                {
                    "rank": rank,
                    "idea": node,
                    "entity_type": entity_type,
                    "category": "Sacred" if entity_type in SACRED_ENTITY_TYPES else "Non-sacred",
                    "prominence_score": centrality,
                    "degree": int(G.degree(node)),
                    "community_name": attrs.get("community_name", ""),
                    "why_it_matters": self._hub_interpretation(node, entity_type),
                }
            )

        type_rows = []
        for entity_type, stats in core.centrality.type_centrality.items():
            type_rows.append(
                {
                    "entity_type": entity_type,
                    "label": entity_type.replace("_", " ").title(),
                    "category": "Sacred" if entity_type in SACRED_ENTITY_TYPES else "Non-sacred",
                    "node_count": stats.get("count", 0),
                    "avg_centrality": stats.get("avg_degree_centrality", 0.0),
                    "max_centrality": stats.get("max_degree_centrality", 0.0),
                    "avg_weighted_degree": stats.get("avg_weighted_degree", 0.0),
                }
            )
        type_rows.sort(key=lambda row: row["avg_centrality"], reverse=True)
        return {
            "top_10_hubs": top_hubs,
            "type_centrality_table": type_rows,
        }

    def _temporal_detail(self, core: CoreAnalysisResults) -> Dict[str, Dict[str, Any]]:
        return {
            period: {
                "period": period,
                "label": PERIOD_LABELS.get(period, period.replace("_", " ").title()),
                "year_range": stats.get("year_range"),
                "review_count": stats.get("review_count", 0),
                "sacred_entity_pct": stats.get("sacred_entity_pct", 0.0),
                "avg_sentiment_score": stats.get("avg_sentiment_score", 0.0),
                "dual_valence_count": stats.get("dual_valence_count", 0),
                "spiritual_emotion_count": stats.get("spiritual_emotion_count", 0),
                "density": stats.get("density", 0.0),
                "node_count": stats.get("node_count", 0),
                "edge_count": stats.get("edge_count", 0),
            }
            for period, stats in core.temporal.items()
        }

    def _trip_type_profiles(self, core: CoreAnalysisResults) -> Dict[str, Dict[str, Any]]:
        return {
            trip_type: {
                "trip_type": trip_type,
                "label": trip_type.title(),
                "review_count": stats.get("review_count", 0),
                "sacred_entity_pct": stats.get("sacred_entity_pct", 0.0),
                "dual_valence_pct": stats.get("dual_valence_pct", 0.0),
                "spiritual_emotion_pct": stats.get("spiritual_emotion_pct", 0.0),
                "avg_sentiment_score": stats.get("avg_sentiment_score", 0.0),
                "profile": stats.get("profile", "Visitor segment"),
            }
            for trip_type, stats in core.trip_type.items()
        }

    def _aspect_sentiment(self, core: CoreAnalysisResults) -> Dict[str, Dict[str, Any]]:
        order = [
            "spiritual_authenticity",
            "sacred_atmosphere",
            "ritual_experience",
            "service",
            "facility",
            "cultural_sensitivity",
            "environment",
            "crowd_management",
            "access_fairness",
        ]
        return {
            aspect: core.aspect_sentiment[aspect]
            for aspect in order
            if aspect in core.aspect_sentiment
        }

    @staticmethod
    def _hub_interpretation(node: str, entity_type: str) -> str:
        if entity_type in SACRED_ENTITY_TYPES:
            return "Central to the sacred visitor experience"
        if "ban" in node.lower() or entity_type == "cultural_rule":
            return "A major access and cultural-rule tension"
        if entity_type == "problem":
            return "A recurring visitor concern"
        return "Frequently connected to many visitor stories"

    def export_node_data(
        self,
        G: nx.Graph,
        core: CoreAnalysisResults,
        advanced: AdvancedAnalysisResults,
        filename: str = "node_data.json",
    ) -> Path:
        logger.info("Exporting node data JSON...")
        community_lookup = advanced.communities.assignments
        node_data: Dict[str, Dict[str, Any]] = {}
        for node, attrs in G.nodes(data=True):
            node_data[node] = {
                "type": attrs.get("entity_type", "unknown"),
                "degree": int(G.degree(node)),
                "centrality": core.centrality.degree_centrality.get(node, 0.0),
                "weighted_degree": core.centrality.strength.get(node, 0.0),
                "community_id": community_lookup.get(node),
                "community_name": attrs.get("community_name", ""),
                "advanced_metrics": {
                    "community_id": community_lookup.get(node),
                    "community_name": attrs.get("community_name", ""),
                    "emotional_influence_score": attrs.get("emotional_influence_score", 0.0),
                    "sentiment_role": attrs.get("sentiment_role", "none"),
                },
                "attributes": {k: v for k, v in attrs.items() if not str(k).startswith("_")},
            }
        output_path = self.output_dir / filename
        write_json(output_path, to_jsonable(node_data))
        logger.success(f"Node data exported: {output_path}")
        return output_path
