import networkx as nx
import pandas as pd

from app.social.analysis.communities import CommunityAnalyzer
from app.social.analysis.metapaths import MetaPathAnalyzer
from app.social.analysis.motifs import MotifAnalyzer
from app.social.analysis.sentiment_flow import SentimentFlowAnalyzer
from app.social.models.results import NetworkContext, SocialDataBundle


def _context(tmp_path):
    G = nx.Graph()
    G.add_node("ritual", entity_type="ritual", sentiment_overall=0.8)
    G.add_node("temple", entity_type="sacred_space", sentiment_overall=0.7)
    G.add_node("awe", entity_type="spiritual_emotion", sentiment_overall=0.9)
    G.add_node("crowd", entity_type="problem", sentiment_overall=0.2)
    G.add_edge("ritual", "temple", weight=2.0)
    G.add_edge("temple", "awe", weight=2.0)
    G.add_edge("temple", "crowd", weight=1.0)

    entities = pd.DataFrame(
        [
            {"review_id": "r1", "year": 2019, "trip_type": "solo", "entity_name": "ritual", "entity_type": "ritual"},
            {"review_id": "r1", "year": 2019, "trip_type": "solo", "entity_name": "temple", "entity_type": "sacred_space"},
            {"review_id": "r1", "year": 2019, "trip_type": "solo", "entity_name": "awe", "entity_type": "spiritual_emotion"},
            {"review_id": "r2", "year": 2023, "trip_type": "family", "entity_name": "crowd", "entity_type": "problem"},
            {"review_id": "r2", "year": 2023, "trip_type": "family", "entity_name": "temple", "entity_type": "sacred_space"},
        ]
    )
    sentiments = pd.DataFrame(
        [
            {"review_id": "r1", "score": 0.8},
            {"review_id": "r2", "score": 0.3},
        ]
    )
    return NetworkContext(
        graph=G,
        data=SocialDataBundle(entities=entities, relations=pd.DataFrame(), sentiments=sentiments),
        output_dir=tmp_path,
    )


def test_community_analyzer_assigns_communities(tmp_path):
    result = CommunityAnalyzer().analyze(_context(tmp_path))

    assert result.assignments
    assert all(isinstance(value, int) for value in result.assignments.values())
    assert result.communities


def test_metapath_analyzer_counts_research_paths(tmp_path):
    result = MetaPathAnalyzer().analyze(_context(tmp_path))
    path = next(metric for metric in result.paths if metric.path == "ritual -> sacred_space -> spiritual_emotion")

    assert path.frequency >= 1
    assert path.group_frequencies["pilgrim"] >= 1


def test_sentiment_flow_returns_emotional_anchors(tmp_path):
    result = SentimentFlowAnalyzer().analyze(_context(tmp_path))

    assert 0 <= result.homophily_score <= 1
    assert result.emotional_anchors


def test_motif_analyzer_tracks_period_motifs(tmp_path):
    result = MotifAnalyzer(max_nodes_per_period=50).analyze(_context(tmp_path))

    assert isinstance(result.motifs, list)

