# app/social/analysis/entropy.py

"""
Information Entropy Analysis for PHASE 3b

Computes Shannon entropy: H = -Σ p(i) * log2(p(i))
where p(i) = degree of node i / sum of all degrees

Compares LLM-SC network entropy vs traditional NLP baseline.
"""

from typing import Dict
import numpy as np
import networkx as nx
from loguru import logger

from app.social.config.constants import TRADITIONAL_NLP_ENTROPY_BASELINE


class EntropyAnalyzer:
    """Computes information entropy of HIN"""
    
    def __init__(self, G: nx.Graph):
        """Initialize with graph"""
        self.G = G
    
    def compute_entropy(self) -> Dict[str, float]:
        """
        Compute Shannon entropy of degree distribution.
        
        H = -Σ p(i) * log2(p(i))
        
        where p(i) = deg(v) / Σ deg(v)
        
        Returns:
            Dictionary with entropy metrics
        """
        logger.info("Computing network entropy...")
        
        # Get degree distribution
        degrees = dict(self.G.degree())
        total_degree = sum(degrees.values())
        
        if total_degree == 0:
            logger.warning("Graph has no edges, entropy undefined")
            return {
                "entropy": 0.0,
                "entropy_bits": 0.0,
                "traditional_baseline": TRADITIONAL_NLP_ENTROPY_BASELINE,
                "improvement_pct": 0.0,
            }
        
        # Compute entropy
        entropy = 0.0
        for degree in degrees.values():
            if degree > 0:
                p = degree / total_degree
                entropy -= p * np.log2(p)
        
        # Improvement vs traditional NLP (star-shaped network)
        improvement_pct = (entropy / TRADITIONAL_NLP_ENTROPY_BASELINE - 1) * 100
        
        logger.debug(f"  Entropy: {entropy:.4f} bits")
        logger.debug(f"  Traditional baseline: {TRADITIONAL_NLP_ENTROPY_BASELINE:.4f} bits")
        logger.debug(f"  Improvement: {improvement_pct:.1f}%")
        
        return {
            "entropy": entropy,
            "entropy_bits": entropy,
            "traditional_baseline": TRADITIONAL_NLP_ENTROPY_BASELINE,
            "improvement_pct": improvement_pct,
        }
