"""Interactive PyVis graph explorer exporter."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
from loguru import logger

from app.social.visualization import NetworkVizBuilder


class PyVisExporter:
    """Export an Obsidian-style interactive network explorer."""

    def __init__(self, output_dir: Path | str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        G: nx.Graph,
        filename: str = "graph_explorer.html",
        max_nodes: int = 900,
        edge_threshold: float = 0.5,
    ) -> Path:
        logger.info("Exporting PyVis graph explorer...")
        output_path = self.output_dir / filename
        NetworkVizBuilder(edge_threshold=edge_threshold, max_nodes=max_nodes).export_html(G, output_path)
        logger.success(f"Graph explorer exported: {output_path}")
        return output_path

