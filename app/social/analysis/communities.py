"""Thematic community detection with Louvain clustering."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List

import networkx as nx
from loguru import logger

from app.social.graph.services import (
    EntityTypeService,
    GraphAttributeService,
    GraphMetricsService,
    NodeSentimentService,
)
from app.social.models.results import CommunityAnalysisResult, CommunityStats, NetworkContext


ENTITY_THEME_LABELS = {
    "ritual": "Rituals and Worship",
    "religious_actor": "Holy People and Guides",
    "sacred_space": "Sacred Places",
    "spiritual_emotion": "Spiritual Feelings",
    "cultural_rule": "Rules and Respect",
    "problem": "Visitor Problems",
    "festival_event": "Festivals and Events",
    "sacred_object": "Sacred Objects",
    "dual_valence": "Mixed Feelings",
    "facility_service": "Facilities and Services",
    "scenic_spot": "Views and Landmarks",
    "general_sentiment": "Overall Visitor Impressions",
}


class CommunityAnalyzer:
    """Detect and summarize thematic communities in the heritage network."""

    name = "communities"

    def __init__(self, top_n: int = 10):
        self.top_n = top_n

    def analyze(self, context: NetworkContext) -> CommunityAnalysisResult:
        G = context.graph
        logger.info("Running Louvain thematic community detection...")
        assignments = self._detect_louvain(G)
        GraphAttributeService.assign_communities(G, assignments)
        modularity = self._modularity(G, assignments)
        communities = self._summarize(G, assignments)
        community_names = {
            community.community_id: community.community_name
            for community in communities
        }
        GraphAttributeService.assign_node_attributes(
            G,
            {
                node: {"community_name": community_names.get(community_id, f"Theme {community_id}")}
                for node, community_id in assignments.items()
            },
        )
        return CommunityAnalysisResult(
            assignments=assignments,
            modularity=modularity,
            communities=communities,
        )

    def _detect_louvain(self, G: nx.Graph) -> Dict[str, int]:
        if G.number_of_nodes() == 0:
            return {}
        try:
            import community as community_louvain

            return {
                str(node): int(cid)
                for node, cid in community_louvain.best_partition(G, weight="weight", random_state=42).items()
            }
        except Exception as exc:
            logger.warning(f"python-louvain unavailable, trying NetworkX Louvain fallback: {exc}")
        try:
            communities = nx.algorithms.community.louvain_communities(G, weight="weight", seed=42)
            assignments = {}
            for cid, nodes in enumerate(communities):
                for node in nodes:
                    assignments[str(node)] = cid
            return assignments
        except Exception as exc:
            logger.warning(f"Louvain detection unavailable, using connected components fallback: {exc}")
            assignments = {}
            for cid, component in enumerate(nx.connected_components(G)):
                for node in component:
                    assignments[str(node)] = cid
            return assignments

    def _modularity(self, G: nx.Graph, assignments: Dict[str, int]) -> float:
        if G.number_of_edges() == 0 or not assignments:
            return 0.0
        communities = defaultdict(set)
        for node, community_id in assignments.items():
            communities[community_id].add(node)
        try:
            return float(nx.algorithms.community.modularity(G, communities.values(), weight="weight"))
        except Exception:
            return 0.0

    def _summarize(self, G: nx.Graph, assignments: Dict[str, int]) -> List[CommunityStats]:
        degree_centrality = nx.degree_centrality(G) if G.number_of_nodes() > 1 else {}
        grouped = defaultdict(list)
        for node, community_id in assignments.items():
            grouped[community_id].append(node)

        summaries = []
        for community_id, nodes in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
            subgraph = G.subgraph(nodes).copy()
            type_counts = EntityTypeService.type_counts(G, nodes)
            top_nodes = GraphMetricsService.top_nodes(G, degree_centrality, limit=G.number_of_nodes())
            top_nodes = [row for row in top_nodes if row["node"] in set(nodes)][: self.top_n]
            dominant_type = Counter(type_counts).most_common(1)[0][0] if type_counts else "unknown"
            summaries.append(
                CommunityStats(
                    community_id=int(community_id),
                    community_name=self._community_name(dominant_type, top_nodes),
                    node_count=len(nodes),
                    edge_count=subgraph.number_of_edges(),
                    dominant_entity_type=dominant_type,
                    average_sentiment=NodeSentimentService.average_sentiment(G, nodes),
                    density=GraphMetricsService.density(subgraph),
                    top_nodes=top_nodes,
                    entity_type_counts=type_counts,
                )
            )
        return summaries

    def _community_name(self, dominant_type: str, top_nodes: List[Dict[str, object]]) -> str:
        base = ENTITY_THEME_LABELS.get(dominant_type, "Visitor Experience")
        clean_nodes = []
        for row in top_nodes:
            node = str(row.get("node", "")).strip()
            if not node or len(node) > 42:
                continue
            if node.lower() in {"good", "bad", "nice", "different", "place", "thing", "things"}:
                continue
            clean_nodes.append(node.title())
            if len(clean_nodes) == 2:
                break
        if len(clean_nodes) >= 2:
            return f"{base}: {clean_nodes[0]} and {clean_nodes[1]}"
        if clean_nodes:
            return f"{base}: {clean_nodes[0]}"
        return base
