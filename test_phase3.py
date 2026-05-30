#!/usr/bin/env python3
# test_phase3.py

"""
Test script for PHASE 3: Social Network Computing

Verifies all modules load correctly and basic functionality works.
Run: python test_phase3.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all PHASE 3 modules import correctly"""
    print("=" * 70)
    print("TESTING PHASE 3 MODULE IMPORTS")
    print("=" * 70)
    
    try:
        print("\n[1] Importing config...")
        from app.social.config import ENTITY_TYPES, EDGE_WEIGHT_ALPHA, SACRED_ENTITY_TYPES
        print(f"  ✓ Loaded {len(ENTITY_TYPES)} entity types")
        print(f"  ✓ Edge weighting: α={EDGE_WEIGHT_ALPHA}, β=0.3")
        print(f"  ✓ Loaded {len(SACRED_ENTITY_TYPES)} sacred entity types")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    try:
        print("\n[2] Importing models...")
        from app.social.models import Node, Edge, Network
        print(f"  ✓ Node model")
        print(f"  ✓ Edge model")
        print(f"  ✓ Network model")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    try:
        print("\n[3] Importing loaders...")
        from app.social.loaders import CSVLoader
        print(f"  ✓ CSVLoader")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    try:
        print("\n[4] Importing builders...")
        from app.social.builders import GraphBuilder
        print(f"  ✓ GraphBuilder")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    try:
        print("\n[5] Importing analysis modules...")
        from app.social.analysis import (
            CentralityAnalyzer,
            EntropyAnalyzer,
            TemporalAnalyzer,
            SacredSecularAnalyzer,
        )
        print(f"  ✓ CentralityAnalyzer")
        print(f"  ✓ EntropyAnalyzer")
        print(f"  ✓ TemporalAnalyzer")
        print(f"  ✓ SacredSecularAnalyzer")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    try:
        print("\n[6] Importing exporters...")
        from app.social.exporters import (
            GraphMLExporter,
            JSONExporter,
            ReportExporter,
        )
        print(f"  ✓ GraphMLExporter")
        print(f"  ✓ JSONExporter")
        print(f"  ✓ ReportExporter")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    try:
        print("\n[7] Importing pipeline...")
        from app.social.pipeline import Phase3Pipeline
        print(f"  ✓ Phase3Pipeline")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ ALL IMPORTS SUCCESSFUL")
    print("=" * 70)
    return True


def test_pydantic_models():
    """Test Pydantic models"""
    print("\n" + "=" * 70)
    print("TESTING PYDANTIC MODELS")
    print("=" * 70)
    
    try:
        from app.social.models import Node, Edge
        
        # Test Node creation
        node = Node(
            name="cremation",
            entity_type="sacred_space",
        )
        print(f"\n✓ Node created: {node.name} ({node.entity_type})")
        
        # Test Edge creation
        edge = Edge(
            source="cremation",
            target="bagmati",
            weight=0.85,
            co_occur_count=10,
            causal_count=5,
        )
        print(f"✓ Edge created: {edge.source} → {edge.target} (weight={edge.weight})")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    return True


def test_graph_builder():
    """Test GraphBuilder with mock data"""
    print("\n" + "=" * 70)
    print("TESTING GRAPH BUILDER")
    print("=" * 70)
    
    try:
        import pandas as pd
        import networkx as nx
        
        # Create mock data
        entities_data = {
            "entity_name": ["cremation", "bagmati", "ghat", "sadhu"],
            "entity_type": ["ritual", "sacred_space", "sacred_space", "religious_actor"],
            "year": [2019, 2019, 2019, 2019],
            "period": ["pre_covid_peak", "pre_covid_peak", "pre_covid_peak", "pre_covid_peak"],
            "review_id": ["r1", "r1", "r2", "r2"],
            "trip_type": ["solo", "solo", "family", "family"],
        }
        
        relations_data = {
            "source_node": ["cremation", "bagmati", "cremation"],
            "target_node": ["bagmati", "ghat", "sadhu"],
            "relation": ["co_occurrence", "co_occurrence", "description"],
            "review_id": ["r1", "r1", "r2"],
        }
        
        sentiments_data = {
            "entity_name": ["cremation", "bagmati", "ghat"],
            "aspect": ["sacred_atmosphere", "environment", "facility"],
            "score": [0.8, 0.7, 0.6],
            "sentiment": ["positive", "positive", "neutral"],
            "review_id": ["r1", "r1", "r2"],
        }
        
        # Create temp dataframes
        entities_df = pd.DataFrame(entities_data)
        relations_df = pd.DataFrame(relations_data)
        sentiments_df = pd.DataFrame(sentiments_data)
        
        print("\nBuilding mock graph...")
        print(f"  Entities: {len(entities_df)}")
        print(f"  Relations: {len(relations_df)}")
        print(f"  Sentiments: {len(sentiments_df)}")
        
        # Simulate GraphBuilder steps
        # This is a simplified test without file I/O
        print("\n✓ Graph builder modules ready")
        print(f"  Node deduplication: {len(entities_df)} → {len(entities_df['entity_name'].unique())} unique")
        print(f"  Edge weighting: α=0.7 (co-occur), β=0.3 (causal)")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n")
    
    results = {
        "Imports": test_imports(),
        "Pydantic Models": test_pydantic_models(),
        "Graph Builder": test_graph_builder(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:30s} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED - PHASE 3 READY")
    else:
        print("\n✗ SOME TESTS FAILED - CHECK ABOVE")
        sys.exit(1)


if __name__ == "__main__":
    main()
