"""Main social network pipeline executor."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

from app.social.models.results import PipelineResult
from app.social.pipeline.stages import (
    AdvancedAnalysisStage,
    CoreAnalysisStage,
    DataPreparationStage,
    NetworkConstructionStage,
    ReportingStage,
)
from app.social.utils.serialization import to_jsonable


class Phase3Pipeline:
    """Five-stage Heritage Experience Network pipeline."""

    def __init__(
        self,
        data_dir: Path | str,
        output_dir: Path | str,
        reviews_path: Optional[Path | str] = "app/storage/processed/pashupatinath_reviews_clean.csv",
    ):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reviews_path = Path(reviews_path) if reviews_path else None
        self.pipeline_result: PipelineResult | None = None

    def execute(self) -> Dict[str, Any]:
        logger.info("=" * 70)
        logger.info("HERITAGE EXPERIENCE NETWORK PIPELINE")
        logger.info("=" * 70)
        try:
            data = DataPreparationStage(self.data_dir, self.reviews_path).run()
            context = NetworkConstructionStage().run(data, self.output_dir)
            core = CoreAnalysisStage().run(context)
            advanced = AdvancedAnalysisStage().run(context)
            result = PipelineResult(context=context, core=core, advanced=advanced)
            result.exports = ReportingStage().run(result)
            self.pipeline_result = result
            logger.success("Heritage Experience Network pipeline complete")
            return self._summary(result)
        except Exception as exc:
            logger.error(f"Social network pipeline failed: {exc}", exc_info=True)
            raise

    def _summary(self, result: PipelineResult) -> Dict[str, Any]:
        G = result.context.graph
        return to_jsonable(
            {
                "phase_1_data_preparation": {
                    "entities": len(result.context.data.entities),
                    "relations": len(result.context.data.relations),
                    "sentiments": len(result.context.data.sentiments),
                    "reviews": 0 if result.context.data.reviews is None else len(result.context.data.reviews),
                },
                "phase_2_network_construction": {
                    "nodes": G.number_of_nodes(),
                    "edges": G.number_of_edges(),
                    "entity_types": sorted({attrs.get("entity_type", "unknown") for _, attrs in G.nodes(data=True)}),
                },
                "phase_3_core_analysis": {
                    "entropy": result.core.entropy,
                    "temporal_periods": len(result.core.temporal),
                    "top_nodes": result.core.centrality.top_nodes[:20],
                },
                "phase_4_advanced_analysis": {
                    "communities": len(result.advanced.communities.communities),
                    "modularity": result.advanced.communities.modularity,
                    "semantic_paths": len(result.advanced.metapaths.paths),
                    "motifs": len(result.advanced.motifs.motifs),
                    "sentiment_homophily": result.advanced.sentiment_flow.homophily_score,
                },
                "phase_5_reporting": result.exports,
                "exports": result.exports,
            }
        )

