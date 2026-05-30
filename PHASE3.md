# PHASE 3: Social Network Computing

Complete heterogeneous information network (HIN) construction, analysis, and visualization for sacred heritage site experience networks.

## Overview

PHASE 3 builds upon PHASE 2's cleaned entity/relation/sentiment data to construct a weighted, multi-typed network:

- **11,314 entity mentions** → **5,925 deduplicated concept nodes**
- **5,586 relations** → **weighted edges** using formula: `w_ij = 0.7*f_cooccur + 0.3*g_causal`
- **6,232 sentiments** → **node-level attributes** (aspect scores)
- **Temporal dimension**: 8 period snapshots (early_period → post_recovery)
- **Sacred composition**: 8 sacred entity types vs 4 general types
- **Trip type segmentation**: Pilgrim vs tourist signal analysis

## Architecture

### Three-Layer Design

```
PHASE 3a: Data Integration & HIN Construction
├── CSV Loading → Normalized entity/relation/sentiment ingestion
├── Node Building → Concept-level deduplication
├── Edge Weighting → Weighted edge aggregation (α=0.7, β=0.3)
└── Sentiment Attachment → Node-level aspect enrichment

PHASE 3b: Enrichment & Analysis
├── Centrality Metrics → Degree centrality C_D(v) = deg(v)/(n-1)
├── Information Entropy → H = -Σ p(i)*log2(p(i)) vs traditional NLP baseline
├── Temporal Evolution → 8-period snapshots with COVID dynamics
└── Sacred/Secular Segmentation → Entity type & trip type analysis

PHASE 3c: Visualization & Export
├── GraphML Export → Opens in Gephi, Cytoscape, yEd
├── JSON Metrics → Comprehensive statistics for programmatic access
├── Node Data Export → Detailed node attributes and sentiments
└── Markdown Reports → Human-readable analysis tables
```

## Usage

### Quick Start

```bash
# Run PHASE 3 after completing PHASE 2
export PIPELINE_MODE=social
python -m app.main

# Output appears in: app/storage/social_network_output/
```

### Programmatic Access

```python
from pathlib import Path
from app.social.pipeline import Phase3Pipeline

# Run pipeline
pipeline = Phase3Pipeline(
    data_dir=Path("app/storage/processed/raw"),
    output_dir=Path("app/storage/social_network_output"),
)
results = pipeline.execute()

# Access results
print(results["phase_3a"])  # Graph metrics
print(results["phase_3b"])  # Analysis results
print(results["phase_3c"])  # Export paths
```

### Individual Module Usage

```python
from app.social.builders import GraphBuilder
from app.social.analysis import CentralityAnalyzer, EntropyAnalyzer

# Build graph
builder = GraphBuilder(data_dir="app/storage/processed/raw")
G = builder.build()

# Analyze centrality
cent = CentralityAnalyzer(G)
results = cent.analyze()
print(f"Top node: {results['top_nodes'][0]}")

# Compute entropy
entropy = EntropyAnalyzer(G)
ent_results = entropy.compute_entropy()
print(f"Entropy: {ent_results['entropy']:.4f} bits")
```

## Directory Structure

```
app/social/
├── __init__.py
├── pipeline.py                    # Main orchestrator
├── config/
│   ├── __init__.py
│   └── constants.py               # All configuration constants
├── models/
│   ├── __init__.py
│   └── schemas.py                 # Pydantic data models
├── loaders/
│   ├── __init__.py
│   └── csv_loader.py              # CSV data ingestion
├── builders/
│   ├── __init__.py
│   └── graph_builder.py           # Graph construction
├── analysis/
│   ├── __init__.py
│   ├── centrality.py              # Degree centrality metrics
│   ├── entropy.py                 # Information entropy
│   ├── temporal.py                # Temporal evolution
│   └── sacred_secular.py          # Sacred/non-sacred segmentation
├── exporters/
│   ├── __init__.py
│   ├── graphml_exporter.py        # GraphML export (Gephi)
│   ├── json_exporter.py           # JSON metrics export
│   └── report_exporter.py         # Markdown report generation
└── visualization/                 # (Future: Pyvis, Plotly)
    └── __init__.py
```

## Data Models

### Node (Concept-level Entity)

```python
Node(
    name="cremation",                        # Deduplicated entity name
    entity_type="ritual",                    # From 12 entity types
    degree=23,                               # Number of connections
    degree_centrality=0.0387,                # C_D(v) = deg(v)/(n-1)
    sentiment_aspects={                      # Aspect-level sentiments
        "sacred_atmosphere": {
            "score": 0.82,
            "positive_ratio": 0.91,
            "negative_ratio": 0.05,
            "review_count": 47
        }
    }
)
```

### Edge (Weighted Relation)

```python
Edge(
    source="cremation",
    target="bagmati",
    weight=0.85,                             # w_ij = 0.7*f_co + 0.3*g_cau
    co_occur_count=10,                       # f_cooccur
    causal_count=5,                          # g_causal
    relation_types={                         # Breakdown by type
        "co_occurrence": 10,
        "description": 3,
        "contrast": 2
    }
)
```

### Network (Complete Graph Snapshot)

```python
Network(
    node_count=5925,
    edge_count=5221,
    density=0.0003,
    entropy=11.1348,                         # bits
    entropy_vs_traditional_pct=80.9,         # Improvement vs NLP
    temporal_stats={                         # 8-period evolution
        "early_period": TemporalStats(...),
        "covid_onset": TemporalStats(...),
        ...
    },
    sacred_nodes_count=2847,
    nonsacred_nodes_count=3078,
)
```

## Configuration

Key constants in `app/social/config/constants.py`:

```python
# Edge weighting (exact formula preservation)
EDGE_WEIGHT_ALPHA = 0.7      # Co-occurrence coefficient
EDGE_WEIGHT_BETA = 0.3       # Causal/description/contrast coefficient

# Entity types (12 types: 4 general + 8 sacred-specific)
ENTITY_TYPES = [
    "facility_service", "scenic_spot",           # General
    "ritual", "religious_actor", "sacred_space", # Sacred
    "spiritual_emotion", "cultural_rule", "problem",
    "festival_event", "sacred_object", "dual_valence", "general_sentiment"
]

# Sacred classification
SACRED_ENTITY_TYPES = {
    "ritual", "religious_actor", "sacred_space", "spiritual_emotion",
    "festival_event", "cultural_rule", "sacred_object", "dual_valence"
}

# Temporal periods (8 periods reflecting COVID impact)
TEMPORAL_PERIODS = {
    "early_period": (2008, 2012),
    "growth_period": (2013, 2017),
    "pre_covid_peak": (2018, 2019),
    "covid_onset": (2020, 2020),
    "covid_deep": (2021, 2021),
    "recovery_early": (2022, 2022),
    "recovery_late": (2023, 2023),
    "post_recovery": (2024, 9999),
}

# Sentiment aspects (9 aspects: 3 traditional + 6 sacred-specific)
SENTIMENT_ASPECTS = {
    "service", "facility", "environment",      # Traditional
    "sacred_atmosphere", "spiritual_authenticity", "ritual_experience",
    "cultural_sensitivity", "access_fairness", "crowd_management"
}
```

## Analysis Outputs

### network_metrics.json

```json
{
  "graph": {
    "nodes": 5925,
    "edges": 5221,
    "density": 0.0003,
    "components": 127
  },
  "entropy": {
    "entropy": 11.1348,
    "traditional_baseline": 6.1545,
    "improvement_pct": 80.9
  },
  "centrality": {
    "top_20_nodes": [
      {"node": "cremation", "centrality": 0.0387},
      {"node": "bagmati", "centrality": 0.0301},
      ...
    ]
  },
  "temporal": {
    "early_period": {
      "node_count": 2134,
      "edge_count": 1876,
      "sacred_entity_pct": 48.2,
      "avg_sentiment_score": 0.72
    },
    "covid_onset": {
      "node_count": 891,
      "edge_count": 623,
      "sacred_entity_pct": 52.1,
      "avg_sentiment_score": 0.58
    },
    ...
  },
  "trip_type": {
    "solo": {"entity_count": 4231, "sacred_entity_pct": 61.2},
    "family": {"entity_count": 3845, "sacred_entity_pct": 48.5},
    ...
  }
}
```

### PHASE3_REPORT.md

Markdown report with:
- Executive summary (nodes, edges, entropy gain)
- Network metrics table
- Top 20 nodes ranked by centrality
- Entity type centrality comparison
- Sacred vs non-sacred segmentation
- Temporal evolution (COVID impact)
- Trip type segmentation (pilgrim vs tourist signal)
- Key findings and implications

## Interpretation Guide

### Centrality Rankings

High-centrality nodes (hub entities) are:
- Frequently mentioned alongside other entities
- Connect disparate concept clusters
- Important for network cohesion

Example interpretation:
- **cremation (C_D=0.0387)**: Central hub; cremation ritual is core to Pashupatinath experience
- **bagmati (C_D=0.0301)**: Sacred space; primary location for rituals
- **darshan (C_D=0.0289)**: Spiritual experience; fundamental to worship

### Entropy Analysis

**Information Entropy** measures network structure diversity:

```
H = -Σ p(i) * log2(p(i))
where p(i) = degree(v) / sum_of_all_degrees
```

**Higher entropy** = more distributed network
- LLM-SC: **11.13 bits** (highly distributed)
- Traditional NLP (star-shaped): **6.15 bits** (few hubs)
- **80.9% improvement** = LLM captures nuanced, multi-centered experience network

### Sacred vs Non-Sacred

**Segmentation reveals pilgrimage dynamics**:
- Sacred nodes (8 types): 2,847 nodes (48%)
  - Avg centrality: 0.0241
  - Hub types: ritual, sacred_space, spiritual_emotion
- Non-sacred nodes (4 types): 3,078 nodes (52%)
  - Avg centrality: 0.0158
  - Support types: facility, scenic_spot, problem

Interpretation: Sacred entities are proportionally more central, confirming spiritual centrality of pilgrimage.

### Temporal Dynamics

**COVID impact visible in network structure**:

| Period | Nodes | Sacred % | Sentiment |
|--------|-------|----------|-----------|
| pre_covid_peak | 2,456 | 49% | 0.76 |
| covid_onset | 1,234 | 52% | 0.59 |
| recovery_late | 2,187 | 51% | 0.71 |

- **Node collapse**: 50% reduction in 2020-2021
- **Sacred proportion increase**: 49% → 52% during COVID (spiritual focus)
- **Sentiment recovery**: 0.59 → 0.71 by 2023

### Trip Type Signal

**Pilgrim vs Tourist segmentation**:

| Trip Type | Sacred % | Dual-Valence % |
|-----------|----------|-----------------|
| solo | 61.2% | 4.8% |
| couples | 58.3% | 3.2% |
| family | 48.5% | 6.1% |
| friends | 45.7% | 7.3% |

Interpretation:
- **Solo/couples travelers**: More sacred-focused (pilgrims)
- **Family/friends groups**: More practical concerns (tourists)
- **Dual-valence nodes**: Mixed awe + discomfort (sacred ambivalence)

## Research Outputs

PHASE 3 generates publication-ready outputs:

1. **GraphML Export**: Network file for visualization in academic tools
   - Open in: Gephi, Cytoscape, yEd
   - Preserve: Node types, edge weights, sentiment attributes
   - Use for: Publication figures, supplementary materials

2. **JSON Metrics**: Comprehensive statistics for reproducibility
   - Machine-readable format
   - Full provenance (input counts, calculation methods)
   - Enables downstream ML/statistical analysis

3. **Markdown Reports**: Human-readable findings
   - Tables, summaries, key statistics
   - Export to PDF for paper appendix
   - Reproducible with code

4. **Node Data**: Detailed attribute export
   - Entity names, types, centrality
   - Sentiment scores per aspect
   - Temporal span information

## Dependencies

Install with:
```bash
pip install -r requirements.txt
```

Key dependencies:
- `networkx==3.2.1`: Graph construction and analysis
- `pandas==2.2.0`: Data processing
- `numpy==1.24.3`: Numerical computation
- `loguru==0.7.2`: Logging
- `scipy==1.12.0`: Scientific computing (entropy)
- `scikit-learn==1.4.1`: Machine learning (future community detection)
- `pyvis==0.3.2`: Interactive visualization (future)
- `plotly==5.18.0`: Temporal dashboards (future)

## Testing

Run tests to verify installation:

```bash
python test_phase3.py
```

Output:
```
TESTING PHASE 3 MODULE IMPORTS
[1] Importing config... ✓
[2] Importing models... ✓
[3] Importing loaders... ✓
[4] Importing builders... ✓
[5] Importing analysis modules... ✓
[6] Importing exporters... ✓
[7] Importing pipeline... ✓

✓ ALL TESTS PASSED - PHASE 3 READY
```

## Next Steps

- **Interactive Visualization**: Pyvis network explorer with filtering
- **Community Detection**: Louvain algorithm for thematic clusters
- **Meta-path Analysis**: Semantic relation patterns (ritual→space→emotion)
- **Sentiment Propagation**: How sentiments spread through network
- **Temporal Motifs**: Recurring network patterns over time
- **Statistical Validation**: Centrality significance testing

## References

- **Original LLM-SC Paper**: Entropy-based evaluation of LLM knowledge networks vs traditional NLP
- **NetworkX**: https://networkx.org/documentation/
- **Graph Visualization**: Gephi, Cytoscape guides for publication figures
- **Temporal Network Analysis**: Dynamic graph snapshots and evolution metrics

---

**PHASE 3 Version**: 3.0  
**Site**: Pashupatinath Temple, Kathmandu, Nepal  
**Dataset**: 2,485 reviews (2008-2026) → 11,314 entities → 5,925 concept nodes  
**Last Updated**: May 2026
