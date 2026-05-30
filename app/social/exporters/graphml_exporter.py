# app/social/exporters/graphml_exporter.py

"""
GraphML Exporter for PHASE 3c

Exports NetworkX graph to GraphML format for Gephi/Cytoscape visualization.
"""

import json
from pathlib import Path
import networkx as nx
from loguru import logger


class GraphMLExporter:
    """Exports HIN to GraphML format"""
    
    def __init__(self, G: nx.Graph, output_dir: Path | str):
        """
        Initialize exporter
        
        Args:
            G: NetworkX graph
            output_dir: Output directory
        """
        self.G = G
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, filename: str = "network.graphml") -> Path:
        """
        Export graph to GraphML format.
        
        GraphML opens in Gephi, Cytoscape, yEd, etc.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        logger.info("Exporting graph to GraphML format...")
        
        output_path = self.output_dir / filename
        
        try:
            # Create a copy of the graph for export to avoid modifying original
            export_G = self.G.copy()
            
            # Flatten all dictionary attributes to JSON strings
            # Node attributes
            for n, attrs in export_G.nodes(data=True):
                for key, value in attrs.items():
                    if isinstance(value, dict):
                        export_G.nodes[n][key] = json.dumps(value)
            
            # Edge attributes
            for u, v, attrs in export_G.edges(data=True):
                for key, value in attrs.items():
                    if isinstance(value, dict):
                        export_G.edges[u, v][key] = json.dumps(value)
            
            nx.write_graphml(export_G, str(output_path))
            logger.success(f"✓ GraphML exported: {output_path}")
            logger.info(f"  Open in: Gephi, Cytoscape, yEd, or NetworkX")
            return output_path
        except Exception as e:
            logger.error(f"Failed to export GraphML: {e}")
            raise
