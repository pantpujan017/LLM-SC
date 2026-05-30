"""Sentiment propagation, homophily, and emotional anchor analysis."""

from __future__ import annotations

from typing import Dict, List

import networkx as nx
import numpy as np
from loguru import logger

from app.social.graph.services import GraphAttributeService, NodeSentimentService
from app.social.models.results import EmotionalAnchor, NetworkContext, SentimentFlowResult


class SentimentFlowAnalyzer:
    """Analyze emotional organization across weighted graph ties."""

    name = "sentiment_flow"

    def __init__(self, top_n: int = 15):
        self.top_n = top_n

    def analyze(self, context: NetworkContext) -> SentimentFlowResult:
        logger.info("Analyzing sentiment propagation and assortativity...")
        G = context.graph
        sentiments = {node: NodeSentimentService.node_sentiment(G, node, 0.5) for node in G.nodes()}
        labels = {node: NodeSentimentService.sentiment_label(score) for node, score in sentiments.items()}
        assortativity = self._assortativity(G, labels)
        homophily = self._homophily(G, labels)
        correlation = self._edge_sentiment_correlation(G, sentiments)
        clustering = self._sentiment_clustering(G, sentiments)
        anchors = self._anchors(G, sentiments, labels)

        GraphAttributeService.assign_node_attributes(
            G,
            {
                anchor.node: {
                    "emotional_influence_score": anchor.emotional_influence_score,
                    "sentiment_role": anchor.role,
                }
                for anchor in anchors
            },
        )

        hubs = [anchor for anchor in anchors if anchor.role == "hub"][: self.top_n]
        sinks = [anchor for anchor in anchors if anchor.role == "sink"][: self.top_n]
        return SentimentFlowResult(
            assortativity_score=assortativity,
            homophily_score=homophily,
            sentiment_correlation=correlation,
            sentiment_clustering_coefficient=clustering,
            emotional_anchors=anchors[: self.top_n],
            sentiment_hubs=hubs,
            sentiment_sinks=sinks,
        )

    def _assortativity(self, G: nx.Graph, labels: Dict[str, str]) -> float:
        if G.number_of_edges() == 0:
            return 0.0
        nx.set_node_attributes(G, labels, "_sentiment_label_tmp")
        try:
            return float(nx.attribute_assortativity_coefficient(G, "_sentiment_label_tmp"))
        except Exception:
            return 0.0
        finally:
            for node in G.nodes:
                G.nodes[node].pop("_sentiment_label_tmp", None)

    def _homophily(self, G: nx.Graph, labels: Dict[str, str]) -> float:
        same_weight = 0.0
        total_weight = 0.0
        for u, v, data in G.edges(data=True):
            weight = float(data.get("weight", 1.0))
            total_weight += weight
            if labels[u] == labels[v]:
                same_weight += weight
        return same_weight / total_weight if total_weight else 0.0

    def _edge_sentiment_correlation(self, G: nx.Graph, sentiments: Dict[str, float]) -> float:
        if G.number_of_edges() == 0:
            return 0.0
        left = []
        right = []
        for u, v in G.edges():
            left.append(sentiments[u])
            right.append(sentiments[v])
        if len(set(left)) < 2 or len(set(right)) < 2:
            return 0.0
        return float(np.corrcoef(left, right)[0, 1])

    def _sentiment_clustering(self, G: nx.Graph, sentiments: Dict[str, float]) -> float:
        if G.number_of_nodes() < 3:
            return 0.0
        coefficients = []
        for node in G.nodes():
            neighbors = list(G.neighbors(node))
            if len(neighbors) < 2:
                continue
            node_score = sentiments[node]
            similar = [n for n in neighbors if abs(sentiments[n] - node_score) <= 0.15]
            if len(similar) < 2:
                coefficients.append(0.0)
                continue
            subgraph = G.subgraph(similar)
            coefficients.append(nx.density(subgraph))
        return float(np.mean(coefficients)) if coefficients else 0.0

    def _anchors(
        self,
        G: nx.Graph,
        sentiments: Dict[str, float],
        labels: Dict[str, str],
    ) -> List[EmotionalAnchor]:
        anchors = []
        for node in G.nodes():
            same_weight = 0.0
            opposite_weight = 0.0
            weighted_delta = 0.0
            for neighbor in G.neighbors(node):
                weight = float(G.edges[node, neighbor].get("weight", 1.0))
                delta = abs(sentiments[node] - sentiments[neighbor])
                weighted_delta += weight * delta
                if labels[node] == labels[neighbor]:
                    same_weight += weight
                else:
                    opposite_weight += weight
            influence = weighted_delta + opposite_weight
            if influence <= 0:
                continue
            role = "sink" if opposite_weight > same_weight else "hub"
            anchors.append(
                EmotionalAnchor(
                    node=node,
                    entity_type=G.nodes[node].get("entity_type", "unknown"),
                    sentiment=float(sentiments[node]),
                    emotional_influence_score=float(influence),
                    opposite_weight=float(opposite_weight),
                    same_weight=float(same_weight),
                    role=role,
                )
            )
        return sorted(anchors, key=lambda anchor: -anchor.emotional_influence_score)

