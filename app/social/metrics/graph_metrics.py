"""Global network metric calculation."""

from __future__ import annotations

from typing import Dict

import networkx as nx

from app.social.graph.services import GraphMetricsService


def compute_global_graph_metrics(G: nx.Graph, centrality: Dict[str, float] | None = None) -> Dict[str, float | int]:
    """Compute reusable global network metrics."""
    assortativity = 0.0
    if G.number_of_edges() > 0:
        try:
            assortativity = float(nx.degree_assortativity_coefficient(G, weight="weight"))
        except Exception:
            assortativity = 0.0
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": GraphMetricsService.density(G),
        "components": GraphMetricsService.connected_components(G),
        "clustering_coefficient": GraphMetricsService.average_clustering(G),
        "centralization": GraphMetricsService.centralization(G, centrality),
        "degree_assortativity": assortativity,
    }

