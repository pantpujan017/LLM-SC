# app/social/__init__.py
"""
PHASE 3: Social Network Computing Layer

Heterogeneous Information Network (HIN) construction, analysis, and visualization
for sacred heritage site experience networks.

Architecture:
- Models: Pydantic schemas for Node, Edge, Network structures
- Loaders: CSV data ingestion with normalization
- Builders: Graph construction with deduplication and weighted edges
- Analysis: Centrality, entropy, temporal evolution, community detection
- Visualization: GraphML export, JSON metrics, interactive dashboards
- Exporters: Multi-format output (GraphML, JSON, reports)
"""

__version__ = "3.0"
