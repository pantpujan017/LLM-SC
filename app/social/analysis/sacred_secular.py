# app/social/analysis/sacred_secular.py

"""
Sacred vs Non-Sacred Network Analysis for PHASE 3b

Segments network by sacred entity types and compares centrality patterns.
Analyzes trip-type composition (pilgrim vs tourist signal).
"""

from typing import Dict, List, Any
import pandas as pd
import networkx as nx
import numpy as np
from loguru import logger

from app.social.config.constants import SACRED_ENTITY_TYPES, TRIP_TYPE_PROFILES


class SacredSecularAnalyzer:
    """Analyzes sacred vs non-sacred network structure"""
    
    def __init__(
        self,
        G: nx.Graph,
        entities_df: pd.DataFrame,
        centrality_dict: Dict[str, float],
        sentiments_df: pd.DataFrame | None = None,
    ):
        """
        Initialize analyzer
        
        Args:
            G: Network graph
            entities_df: Entities dataframe
            centrality_dict: Node → centrality score mapping
        """
        self.G = G
        self.entities_df = entities_df
        self.centrality_dict = centrality_dict
        self.sentiments_df = sentiments_df
    
    def analyze(self) -> Dict[str, Dict]:
        """
        Analyze sacred vs non-sacred network structure.
        
        Returns:
            Dictionary with segmentation results
        """
        logger.info("Analyzing sacred vs non-sacred network...")
        
        # Classify nodes
        sacred_nodes = [
            n for n in self.G.nodes()
            if self.G.nodes[n]["entity_type"] in SACRED_ENTITY_TYPES
        ]
        nonsacred_nodes = [
            n for n in self.G.nodes()
            if self.G.nodes[n]["entity_type"] not in SACRED_ENTITY_TYPES
        ]
        
        # Centrality statistics
        sacred_centralities = [self.centrality_dict[n] for n in sacred_nodes]
        nonsacred_centralities = [self.centrality_dict[n] for n in nonsacred_nodes]
        
        results = {
            "sacred": {
                "count": len(sacred_nodes),
                "avg_centrality": float(np.mean(sacred_centralities)) if sacred_centralities else 0.0,
                "max_centrality": float(np.max(sacred_centralities)) if sacred_centralities else 0.0,
                "top_nodes": sorted(
                    [(n, self.centrality_dict[n]) for n in sacred_nodes],
                    key=lambda x: -x[1]
                )[:10],
            },
            "nonsacred": {
                "count": len(nonsacred_nodes),
                "avg_centrality": float(np.mean(nonsacred_centralities)) if nonsacred_centralities else 0.0,
                "max_centrality": float(np.max(nonsacred_centralities)) if nonsacred_centralities else 0.0,
                "top_nodes": sorted(
                    [(n, self.centrality_dict[n]) for n in nonsacred_nodes],
                    key=lambda x: -x[1]
                )[:10],
            },
        }
        
        logger.debug(f"  Sacred nodes: {results['sacred']['count']} | avg centrality: {results['sacred']['avg_centrality']:.4f}")
        logger.debug(f"  Non-sacred nodes: {results['nonsacred']['count']} | avg centrality: {results['nonsacred']['avg_centrality']:.4f}")
        
        return results
    
    def analyze_trip_types(self) -> Dict[str, Dict]:
        """
        Analyze network composition by trip type.
        
        Detects pilgrim vs tourist signal through entity type distribution.
        
        Returns:
            Dictionary mapping trip_type → {sacred%, sentiment_avg, entity_counts}
        """
        logger.info("Analyzing trip type segmentation...")
        
        trip_type_results = {}
        
        for trip_type in self.entities_df["trip_type"].unique():
            if pd.isna(trip_type):
                continue
            
            trip_type = str(trip_type).strip()
            
            # Entities in this trip type
            tt_entities = self.entities_df[self.entities_df["trip_type"] == trip_type]
            
            # Sacred composition
            sacred_count = len(
                tt_entities[tt_entities["entity_type"].isin(SACRED_ENTITY_TYPES)]
            )
            total_count = len(tt_entities)
            sacred_pct = (sacred_count / total_count * 100) if total_count > 0 else 0
            
            # Dual-valence proportion
            dual_count = len(tt_entities[tt_entities["entity_type"] == "dual_valence"])
            dual_pct = (dual_count / total_count * 100) if total_count > 0 else 0
            
            # Spiritual emotion proportion
            spiritual_count = len(tt_entities[tt_entities["entity_type"] == "spiritual_emotion"])
            spiritual_pct = (spiritual_count / total_count * 100) if total_count > 0 else 0

            avg_sentiment = 0.0
            if self.sentiments_df is not None and "trip_type" in self.sentiments_df.columns:
                tt_sentiments = self.sentiments_df[self.sentiments_df["trip_type"] == trip_type]
                avg_sentiment = float(tt_sentiments["score"].mean()) if len(tt_sentiments) else 0.0
            
            trip_type_results[trip_type] = {
                "entity_count": total_count,
                "sacred_entity_pct": sacred_pct,
                "dual_valence_pct": dual_pct,
                "spiritual_emotion_pct": spiritual_pct,
                "review_count": len(tt_entities["review_id"].unique()),
                "avg_sentiment_score": avg_sentiment,
                "profile": TRIP_TYPE_PROFILES.get(trip_type.lower(), "Visitor segment"),
            }
        
        return trip_type_results
