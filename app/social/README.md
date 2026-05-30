# Social Network Analysis Architecture

This package builds and analyzes the Pashupatinath Heritage Experience Network.

## Pipeline

`Phase3Pipeline` runs five explicit stages:

1. `DataPreparationStage` loads cleaned entity, relation, sentiment, and optional review tables.
2. `NetworkConstructionStage` builds the weighted heterogeneous graph.
3. `CoreAnalysisStage` runs centrality, entropy, temporal, and sacred/secular analyses.
4. `AdvancedAnalysisStage` runs community detection, meta-paths, sentiment flow, and motifs.
5. `ReportingStage` exports GraphML, JSON metrics, node data, Markdown, and PyVis HTML.

The public entry point remains:

```python
from app.social.pipeline import Phase3Pipeline
```

## Extension Pattern

Add new analysis modules under `app/social/analysis/`.

Each analyzer should:

- expose a class with `name`
- accept `NetworkContext`
- return a typed dataclass from `app/social/models/results.py`
- avoid direct file writes
- use `GraphAttributeService` when adding node attributes

Example:

```python
class MyAnalyzer:
    name = "my_analysis"

    def analyze(self, context: NetworkContext) -> MyResult:
        ...
```

Wire it into `AdvancedAnalysisStage` or `CoreAnalysisStage`, then add exporter fields in `JSONExporter` and report text in `ReportExporter`.

## Artifacts

Pipeline output is written to `app/storage/social_network_output/`:

- `network.graphml`
- `network_metrics.json`
- `node_data.json`
- `PHASE3_REPORT.md`
- `graph_explorer.html`

The dashboard reads these artifacts rather than recomputing the pipeline on page load.

Run it with:

```bash
PIPELINE_MODE=dashboard .venv/bin/python -m app.main
```

