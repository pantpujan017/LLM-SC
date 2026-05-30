"""Typed result objects for social network analyses."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd


@dataclass
class SocialDataBundle:
    """Loaded and cleaned tables used by the social pipeline."""

    entities: pd.DataFrame
    relations: pd.DataFrame
    sentiments: pd.DataFrame
    reviews: Optional[pd.DataFrame] = None


@dataclass
class NetworkContext:
    """Shared state passed between pipeline stages."""

    graph: nx.Graph
    data: SocialDataBundle
    output_dir: Path


@dataclass
class CentralityResult:
    degree_centrality: Dict[str, float]
    strength: Dict[str, float]
    top_nodes: List[Tuple[str, float]]
    type_centrality: Dict[str, Dict[str, float]]


@dataclass
class CoreAnalysisResults:
    centrality: CentralityResult
    entropy: Dict[str, float]
    temporal: Dict[str, Dict[str, Any]]
    sacred: Dict[str, Dict[str, Any]]
    trip_type: Dict[str, Dict[str, Any]]
    aspect_sentiment: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class CommunityStats:
    community_id: int
    community_name: str
    node_count: int
    edge_count: int
    dominant_entity_type: str
    average_sentiment: float
    density: float
    top_nodes: List[Dict[str, Any]]
    entity_type_counts: Dict[str, int]


@dataclass
class CommunityAnalysisResult:
    assignments: Dict[str, int]
    modularity: float
    communities: List[CommunityStats]


@dataclass
class MetaPathMetric:
    path: str
    node_types: List[str]
    frequency: int
    prevalence: float
    significance: float
    group_frequencies: Dict[str, int] = field(default_factory=dict)


@dataclass
class MetaPathAnalysisResult:
    paths: List[MetaPathMetric]
    total_observed_paths: int
    pilgrim_vs_tourist: Dict[str, Dict[str, int]]


@dataclass
class EmotionalAnchor:
    node: str
    entity_type: str
    sentiment: float
    emotional_influence_score: float
    opposite_weight: float
    same_weight: float
    role: str


@dataclass
class SentimentFlowResult:
    assortativity_score: float
    homophily_score: float
    sentiment_correlation: float
    sentiment_clustering_coefficient: float
    emotional_anchors: List[EmotionalAnchor]
    sentiment_hubs: List[EmotionalAnchor]
    sentiment_sinks: List[EmotionalAnchor]


@dataclass
class MotifMetric:
    motif_type: str
    entity_composition: str
    frequency: int
    periods: Dict[str, int]
    persistence: int
    survival_rate: float
    covid_resilience: str


@dataclass
class MotifAnalysisResult:
    motifs: List[MotifMetric]
    disappeared_after_covid: List[str]
    survived_covid: List[str]
    emerged_after_recovery: List[str]


@dataclass
class AdvancedAnalysisResults:
    communities: CommunityAnalysisResult
    metapaths: MetaPathAnalysisResult
    sentiment_flow: SentimentFlowResult
    motifs: MotifAnalysisResult


@dataclass
class PipelineResult:
    context: NetworkContext
    core: CoreAnalysisResults
    advanced: AdvancedAnalysisResults
    exports: Dict[str, str] = field(default_factory=dict)
