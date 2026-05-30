"""Temporal graph snapshot helpers."""

from __future__ import annotations

from typing import Dict

import networkx as nx
import pandas as pd

from app.social.config.constants import TEMPORAL_PERIODS
from app.social.graph.services import TemporalGraphService


def build_period_snapshots(G: nx.Graph, entities_df: pd.DataFrame) -> Dict[str, nx.Graph]:
    """Build subgraphs for configured temporal periods."""
    service = TemporalGraphService(G, entities_df)
    return {
        period: service.period_subgraph(start, end)
        for period, (start, end) in TEMPORAL_PERIODS.items()
    }

