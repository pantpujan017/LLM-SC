# app/social/analysis/centrality.py

"""
Centrality Analysis for PHASE 3b

Computes degree centrality C_D(v) = deg(v) / (n-1) and related metrics.
"""

from typing import Dict, List, Tuple
import networkx as nx
import numpy as np
from loguru import logger

from app.social.config.constants import TOP_N_NODES


class CentralityAnalyzer:
    """Computes centrality metrics for HIN nodes"""
    
    def __init__(self, G: nx.Graph):
        """Initialize with graph"""
        self.G = G
        self.degree_centrality: Dict[str, float] = {}
        self.strength: Dict[str, float] = {}  # Weighted degree
    
    def analyze(self) -> Dict[str, Dict]:
        """
        Compute centrality metrics.
        
        Returns:
            Dictionary with results
        """
        logger.info("Computing centrality metrics...")
        
        # Degree centrality: C_D(v) = deg(v) / (n-1)
        self.degree_centrality = nx.degree_centrality(self.G)
        
        # Weighted degree (strength): Σ w_ij for all edges incident to v
        self.strength = {}
        for node in self.G.nodes():
            self.strength[node] = sum(
                d["weight"] for _, _, d in self.G.edges(node, data=True)
            )
        
        # Top nodes
        top_by_degree = self._get_top_nodes(self.degree_centrality, TOP_N_NODES)
        
        logger.debug(f"  Top node: {top_by_degree[0][0]} (centrality: {top_by_degree[0][1]:.4f})")
        
        return {
            "degree_centrality": self.degree_centrality,
            "strength": self.strength,
            "top_nodes": top_by_degree,
        }
    
    def _get_top_nodes(
        self, centrality_dict: Dict[str, float], top_n: int
    ) -> List[Tuple[str, float]]:
        """Get top N nodes by centrality"""
        return sorted(centrality_dict.items(), key=lambda x: -x[1])[:top_n]
    
    def get_type_level_centrality(self) -> Dict[str, Dict[str, float]]:
        """
        Aggregate centrality by entity type.
        
        Returns:
            Dict mapping entity_type → {avg, max, count}
        """
        logger.info("Computing type-level centrality...")
        
        type_centrality: Dict[str, Dict[str, float | int]] = {}
        
        for node in self.G.nodes():
            etype = self.G.nodes[node]["entity_type"]
            
            if etype not in type_centrality:
                type_centrality[etype] = {
                    "nodes": [],
                    "degrees": [],
                    "strengths": [],
                }
            
            type_centrality[etype]["nodes"].append(node)
            type_centrality[etype]["degrees"].append(self.degree_centrality[node])
            type_centrality[etype]["strengths"].append(self.strength[node])
        
        # Aggregate
        result = {}
        for etype, data in type_centrality.items():
            degrees = data["degrees"]
            strengths = data["strengths"]
            
            result[etype] = {
                "count": len(data["nodes"]),
                "avg_degree_centrality": float(np.mean(degrees)),
                "max_degree_centrality": float(np.max(degrees)),
                "avg_weighted_degree": float(np.mean(strengths)),
                "max_weighted_degree": float(np.max(strengths)),
            }
        
        return result
