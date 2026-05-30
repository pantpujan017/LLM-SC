"""Temporal 3-node motif mining."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Dict, Iterable, List, Tuple

import networkx as nx
from loguru import logger

from app.social.config.constants import TEMPORAL_PERIODS
from app.social.graph.services import TemporalGraphService
from app.social.models.results import MotifAnalysisResult, MotifMetric, NetworkContext


class MotifAnalyzer:
    """Detect 3-node triangles, chains, and stars across temporal periods."""

    name = "motifs"

    def __init__(self, max_nodes_per_period: int = 800):
        self.max_nodes_per_period = max_nodes_per_period

    def analyze(self, context: NetworkContext) -> MotifAnalysisResult:
        logger.info("Mining temporal semantic motifs...")
        temporal_service = TemporalGraphService(context.graph, context.data.entities)
        period_counts: Dict[str, Counter[Tuple[str, str]]] = {}
        for period, (start, end) in TEMPORAL_PERIODS.items():
            Gp = temporal_service.period_subgraph(start, end)
            period_counts[period] = self._count_motifs(Gp)

        all_keys = set().union(*(counts.keys() for counts in period_counts.values())) if period_counts else set()
        metrics = []
        active_period_count = len(TEMPORAL_PERIODS)
        for key in all_keys:
            motif_type, composition = key
            periods = {period: int(counts.get(key, 0)) for period, counts in period_counts.items()}
            frequency = sum(periods.values())
            persistence = sum(1 for value in periods.values() if value > 0)
            survival_rate = persistence / active_period_count if active_period_count else 0.0
            metrics.append(
                MotifMetric(
                    motif_type=motif_type,
                    entity_composition=composition,
                    frequency=int(frequency),
                    periods=periods,
                    persistence=int(persistence),
                    survival_rate=float(survival_rate),
                    covid_resilience=self._resilience_label(periods),
                )
            )

        metrics = sorted(metrics, key=lambda metric: (-metric.frequency, metric.entity_composition))
        disappeared = [m.entity_composition for m in metrics if m.covid_resilience == "disappeared_after_covid"][:20]
        survived = [m.entity_composition for m in metrics if m.covid_resilience == "survived_covid"][:20]
        emerged = [m.entity_composition for m in metrics if m.covid_resilience == "emerged_after_recovery"][:20]
        return MotifAnalysisResult(
            motifs=metrics[:200],
            disappeared_after_covid=disappeared,
            survived_covid=survived,
            emerged_after_recovery=emerged,
        )

    def _count_motifs(self, G: nx.Graph) -> Counter[Tuple[str, str]]:
        if G.number_of_nodes() > self.max_nodes_per_period:
            scores = dict(G.degree(weight="weight"))
            keep = {
                node
                for node, _ in sorted(scores.items(), key=lambda item: -item[1])[: self.max_nodes_per_period]
            }
            G = G.subgraph(keep).copy()

        counts: Counter[Tuple[str, str]] = Counter()
        seen = set()
        for center in G.nodes():
            neighbors = list(G.neighbors(center))
            for u, v in combinations(neighbors, 2):
                triple = tuple(sorted((u, center, v)))
                if triple in seen:
                    continue
                edge_count = int(G.has_edge(u, center)) + int(G.has_edge(center, v)) + int(G.has_edge(u, v))
                if edge_count < 2:
                    continue
                seen.add(triple)
                motif_type = "triangle" if edge_count == 3 else "chain"
                composition = self._composition(G, triple)
                counts[(motif_type, composition)] += 1
        return counts

    @staticmethod
    def _composition(G: nx.Graph, nodes: Iterable[str]) -> str:
        types = sorted(G.nodes[node].get("entity_type", "unknown") for node in nodes)
        return " + ".join(types)

    @staticmethod
    def _resilience_label(periods: Dict[str, int]) -> str:
        pre = periods.get("pre_covid_peak", 0) + periods.get("growth_period", 0)
        covid = periods.get("covid_onset", 0) + periods.get("covid_deep", 0)
        recovery = (
            periods.get("recovery_early", 0)
            + periods.get("recovery_late", 0)
            + periods.get("post_recovery", 0)
        )
        if pre > 0 and covid == 0 and recovery == 0:
            return "disappeared_after_covid"
        if pre > 0 and covid > 0 and recovery > 0:
            return "survived_covid"
        if pre == 0 and covid == 0 and recovery > 0:
            return "emerged_after_recovery"
        if recovery > pre:
            return "recovered_or_growing"
        return "intermittent"

