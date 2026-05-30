# app/social/models/schemas.py

"""
Pydantic data models for PHASE 3 Social Network Computing.

Defines Node, Edge, and Network structures with full validation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class SentimentAttribute(BaseModel):
    """Sentiment score for a specific aspect (service, facility, environment, etc.)"""
    
    aspect: str                    # aspect name (service, facility, sacred_atmosphere, etc.)
    score: float                   # sentiment score (0.0 - 1.0)
    positive_ratio: float          # % positive (0.0 - 1.0)
    negative_ratio: float          # % negative (0.0 - 1.0)
    review_count: int              # number of reviews contributing to this aspect


class Node(BaseModel):
    """
    Heterogeneous Information Network Node
    
    Represents a unique entity (concept-level deduplication).
    One node per unique entity name, enriched with attributes.
    """
    
    name: str                      # Entity name (lowercase, deduplicated)
    entity_type: str               # Entity type (from ENTITY_TYPES)
    degree: int = 0                # Degree (set during graph analysis)
    weighted_degree: float = 0.0   # Strength (sum of edge weights)
    degree_centrality: float = 0.0 # Degree centrality C_D(v) = deg(v)/(n-1)
    
    # Sentiment enrichment
    sentiment_aspects: Dict[str, SentimentAttribute] = Field(default_factory=dict)
    overall_sentiment_score: float = 0.0  # Average across all aspects
    
    # Temporal attributes
    first_appearance_year: int = 0
    last_appearance_year: int = 0
    appearance_count: int = 0     # How many reviews mention this entity
    
    class Config:
        """Pydantic config"""
        frozen = False
        extra = "allow"  # Allow extra fields from data source

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Ensure names are lowercase and stripped"""
        return v.lower().strip()


class Edge(BaseModel):
    """
    Heterogeneous Information Network Edge
    
    Weighted edge between two nodes.
    Preserves relation type counts for transparency.
    """
    
    source: str                   # Source node name
    target: str                   # Target node name
    weight: float                 # w_ij = α*f_cooccur + β*g_causal
    co_occur_count: int = 0       # f_cooccur (co-occurrence frequency)
    causal_count: int = 0         # g_causal (causal/description/contrast frequency)
    
    # Relation type breakdown
    relation_types: Dict[str, int] = Field(default_factory=dict)
    
    # Temporal span
    first_appearance_year: int = 0
    last_appearance_year: int = 0
    appearance_count: int = 0     # Reviews with this relation
    
    class Config:
        """Pydantic config"""
        frozen = False
        extra = "allow"

    @field_validator("source", "target")
    @classmethod
    def normalize_endpoints(cls, v: str) -> str:
        """Ensure endpoint names are normalized"""
        return v.lower().strip()

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Weight should be non-negative"""
        if v < 0:
            raise ValueError(f"Edge weight must be non-negative, got {v}")
        return v


class TemporalStats(BaseModel):
    """Network statistics for a specific temporal period"""
    
    period: str                    # Period name (early_period, covid_onset, etc.)
    year_range: tuple             # (start_year, end_year)
    review_count: int             # Number of reviews in period
    
    # Graph metrics
    node_count: int               # V
    edge_count: int               # E
    density: float                # E / (V*(V-1)/2) for undirected
    
    # Semantic composition
    sacred_entity_count: int      # Nodes with sacred entity types
    sacred_entity_pct: float      # Percentage
    dual_valence_count: int       # Dual-valence nodes
    spiritual_emotion_count: int  # Spiritual emotion nodes
    
    # Sentiment
    avg_sentiment_score: float    # Mean sentiment across all sentiments
    
    class Config:
        """Pydantic config"""
        frozen = False


class TripTypeStats(BaseModel):
    """Visitor segment statistics by TripAdvisor trip type."""

    trip_type: str
    review_count: int = 0
    sacred_entity_pct: float = 0.0
    dual_valence_pct: float = 0.0
    spiritual_emotion_pct: float = 0.0
    avg_sentiment_score: float = 0.0
    profile: str = "Visitor segment"


class AspectSentimentStats(BaseModel):
    """Human-readable aspect sentiment summary."""

    aspect: str
    label: str
    count: int = 0
    positive_pct: float = 0.0
    negative_pct: float = 0.0
    avg_score: float = 0.0
    type: str = "Other"
    interpretation: str = ""


class TypeCentrality(BaseModel):
    """Centrality statistics aggregated by entity type"""
    
    entity_type: str              # Type name
    node_count: int               # Number of nodes of this type
    avg_degree_centrality: float  # Mean degree centrality
    max_degree_centrality: float  # Max degree centrality (hub of type)
    avg_weighted_degree: float    # Mean strength
    sacred: bool                  # Is this a sacred type?


class Network(BaseModel):
    """
    Complete Heterogeneous Information Network representation
    
    Full network snapshot with all nodes, edges, and metadata.
    """
    
    # Metadata
    name: str = "Pashupatinath Experience Network"
    phase: str = "PHASE 3"
    version: str = "3.0"
    site: str = "Pashupatinath Temple"
    
    # Graph structure
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    
    # Global metrics
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0
    
    # Information entropy
    entropy: float = 0.0          # H = -Σ p(i) * log2(p(i))
    entropy_vs_traditional_pct: float = 0.0  # Improvement vs traditional NLP
    
    # Components
    component_count: int = 0
    largest_component_pct: float = 0.0
    
    # Centrality summary
    top_nodes: List[Dict[str, Any]] = Field(default_factory=list)  # Top 20 by centrality
    type_centrality: Dict[str, TypeCentrality] = Field(default_factory=dict)
    
    # Temporal evolution
    temporal_stats: Dict[str, TemporalStats] = Field(default_factory=dict)
    detailed_temporal_stats: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Sacred vs non-sacred segmentation
    sacred_nodes_count: int = 0
    sacred_nodes_avg_centrality: float = 0.0
    nonsacred_nodes_count: int = 0
    nonsacred_nodes_avg_centrality: float = 0.0
    
    # Trip type segmentation
    trip_type_stats: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    detailed_trip_type_stats: Dict[str, TripTypeStats] = Field(default_factory=dict)
    aspect_sentiment_stats: Dict[str, AspectSentimentStats] = Field(default_factory=dict)
    hub_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Data provenance
    reviews_count: int = 0
    entities_count: int = 0  # Raw entity mentions
    relations_count: int = 0  # Raw relation mentions
    sentiments_count: int = 0  # Sentiment records
    
    class Config:
        """Pydantic config"""
        frozen = False
        extra = "allow"
