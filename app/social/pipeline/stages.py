"""Staged execution units for the social network pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import networkx as nx
from loguru import logger

from app.social.analysis import AspectSentimentAnalyzer, CentralityAnalyzer, EntropyAnalyzer, SacredSecularAnalyzer, TemporalAnalyzer
from app.social.analysis.communities import CommunityAnalyzer
from app.social.analysis.metapaths import MetaPathAnalyzer
from app.social.analysis.motifs import MotifAnalyzer
from app.social.analysis.sentiment_flow import SentimentFlowAnalyzer
from app.social.exporters import GraphMLExporter, JSONExporter, PyVisExporter, ReportExporter
from app.social.graph import GraphAttributeService, GraphBuilder
from app.social.models.results import (
    AdvancedAnalysisResults,
    CentralityResult,
    CoreAnalysisResults,
    NetworkContext,
    PipelineResult,
    SocialDataBundle,
)
from app.social.services.data_service import SocialDataService


class DataPreparationStage:
    """Load Phase 2.5 tables and optional review analytics data."""

    def __init__(self, data_dir: Path | str, reviews_path: Optional[Path | str] = None):
        self.data_dir = Path(data_dir)
        self.reviews_path = Path(reviews_path) if reviews_path else None

    def run(self) -> SocialDataBundle:
        logger.info("[Phase 1] Data Preparation")
        return SocialDataService(self.data_dir, self.reviews_path).load()


class NetworkConstructionStage:
    """Construct the weighted HIN."""

    def run(self, data: SocialDataBundle, output_dir: Path) -> NetworkContext:
        logger.info("[Phase 2] Network Construction")
        graph = GraphBuilder(data=data).build()
        return NetworkContext(graph=graph, data=data, output_dir=output_dir)


class CoreAnalysisStage:
    """Run existing core network analyses."""

    def run(self, context: NetworkContext) -> CoreAnalysisResults:
        logger.info("[Phase 3] Core Network Analysis")
        centrality_analyzer = CentralityAnalyzer(context.graph)
        centrality_raw = centrality_analyzer.analyze()
        type_centrality = centrality_analyzer.get_type_level_centrality()
        centrality = CentralityResult(
            degree_centrality=centrality_raw["degree_centrality"],
            strength=centrality_raw["strength"],
            top_nodes=centrality_raw["top_nodes"],
            type_centrality=type_centrality,
        )
        GraphAttributeService.assign_node_attributes(
            context.graph,
            {
                node: {
                    "degree": int(context.graph.degree(node)),
                    "weighted_degree": centrality.strength.get(node, 0.0),
                    "degree_centrality": centrality.degree_centrality.get(node, 0.0),
                }
                for node in context.graph.nodes()
            },
        )

        entropy = EntropyAnalyzer(context.graph).compute_entropy()
        temporal = TemporalAnalyzer(
            context.graph,
            context.data.entities,
            context.data.sentiments,
        ).analyze()
        sacred_analyzer = SacredSecularAnalyzer(
            context.graph,
            context.data.entities,
            centrality.degree_centrality,
            context.data.sentiments,
        )
        sacred = sacred_analyzer.analyze()
        trip_type = sacred_analyzer.analyze_trip_types()
        aspect_sentiment = AspectSentimentAnalyzer(context.data.sentiments).analyze()
        return CoreAnalysisResults(
            centrality=centrality,
            entropy=entropy,
            temporal=temporal,
            sacred=sacred,
            trip_type=trip_type,
            aspect_sentiment=aspect_sentiment,
        )


class AdvancedAnalysisStage:
    """Run the advanced network analysis layer."""

    def run(self, context: NetworkContext) -> AdvancedAnalysisResults:
        logger.info("[Phase 4] Advanced Analysis")
        communities = CommunityAnalyzer().analyze(context)
        metapaths = MetaPathAnalyzer().analyze(context)
        sentiment_flow = SentimentFlowAnalyzer().analyze(context)
        motifs = MotifAnalyzer().analyze(context)
        return AdvancedAnalysisResults(
            communities=communities,
            metapaths=metapaths,
            sentiment_flow=sentiment_flow,
            motifs=motifs,
        )


class ReportingStage:
    """Export graph, metrics, node data, and report outputs."""

    def run(self, result: PipelineResult) -> Dict[str, str]:
        logger.info("[Phase 5] Reporting")
        context = result.context
        output_dir = context.output_dir
        graphml_path = GraphMLExporter(context.graph, output_dir).export()
        json_exporter = JSONExporter(output_dir)
        metrics_path = json_exporter.export_metrics(context.graph, result.core, result.advanced)
        node_data_path = json_exporter.export_node_data(context.graph, result.core, result.advanced)
        report_path = ReportExporter(output_dir).export_full_report(
            context.graph,
            result.core,
            result.advanced,
        )
        graph_explorer_path = PyVisExporter(output_dir).export(context.graph)
        return {
            "graphml": str(graphml_path),
            "json_metrics": str(metrics_path),
            "node_data": str(node_data_path),
            "report": str(report_path),
            "graph_explorer": str(graph_explorer_path),
        }
