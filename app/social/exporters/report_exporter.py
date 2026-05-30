"""Markdown report exporter for publication-ready network summaries."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import networkx as nx
from loguru import logger

from app.social.metrics import compute_global_graph_metrics
from app.social.models.results import AdvancedAnalysisResults, CoreAnalysisResults


class ReportExporter:
    """Generate the Phase 3 markdown research report."""

    def __init__(self, output_dir: Path | str, site_name: str = "Pashupatinath Temple"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.site_name = site_name

    def export_full_report(
        self,
        G: nx.Graph,
        core: CoreAnalysisResults,
        advanced: AdvancedAnalysisResults,
        filename: str = "PHASE3_REPORT.md",
    ) -> Path:
        logger.info("Generating markdown report...")
        lines: List[str] = []
        metrics = compute_global_graph_metrics(G, core.centrality.degree_centrality)

        lines.extend(
            [
                "# PHASE 3: Social Network Computing Report",
                f"## {self.site_name} Experience Network",
                "",
                f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## Executive Summary",
                "",
                f"- **Network Nodes (Entities)**: {G.number_of_nodes():,}",
                f"- **Network Edges (Relations)**: {G.number_of_edges():,}",
                f"- **Network Density**: {metrics['density']:.6f}",
                f"- **Connected Components**: {metrics['components']:,}",
                f"- **Information Entropy**: {core.entropy['entropy']:.4f} bits",
                f"- **Louvain Communities**: {len(advanced.communities.communities):,}",
                f"- **Modularity**: {advanced.communities.modularity:.4f}",
                f"- **Sentiment Homophily**: {advanced.sentiment_flow.homophily_score:.4f}",
                "",
            ]
        )

        self._append_network_metrics(lines, metrics, core)
        self._append_story_tables(lines, core)
        self._append_top_nodes(lines, G, core)
        self._append_temporal(lines, core)
        self._append_thematic_clusters(lines, advanced)
        self._append_semantic_trajectories(lines, advanced)
        self._append_sentiment_dynamics(lines, advanced)
        self._append_motif_evolution(lines, advanced)
        self._append_findings(lines, G, core, advanced)

        lines.extend(
            [
                "---",
                f"*PHASE 3 Report | {self.site_name} Experience Network | {datetime.now().year}*",
            ]
        )
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.success(f"Report exported: {output_path}")
        return output_path

    def _append_network_metrics(self, lines: List[str], metrics: dict, core: CoreAnalysisResults) -> None:
        lines.extend(
            [
                "## Network Metrics",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Nodes | {metrics['nodes']:,} |",
                f"| Edges | {metrics['edges']:,} |",
                f"| Density | {metrics['density']:.6f} |",
                f"| Connected Components | {metrics['components']:,} |",
                f"| Clustering Coefficient | {metrics['clustering_coefficient']:.4f} |",
                f"| Centralization | {metrics['centralization']:.4f} |",
                f"| Degree Assortativity | {metrics['degree_assortativity']:.4f} |",
                "",
                "## Information Entropy Analysis",
                "",
                f"- **LLM-SC Network Entropy**: {core.entropy['entropy']:.4f} bits",
                f"- **Traditional NLP Baseline**: {core.entropy['traditional_baseline']:.4f} bits",
                f"- **Improvement**: {core.entropy['improvement_pct']:.1f}%",
                "",
            ]
        )

    def _append_top_nodes(self, lines: List[str], G: nx.Graph, core: CoreAnalysisResults) -> None:
        lines.extend(
            [
                "## Top 20 Nodes by Degree Centrality",
                "",
                "| Rank | Node Name | Entity Type | Community | Centrality | Degree |",
                "|------|-----------|-------------|-----------|------------|--------|",
            ]
        )
        for rank, (node, score) in enumerate(core.centrality.top_nodes[:20], 1):
            attrs = G.nodes[node]
            lines.append(
                f"| {rank} | {node} | {attrs.get('entity_type', 'unknown')} | "
                f"{attrs.get('community_id', '')} | {score:.4f} | {G.degree(node)} |"
            )
        lines.append("")

    def _append_story_tables(self, lines: List[str], core: CoreAnalysisResults) -> None:
        lines.extend(
            [
                "## Aspect Sentiment Intelligence",
                "",
                "| Aspect | N | Positive % | Negative % | Avg Score | Type | Interpretation |",
                "|--------|---|------------|------------|-----------|------|----------------|",
            ]
        )
        for row in core.aspect_sentiment.values():
            lines.append(
                f"| {row['label']} | {row['count']} | {row['positive_pct']:.1f}% | "
                f"{row['negative_pct']:.1f}% | {row['avg_score']:.2f} | {row['type']} | "
                f"{row['interpretation']} |"
            )
        lines.extend(["", "## Visitor Segment Profiles", "", "| Segment | Reviews | Sacred % | Dual-Valence % | Spiritual Emotion % | Avg Sentiment | Profile |", "|---------|---------|----------|----------------|---------------------|---------------|---------|"])
        for trip_type, stats in core.trip_type.items():
            lines.append(
                f"| {trip_type.title()} | {stats.get('review_count', 0)} | "
                f"{stats.get('sacred_entity_pct', 0):.1f}% | {stats.get('dual_valence_pct', 0):.1f}% | "
                f"{stats.get('spiritual_emotion_pct', 0):.1f}% | {stats.get('avg_sentiment_score', 0):.2f} | "
                f"{stats.get('profile', '')} |"
            )
        lines.append("")

    def _append_temporal(self, lines: List[str], core: CoreAnalysisResults) -> None:
        lines.extend(
            [
                "## Temporal Network Evolution",
                "",
                "| Period | Year Range | Reviews | Nodes | Edges | Density | Sacred % | Sentiment |",
                "|--------|------------|---------|-------|-------|---------|----------|-----------|",
            ]
        )
        for period, stats in core.temporal.items():
            start, end = stats["year_range"]
            lines.append(
                f"| {period} | {start}-{end} | {stats.get('review_count', 0)} | "
                f"{stats.get('node_count', 0)} | {stats.get('edge_count', 0)} | "
                f"{stats.get('density', 0):.4f} | {stats.get('sacred_entity_pct', 0):.1f}% | "
                f"{stats.get('avg_sentiment_score', 0):.3f} |"
            )
        lines.append("")

    def _append_thematic_clusters(self, lines: List[str], advanced: AdvancedAnalysisResults) -> None:
        lines.extend(
            [
                "## Thematic Clusters",
                "",
                f"Louvain detection identified **{len(advanced.communities.communities)}** thematic communities "
                f"with modularity **{advanced.communities.modularity:.4f}**.",
                "",
                "| Community Theme | Nodes | Main Topic | Avg Sentiment | Density | Top Nodes |",
                "|-----------|-------|----------------------|---------------|---------|-----------|",
            ]
        )
        for community in advanced.communities.communities[:15]:
            top_nodes = ", ".join(row["node"] for row in community.top_nodes[:5])
            lines.append(
                f"| {community.community_name} | {community.node_count} | "
                f"{community.dominant_entity_type} | {community.average_sentiment:.3f} | "
                f"{community.density:.4f} | {top_nodes} |"
            )
        lines.append("")

    def _append_semantic_trajectories(self, lines: List[str], advanced: AdvancedAnalysisResults) -> None:
        lines.extend(
            [
                "## Semantic Trajectories",
                "",
                "| Semantic Path | Frequency | Prevalence | Significance | Pilgrim | Tourist |",
                "|---------------|-----------|------------|--------------|---------|---------|",
            ]
        )
        for metric in advanced.metapaths.paths:
            groups = metric.group_frequencies
            lines.append(
                f"| {metric.path} | {metric.frequency} | {metric.prevalence:.3f} | "
                f"{metric.significance:.3f} | {groups.get('pilgrim', 0)} | {groups.get('tourist', 0)} |"
            )
        lines.append("")

    def _append_sentiment_dynamics(self, lines: List[str], advanced: AdvancedAnalysisResults) -> None:
        flow = advanced.sentiment_flow
        lines.extend(
            [
                "## Sentiment Dynamics",
                "",
                f"- **Sentiment Assortativity**: {flow.assortativity_score:.4f}",
                f"- **Sentiment Homophily**: {flow.homophily_score:.4f}",
                f"- **Edge Sentiment Correlation**: {flow.sentiment_correlation:.4f}",
                f"- **Sentiment Clustering Coefficient**: {flow.sentiment_clustering_coefficient:.4f}",
                "",
                "| Node | Type | Role | Sentiment | Influence | Opposite Weight |",
                "|------|------|------|-----------|-----------|-----------------|",
            ]
        )
        for anchor in flow.emotional_anchors[:15]:
            lines.append(
                f"| {anchor.node} | {anchor.entity_type} | {anchor.role} | "
                f"{anchor.sentiment:.3f} | {anchor.emotional_influence_score:.3f} | "
                f"{anchor.opposite_weight:.3f} |"
            )
        lines.append("")

    def _append_motif_evolution(self, lines: List[str], advanced: AdvancedAnalysisResults) -> None:
        lines.extend(
            [
                "## Motif Evolution",
                "",
                "| Motif | Entity Composition | Frequency | Persistence | Survival Rate | COVID Resilience |",
                "|-------|--------------------|-----------|-------------|---------------|------------------|",
            ]
        )
        for motif in advanced.motifs.motifs[:25]:
            lines.append(
                f"| {motif.motif_type} | {motif.entity_composition} | {motif.frequency} | "
                f"{motif.persistence} | {motif.survival_rate:.3f} | {motif.covid_resilience} |"
            )
        lines.extend(
            [
                "",
                "### COVID Resilience",
                "",
                f"- **Survived COVID**: {', '.join(advanced.motifs.survived_covid[:8]) or 'None detected'}",
                f"- **Disappeared After COVID**: {', '.join(advanced.motifs.disappeared_after_covid[:8]) or 'None detected'}",
                f"- **Emerged After Recovery**: {', '.join(advanced.motifs.emerged_after_recovery[:8]) or 'None detected'}",
                "",
            ]
        )

    def _append_findings(self, lines: List[str], G: nx.Graph, core: CoreAnalysisResults, advanced: AdvancedAnalysisResults) -> None:
        strongest = advanced.communities.communities[0] if advanced.communities.communities else None
        top_path = advanced.metapaths.paths[0] if advanced.metapaths.paths else None
        top_motif = advanced.motifs.motifs[0] if advanced.motifs.motifs else None
        top_anchor = advanced.sentiment_flow.emotional_anchors[0] if advanced.sentiment_flow.emotional_anchors else None
        lines.extend(["## Key Findings", ""])
        lines.append(f"1. **Network Scale**: {G.number_of_nodes():,} entities connected by {G.number_of_edges():,} weighted relations")
        lines.append(f"2. **Sacred Composition**: {core.sacred['sacred']['count']} sacred nodes in the network")
        if strongest:
            lines.append(f"3. **Strongest Community**: {strongest.community_name} centered on {strongest.dominant_entity_type}")
        if top_path:
            lines.append(f"4. **Dominant Visitor Journey**: {top_path.path} ({top_path.frequency} graph instances)")
        if top_motif:
            lines.append(f"5. **Most Common Motif**: {top_motif.entity_composition} ({top_motif.frequency} instances)")
        if top_anchor:
            lines.append(f"6. **Strongest Emotional Anchor**: {top_anchor.node} ({top_anchor.role}, influence {top_anchor.emotional_influence_score:.2f})")
        lines.append("")
