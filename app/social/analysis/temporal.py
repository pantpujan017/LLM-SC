# app/social/analysis/temporal.py

"""
Temporal Analysis for PHASE 3b

Builds period-specific network snapshots and tracks evolution.
Analyzes COVID-driven network dynamics and recovery trajectory.
"""

from typing import Dict, List, Tuple
import pandas as pd
import networkx as nx
from loguru import logger

from app.social.config.constants import TEMPORAL_PERIODS, SACRED_ENTITY_TYPES


class TemporalAnalyzer:
    """Analyzes network evolution across temporal periods"""
    
    def __init__(self, G: nx.Graph, entities_df: pd.DataFrame, sentiments_df: pd.DataFrame):
        """
        Initialize with graph and data
        
        Args:
            G: Full network
            entities_df: Entities dataframe with year/period columns
            sentiments_df: Sentiments dataframe
        """
        self.G = G
        self.entities_df = entities_df
        self.sentiments_df = sentiments_df
    
    def analyze(self) -> Dict[str, Dict]:
        """
        Analyze network snapshots per period.
        
        Returns:
            Dictionary mapping period → {nodes, edges, density, sacred%, sentiment_avg}
        """
        logger.info("Computing temporal network snapshots...")
        
        period_results = {}
        
        for period_name, (year_start, year_end) in TEMPORAL_PERIODS.items():
            logger.debug(f"  Processing {period_name} ({year_start}-{year_end})")
            
            # Filter entities by period
            period_entities = self.entities_df[
                (self.entities_df["year"] >= year_start) &
                (self.entities_df["year"] <= year_end)
            ]
            
            if len(period_entities) == 0:
                continue
            
            # Build period-specific graph
            period_reviews = period_entities["review_id"].unique()
            
            # Nodes: entities in this period
            period_nodes = set()
            for _, row in period_entities.iterrows():
                name = str(row["entity_name"]).lower().strip()
                if name in self.G:
                    period_nodes.add(name)
            
            # Build subgraph
            Gp = self.G.subgraph(period_nodes).copy()
            
            # Sacred composition
            sacred_nodes = [
                n for n in Gp.nodes()
                if self.G.nodes[n]["entity_type"] in SACRED_ENTITY_TYPES
            ]
            sacred_pct = (len(sacred_nodes) / len(Gp.nodes())) * 100 if len(Gp.nodes()) > 0 else 0
            
            # Sentiment aggregation
            period_sentiments = self.sentiments_df[
                self.sentiments_df["review_id"].isin(period_reviews)
            ]
            avg_sentiment = period_sentiments["score"].mean() if len(period_sentiments) > 0 else 0.0
            
            # Dual-valence count
            dual_count = len(
                period_entities[period_entities["entity_type"] == "dual_valence"]
            )
            
            # Spiritual emotion count
            spiritual_count = len(
                period_entities[period_entities["entity_type"] == "spiritual_emotion"]
            )
            
            period_results[period_name] = {
                "year_range": (year_start, year_end),
                "review_count": len(period_reviews),
                "node_count": len(Gp.nodes()),
                "edge_count": len(Gp.edges()),
                "density": nx.density(Gp),
                "sacred_entity_count": len(sacred_nodes),
                "sacred_entity_pct": sacred_pct,
                "dual_valence_count": dual_count,
                "spiritual_emotion_count": spiritual_count,
                "avg_sentiment_score": float(avg_sentiment),
            }
        
        return period_results
