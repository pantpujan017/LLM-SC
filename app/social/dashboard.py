"""Streamlit dashboard for the Nepal Heritage Experience Network."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import sys

import networkx as nx
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.social.config.constants import COLOR_PALETTE
from app.social.exporters import PyVisExporter


OUTPUT_DIR = Path("app/storage/social_network_output")
REVIEWS_PATH = Path("app/storage/processed/pashupatinath_reviews_clean.csv")
GRAPHML_PATH = OUTPUT_DIR / "network.graphml"
METRICS_PATH = OUTPUT_DIR / "network_metrics.json"
NODE_DATA_PATH = OUTPUT_DIR / "node_data.json"
GRAPH_EXPLORER_PATH = OUTPUT_DIR / "graph_explorer.html"

PLAIN_TYPE_LABELS = {
    "ritual": "Rituals",
    "religious_actor": "Holy people",
    "sacred_space": "Sacred places",
    "spiritual_emotion": "Spiritual feelings",
    "cultural_rule": "Rules and respect",
    "problem": "Problems",
    "festival_event": "Festivals",
    "sacred_object": "Sacred objects",
    "dual_valence": "Mixed feelings",
    "facility_service": "Facilities",
    "scenic_spot": "Views",
    "general_sentiment": "Overall feelings",
    "unknown": "Unknown",
}

PERIOD_LABELS = {
    "early_period": "Early years",
    "growth_period": "Tourism growth",
    "pre_covid_peak": "Before COVID peak",
    "covid_onset": "COVID begins",
    "covid_deep": "Deep COVID period",
    "recovery_early": "Early recovery",
    "recovery_late": "Later recovery",
    "post_recovery": "After recovery",
}


st.set_page_config(
    page_title="Nepal Heritage Experience Network",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    _inject_css()
    metrics = _load_json(METRICS_PATH)
    node_data = _load_json(NODE_DATA_PATH)
    reviews = _load_reviews()
    graph = _load_graph()

    st.title("Nepal Heritage Experience Network")
    st.caption("A plain-language view of what visitors say about Pashupatinath Temple")

    pages = [
        "Overview",
        "Visitor Reviews",
        "Network Health",
        "Experience Themes",
        "Visitor Journeys",
        "Feelings and Emotions",
        "Repeating Patterns",
        "Interactive Story Map",
        "Research Insights",
    ]
    section = st.sidebar.radio("Section", pages, label_visibility="collapsed")
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Artifacts: `{OUTPUT_DIR}`")

    if section == "Overview":
        render_overview(metrics, node_data, reviews)
    elif section == "Visitor Reviews":
        render_review_analytics(reviews)
    elif section == "Network Health":
        render_network_analytics(metrics)
    elif section == "Experience Themes":
        render_community_explorer(metrics)
    elif section == "Visitor Journeys":
        render_semantic_paths(metrics)
    elif section == "Feelings and Emotions":
        render_sentiment_intelligence(metrics)
    elif section == "Repeating Patterns":
        render_motif_evolution(metrics)
    elif section == "Interactive Story Map":
        render_graph_explorer(graph, node_data)
    else:
        render_research_insights(metrics)


@st.cache_data
def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def _load_reviews() -> pd.DataFrame:
    if not REVIEWS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(REVIEWS_PATH)


@st.cache_resource
def _load_graph() -> nx.Graph:
    if not GRAPHML_PATH.exists():
        return nx.Graph()
    return nx.read_graphml(GRAPHML_PATH)


def _inject_css() -> None:
    st.markdown(
        """
        <style>
          .main .block-container{padding-top:1.4rem;max-width:1480px}
          h1,h2,h3{letter-spacing:0}
          div[data-testid="stMetric"]{background:#121722;border:1px solid #273043;border-radius:8px;padding:14px 16px}
          div[data-testid="stMetric"] label{color:#9ca3af}
          .insight-card{background:#121722;border:1px solid #273043;border-radius:8px;padding:16px;margin-bottom:12px;line-height:1.55}
          .insight-card strong{color:#f8fafc}
          .small-muted{color:#9ca3af;font-size:.9rem}
          .finding-box{border-radius:8px;padding:15px 16px;margin:12px 0;line-height:1.6;border:1px solid #2f3a4f;background:#101827}
          .finding-green{border-color:#166534;background:#052e1a}
          .finding-blue{border-color:#1d4ed8;background:#0b1736}
          .finding-orange{border-color:#b45309;background:#2b1905}
          .section-note{color:#9ca3af;font-size:.95rem;margin-bottom:.8rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_overview(metrics: Dict[str, Any], node_data: Dict[str, Any], reviews: pd.DataFrame) -> None:
    st.subheader("Story map overview")
    st.markdown(
        "<div class='section-note'>This view translates the network science into plain-language findings for policy, heritage management, and academic review.</div>",
        unsafe_allow_html=True,
    )

    render_header_kpis(metrics)

    story_cols = st.columns([1.2, 1])
    with story_cols[0]:
        st.markdown("### Quick read")
        render_research_insights(metrics, compact=True)
    with story_cols[1]:
        st.markdown("### Generate summary")
        st.write("Create a short, readable summary for reports, presentations, or classroom discussion.")
        if st.button("Generate overall summary", type="primary"):
            st.session_state["overall_summary"] = generate_overall_summary(metrics, reviews)
        if "overall_summary" in st.session_state:
            st.markdown(f"<div class='insight-card'>{st.session_state['overall_summary']}</div>", unsafe_allow_html=True)

    render_network_hubs_section(metrics)
    render_aspect_sentiment_section(metrics)
    render_covid_natural_experiment(metrics)
    render_visitor_segment_profiles(metrics)


def render_header_kpis(metrics: Dict[str, Any]) -> None:
    story = metrics.get("story_metrics", {})
    cols = st.columns(4)
    cols[0].metric("Network nodes", f"{story.get('total_nodes', 0):,}", help="Unique ideas found in visitor reviews.")
    cols[1].metric("Network edges", f"{story.get('total_edges', 0):,}", help="Connections between visitor ideas.")
    cols[2].metric("Entropy increase", f"{story.get('entropy_increase_pct', 0):.1f}%", help="How much richer this network is than a simple keyword baseline.")
    cols[3].metric("Dual-valence", f"{story.get('dual_valence_instances', 0):,}", help="Moments where visitors describe mixed grief and awe.")


def render_network_hubs_section(metrics: Dict[str, Any]) -> None:
    st.markdown("## Network hubs")
    st.markdown(
        "<div class='section-note'>Hubs are the ideas that connect many visitor stories. They show what the whole experience revolves around.</div>",
        unsafe_allow_html=True,
    )
    hub_data = metrics.get("hub_analysis", {})
    hubs = pd.DataFrame(hub_data.get("top_10_hubs", []))
    type_rows = pd.DataFrame(hub_data.get("type_centrality_table", []))
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("### Top connected ideas")
        if not hubs.empty:
            table = hubs.rename(
                columns={
                    "rank": "Rank",
                    "idea": "Idea",
                    "entity_type": "Topic Type",
                    "category": "Sacred or Practical",
                    "prominence_score": "Prominence Score",
                    "why_it_matters": "Why it matters",
                }
            )[["Rank", "Idea", "Topic Type", "Sacred or Practical", "Prominence Score", "Why it matters"]]
            st.dataframe(
                table.style.format({"Prominence Score": "{:.4f}"}).map(_prominence_color, subset=["Prominence Score"]),
                use_container_width=True,
                hide_index=True,
            )
    with right:
        st.markdown("### Which topic types are most central?")
        if not type_rows.empty:
            type_display = type_rows.rename(
                columns={
                    "label": "Topic Type",
                    "category": "Sacred or Practical",
                    "node_count": "Ideas",
                    "avg_centrality": "Average Prominence",
                    "max_centrality": "Highest Prominence",
                }
            )[["Topic Type", "Sacred or Practical", "Ideas", "Average Prominence", "Highest Prominence"]]
            st.dataframe(
                type_display.style
                .format({"Average Prominence": "{:.5f}", "Highest Prominence": "{:.5f}"})
                .map(_prominence_color, subset=["Average Prominence", "Highest Prominence"]),
                use_container_width=True,
                hide_index=True,
            )
    st.markdown(
        "<div class='finding-box finding-blue'><strong>Interpretation:</strong> Sacred places, rituals, and religious actors dominate the network. "
        "That is different from museum-style heritage sites such as the Forbidden City, where scenic landmarks usually become the main hubs. "
        "Pashupatinath behaves like a living sacred environment, not just a place to sightsee.</div>",
        unsafe_allow_html=True,
    )


def render_aspect_sentiment_section(metrics: Dict[str, Any]) -> None:
    st.markdown("## Aspect sentiment intelligence")
    st.markdown(
        "<div class='section-note'>This table separates spiritual experience from practical management issues, so the overall visitor feeling is easier to understand.</div>",
        unsafe_allow_html=True,
    )
    df = pd.DataFrame(metrics.get("aspect_sentiment", {}).values())
    if df.empty:
        st.warning("Aspect sentiment metrics are not available.")
        return
    display = df.rename(
        columns={
            "label": "Aspect",
            "count": "N",
            "positive_pct": "Positive %",
            "negative_pct": "Negative %",
            "avg_score": "Avg Score",
            "type": "Type",
            "interpretation": "Interpretation",
        }
    )[["Aspect", "N", "Positive %", "Negative %", "Avg Score", "Type", "Interpretation"]]
    st.dataframe(
        display.style
        .format({"Positive %": "{:.1f}%", "Negative %": "{:.1f}%", "Avg Score": "{:.2f}"})
        .map(_positive_percent_color, subset=["Positive %"])
        .map(_negative_percent_color, subset=["Negative %"])
        .map(_score_color, subset=["Avg Score"]),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(
        "<div class='finding-box finding-green'><strong>Interpretation:</strong> Spiritual authenticity and sacred atmosphere are strongly positive, while access fairness, crowding, and environment are the main pain points. "
        "This is the core management story: the sacred experience is powerful, but visitor infrastructure creates friction.</div>",
        unsafe_allow_html=True,
    )


def render_covid_natural_experiment(metrics: Dict[str, Any]) -> None:
    st.markdown("## COVID natural experiment")
    st.markdown(
        "<div class='section-note'>COVID acted like an accidental filter: casual tourism dropped sharply, making devotional visitor signals easier to see.</div>",
        unsafe_allow_html=True,
    )
    df = pd.DataFrame(metrics.get("temporal_detail", {}).values())
    if df.empty:
        st.warning("Temporal detail is not available.")
        return
    display = df.rename(
        columns={
            "label": "Period",
            "review_count": "Reviews",
            "sacred_entity_pct": "Sacred %",
            "avg_sentiment_score": "Avg Feeling",
            "dual_valence_count": "Grief + Awe",
            "spiritual_emotion_count": "Spiritual Feeling",
            "density": "Network Density",
        }
    )[["Period", "Reviews", "Sacred %", "Avg Feeling", "Grief + Awe", "Spiritual Feeling", "Network Density"]]
    st.dataframe(
        display.style.format({"Sacred %": "{:.1f}%", "Avg Feeling": "{:.2f}", "Network Density": "{:.5f}"}).apply(_highlight_covid_row, axis=1),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(
        "<div class='finding-box finding-orange'><strong>Publishable finding:</strong> During the deepest COVID period, review volume collapsed, but sacred content became more concentrated. "
        "This suggests closure filtered out casual tourism noise and exposed a clearer devotional signal from committed visitors. "
        "For policy audiences, this supports treating Pashupatinath as a living sacred system, not only a tourism asset.</div>",
        unsafe_allow_html=True,
    )


def render_visitor_segment_profiles(metrics: Dict[str, Any]) -> None:
    st.markdown("## Visitor segment profiles")
    st.markdown(
        "<div class='section-note'>Different travel groups notice different parts of the sacred experience.</div>",
        unsafe_allow_html=True,
    )
    df = pd.DataFrame(metrics.get("trip_type_profiles", {}).values())
    if df.empty:
        st.warning("Visitor segment profiles are not available.")
        return
    display = df.rename(
        columns={
            "label": "Visitor Group",
            "review_count": "Reviews",
            "sacred_entity_pct": "Sacred %",
            "dual_valence_pct": "Grief + Awe %",
            "spiritual_emotion_pct": "Spiritual Feeling %",
            "avg_sentiment_score": "Avg Feeling",
            "profile": "Research Profile",
        }
    )[["Visitor Group", "Reviews", "Sacred %", "Grief + Awe %", "Spiritual Feeling %", "Avg Feeling", "Research Profile"]]
    st.dataframe(
        display.style
        .format({"Sacred %": "{:.1f}%", "Grief + Awe %": "{:.1f}%", "Spiritual Feeling %": "{:.1f}%", "Avg Feeling": "{:.2f}"})
        .map(_positive_percent_color, subset=["Sacred %", "Spiritual Feeling %"])
        .map(_dual_valence_color, subset=["Grief + Awe %"])
        .map(_score_color, subset=["Avg Feeling"]),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(
        "<div class='finding-box finding-blue'><strong>Segment insight:</strong> Couples tend to register the grief-and-awe experience more distinctly, especially around cremation and river-side ritual spaces. "
        "Family and business visitors lean more toward spiritual interpretation, while friends often behave more like general tourists.</div>",
        unsafe_allow_html=True,
    )


def render_review_analytics(reviews: pd.DataFrame) -> None:
    if reviews.empty:
        st.warning("Review analytics data was not found.")
        return
    st.subheader("What visitors wrote")
    st.write("These charts show when people visited, how they rated the place, who they travelled with, and whether they talked about sacred experiences.")
    display_reviews = reviews.copy()
    if "period" in display_reviews:
        display_reviews["period_label"] = display_reviews["period"].map(PERIOD_LABELS).fillna(display_reviews["period"])
    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(px.histogram(display_reviews, x="year", title="How many reviews were written each year", labels={"year": "Year", "count": "Reviews"}), use_container_width=True)
        st.plotly_chart(px.histogram(display_reviews, x="rating", title="How visitors rated the experience", labels={"rating": "Rating out of 5", "count": "Reviews"}), use_container_width=True)
        st.plotly_chart(px.histogram(display_reviews, x="sentiment_class", title="Overall mood in reviews", labels={"sentiment_class": "Mood", "count": "Reviews"}), use_container_width=True)
    with cols[1]:
        st.plotly_chart(px.histogram(display_reviews, x="trip_type", title="Who visitors travelled with", labels={"trip_type": "Travel group", "count": "Reviews"}), use_container_width=True)
        if "has_sacred_content" in reviews:
            sacred_df = display_reviews.assign(sacred_content=display_reviews["has_sacred_content"].map({True: "Mentions sacred content", False: "Does not mention sacred content"}))
            st.plotly_chart(px.histogram(sacred_df, x="sacred_content", title="Do reviews mention sacred content?", labels={"sacred_content": "Sacred content", "count": "Reviews"}), use_container_width=True)
        st.plotly_chart(px.histogram(display_reviews, x="period_label", title="Reviews across major time periods", labels={"period_label": "Time period", "count": "Reviews"}), use_container_width=True)


def render_network_analytics(metrics: Dict[str, Any], compact: bool = False) -> None:
    graph = metrics.get("graph", {})
    advanced = metrics.get("advanced", {})
    communities = advanced.get("communities", {})
    if not compact:
        st.subheader("How connected the visitor story is")
        st.write(
            "This section explains whether visitor ideas form one shared story or many separate stories. "
            "Higher theme strength means ideas naturally group into clear topics."
        )
    cols = st.columns(5)
    cols[0].metric("Idea connectedness", f"{graph.get('density', 0):.4f}", help="How tightly ideas are connected overall.")
    cols[1].metric("Theme strength", f"{communities.get('modularity', 0):.2f}", help="How clearly the network separates into themes.")
    cols[2].metric("Similar ideas link", f"{graph.get('degree_assortativity', 0):.2f}", help="Whether popular ideas tend to connect with other popular ideas.")
    cols[3].metric("Small groups", f"{graph.get('clustering_coefficient', 0):.2f}", help="How often ideas form small circles of related meaning.")
    cols[4].metric("Big hub effect", f"{graph.get('centralization', 0):.2f}", help="Whether one or two ideas dominate the whole map.")
    temporal = pd.DataFrame(metrics.get("temporal", {})).T
    if not temporal.empty:
        temporal = temporal.reset_index(names="period")
        temporal["period_label"] = temporal["period"].map(PERIOD_LABELS).fillna(temporal["period"])
        st.plotly_chart(
            px.line(
                temporal,
                x="period_label",
                y=["node_count", "edge_count"],
                markers=True,
                title="How the visitor story grew and changed",
                labels={"period_label": "Time period", "value": "Count", "variable": "What is counted"},
            ),
            use_container_width=True,
        )
    if compact:
        return


def render_community_explorer(metrics: Dict[str, Any]) -> None:
    communities = metrics.get("advanced", {}).get("communities", {}).get("communities", [])
    df = pd.DataFrame(communities)
    if df.empty:
        st.warning("Community metrics are not available.")
        return
    st.subheader("Experience themes")
    st.write(
        "A theme is a group of ideas visitors often connect. Instead of numbered communities, each theme is named from its main topic and strongest ideas."
    )
    df["dominant_entity_type_label"] = df["dominant_entity_type"].map(PLAIN_TYPE_LABELS).fillna(df["dominant_entity_type"])
    cols = st.columns([1, 1])
    with cols[0]:
        st.plotly_chart(
            px.bar(
                df.head(25),
                x="node_count",
                y="community_name",
                orientation="h",
                title="Biggest experience themes",
                labels={"node_count": "Number of ideas in theme", "community_name": "Theme name"},
            ).update_layout(yaxis={"categoryorder": "total ascending"}),
            use_container_width=True,
        )
    with cols[1]:
        st.plotly_chart(
            px.scatter(
                df,
                x="density",
                y="average_sentiment",
                size="node_count",
                color="dominant_entity_type_label",
                hover_name="community_name",
                title="Which themes feel positive or negative?",
                labels={
                    "density": "How tightly connected the theme is",
                    "average_sentiment": "Average feeling score",
                    "node_count": "Number of ideas",
                    "dominant_entity_type_label": "Main topic",
                },
            ),
            use_container_width=True,
        )
    st.dataframe(
        df[["community_name", "node_count", "dominant_entity_type_label", "average_sentiment", "density", "top_nodes"]],
        use_container_width=True,
        hide_index=True,
    )


def render_semantic_paths(metrics: Dict[str, Any]) -> None:
    paths = metrics.get("advanced", {}).get("metapaths", {}).get("paths", [])
    df = pd.DataFrame(paths)
    if df.empty:
        st.warning("Meta-path metrics are not available.")
        return
    st.subheader("Visitor journeys")
    st.write(
        "A journey shows a common chain of meaning in reviews. For example, visitors may move from a ritual, to a sacred place, to a spiritual feeling."
    )
    df["plain_path"] = df["path"].map(lambda value: value.replace(" -> ", " to ").replace("_", " "))
    top = df.head(20)
    st.plotly_chart(
        px.bar(
            top,
            x="frequency",
            y="plain_path",
            orientation="h",
            title="Most common visitor journeys",
            labels={"frequency": "How many times this journey appears", "plain_path": "Journey"},
        ).update_layout(yaxis={"categoryorder": "total ascending"}),
        use_container_width=True,
    )
    group_rows = []
    for _, row in df.iterrows():
        groups = row.get("group_frequencies", {}) or {}
        group_rows.append(
            {
                "path": row["path"],
                "pilgrim": groups.get("pilgrim", 0),
                "tourist": groups.get("tourist", 0),
                "solo": groups.get("solo", 0),
                "couples": groups.get("couples", 0),
                "family": groups.get("family", 0),
                "friends": groups.get("friends", 0),
            }
        )
    group_df = pd.DataFrame(group_rows)
    group_df["plain_path"] = group_df["path"].map(lambda value: value.replace(" -> ", " to ").replace("_", " "))
    st.plotly_chart(
        px.bar(
            group_df.head(15),
            x="plain_path",
            y=["pilgrim", "tourist"],
            barmode="group",
            title="Do pilgrims and tourists describe different journeys?",
            labels={"plain_path": "Journey", "value": "Mentions", "variable": "Visitor group"},
        ),
        use_container_width=True,
    )
    st.dataframe(df[["plain_path", "frequency", "prevalence", "significance", "group_frequencies"]], use_container_width=True, hide_index=True)


def render_sentiment_intelligence(metrics: Dict[str, Any]) -> None:
    flow = metrics.get("advanced", {}).get("sentiment_flow", {})
    st.subheader("Feelings and emotions")
    st.write(
        "This section shows which ideas carry strong emotions and whether positive or negative experiences group together."
    )
    cols = st.columns(4)
    cols[0].metric("Similar feelings connect", f"{flow.get('assortativity_score', 0):.2f}")
    cols[1].metric("Feeling togetherness", f"{flow.get('homophily_score', 0):.2f}")
    cols[2].metric("Neighbor mood match", f"{flow.get('sentiment_correlation', 0):.2f}")
    cols[3].metric("Emotion pockets", f"{flow.get('sentiment_clustering_coefficient', 0):.2f}")
    anchors = pd.DataFrame(flow.get("emotional_anchors", []))
    if anchors.empty:
        st.warning("Emotional anchors are not available.")
        return
    st.plotly_chart(
        px.bar(
            anchors,
            x="emotional_influence_score",
            y="node",
            color="role",
            orientation="h",
            title="Ideas that carry the strongest emotions",
            labels={"emotional_influence_score": "Emotional strength", "node": "Idea", "role": "Role"},
        ).update_layout(yaxis={"categoryorder": "total ascending"}),
        use_container_width=True,
    )
    st.dataframe(anchors, use_container_width=True, hide_index=True)


def render_motif_evolution(metrics: Dict[str, Any]) -> None:
    motifs = metrics.get("advanced", {}).get("motifs", {}).get("motifs", [])
    df = pd.DataFrame(motifs)
    if df.empty:
        st.warning("Motif metrics are not available.")
        return
    st.subheader("Repeating experience patterns")
    st.write(
        "A pattern is a small repeated story shape. It shows which combinations of ideas keep appearing together over time."
    )
    df["plain_composition"] = df["entity_composition"].map(lambda value: value.replace("_", " "))
    st.plotly_chart(
        px.bar(
            df.head(25),
            x="frequency",
            y="plain_composition",
            color="motif_type",
            orientation="h",
            title="Most repeated experience patterns",
            labels={"frequency": "How often it repeats", "plain_composition": "Pattern", "motif_type": "Pattern shape"},
        ).update_layout(yaxis={"categoryorder": "total ascending"}),
        use_container_width=True,
    )
    period_rows = []
    for _, row in df.head(20).iterrows():
        for period, frequency in (row.get("periods", {}) or {}).items():
            period_rows.append({"motif": row["plain_composition"], "period": PERIOD_LABELS.get(period, period), "frequency": frequency})
    if period_rows:
        period_df = pd.DataFrame(period_rows)
        st.plotly_chart(px.line(period_df, x="period", y="frequency", color="motif", markers=True, title="How repeated patterns changed over time", labels={"period": "Time period", "frequency": "Pattern count", "motif": "Pattern"}), use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_graph_explorer(graph: nx.Graph, node_data: Dict[str, Any]) -> None:
    if graph.number_of_nodes() == 0:
        st.warning("Graph artifact was not found. Run `PIPELINE_MODE=social python -m app.main` first.")
        return
    st.subheader("Interactive story map")
    st.write(
        "Search for an idea, drag dots around, zoom in, and filter by topic. Neighboring dots are ideas visitors often connect."
    )
    st.sidebar.markdown("### Story map filters")
    entity_types = sorted({attrs.get("entity_type", "unknown") for _, attrs in graph.nodes(data=True)})
    type_options = {PLAIN_TYPE_LABELS.get(entity_type, entity_type): entity_type for entity_type in entity_types}
    if "selected_entity_type_labels" not in st.session_state:
        st.session_state["selected_entity_type_labels"] = list(type_options.keys())
    type_cols = st.sidebar.columns(2)
    if type_cols[0].button("Select all topics"):
        st.session_state["selected_entity_type_labels"] = list(type_options.keys())
    if type_cols[1].button("Select no topics"):
        st.session_state["selected_entity_type_labels"] = []
    selected_type_labels = st.sidebar.multiselect(
        "Topics",
        list(type_options.keys()),
        key="selected_entity_type_labels",
        help="Choose the kinds of ideas to show.",
    )
    selected_types = {type_options[label] for label in selected_type_labels}

    community_names = sorted({
        str(attrs.get("community_name") or f"Theme {attrs.get('community_id', '')}")
        for _, attrs in graph.nodes(data=True)
        if attrs.get("community_id", "") != ""
    })
    if "selected_community_names" not in st.session_state:
        st.session_state["selected_community_names"] = community_names[:20] if len(community_names) > 20 else community_names
    community_cols = st.sidebar.columns(2)
    if community_cols[0].button("Select all themes"):
        st.session_state["selected_community_names"] = community_names
    if community_cols[1].button("Select no themes"):
        st.session_state["selected_community_names"] = []
    selected_communities = st.sidebar.multiselect(
        "Themes",
        community_names,
        key="selected_community_names",
        help="Themes are named groups of related visitor ideas.",
    )
    search = st.sidebar.text_input("Search an idea", help="Try words like cremation, Bagmati, crowd, guide, or temple.")

    keep = []
    for node, attrs in graph.nodes(data=True):
        community = str(attrs.get("community_name") or f"Theme {attrs.get('community_id', '')}")
        matches_type = attrs.get("entity_type", "unknown") in selected_types
        matches_community = not selected_communities or community in selected_communities
        matches_search = not search or search.lower() in str(node).lower()
        if matches_type and matches_community and matches_search:
            keep.append(node)

    subgraph = graph.subgraph(keep).copy()
    if search and keep:
        neighbors = set()
        for node in keep:
            neighbors.update(graph.neighbors(node))
        subgraph = graph.subgraph(set(keep) | neighbors).copy()

    temp_path = OUTPUT_DIR / "temp_explorer.html"
    PyVisExporter(OUTPUT_DIR).export(subgraph, filename=temp_path.name, max_nodes=900)
    st.caption(f"Showing {subgraph.number_of_nodes():,} ideas and {subgraph.number_of_edges():,} connections.")
    components.html(temp_path.read_text(encoding="utf-8"), height=820, scrolling=False)


def render_research_insights(metrics: Dict[str, Any], compact: bool = False) -> None:
    advanced = metrics.get("advanced", {})
    communities = advanced.get("communities", {}).get("communities", [])
    paths = advanced.get("metapaths", {}).get("paths", [])
    motifs = advanced.get("motifs", {}).get("motifs", [])
    anchors = advanced.get("sentiment_flow", {}).get("emotional_anchors", [])
    insights = [
        ("Biggest theme", f"{communities[0]['community_name']} is the largest group of related visitor ideas.") if communities else None,
        ("Most common journey", f"{paths[0]['path'].replace(' -> ', ' to ').replace('_', ' ')} is the most frequent visitor journey.") if paths else None,
        ("Most repeated pattern", f"{motifs[0]['entity_composition'].replace('_', ' ')} is the most common repeated experience pattern.") if motifs else None,
        ("Strongest feeling anchor", f"{anchors[0]['node']} carries the strongest emotional influence in the network.") if anchors else None,
        ("Most positive theme", _highest_sentiment_cluster(communities)) if communities else None,
    ]
    for item in [x for x in insights if x]:
        st.markdown(f"<div class='insight-card'><strong>{item[0]}</strong><br><span class='small-muted'>{item[1]}</span></div>", unsafe_allow_html=True)
    if not compact:
        st.caption("Insight cards are derived from exported metrics and are ready for paper drafting or downstream AI summarization.")


def _highest_sentiment_cluster(communities: List[Dict[str, Any]]) -> str:
    community = max(communities, key=lambda row: row.get("average_sentiment", 0))
    return f"{community['community_name']} has the most positive feeling score ({community.get('average_sentiment', 0):.2f})."


def _score_color(value: float) -> str:
    if value >= 0.65:
        return "color:#16a34a;font-weight:600"
    if value <= 0.45:
        return "color:#dc2626;font-weight:600"
    return "color:#d97706;font-weight:600"


def _prominence_color(value: float) -> str:
    if value >= 0.02:
        return "color:#16a34a;font-weight:600"
    if value >= 0.006:
        return "color:#d97706;font-weight:600"
    return "color:#6b7280"


def _positive_percent_color(value: float) -> str:
    if value >= 70:
        return "color:#16a34a;font-weight:600"
    if value <= 25:
        return "color:#dc2626;font-weight:600"
    return "color:#d97706;font-weight:600"


def _negative_percent_color(value: float) -> str:
    if value >= 60:
        return "color:#dc2626;font-weight:600"
    if value <= 15:
        return "color:#16a34a;font-weight:600"
    return "color:#d97706;font-weight:600"


def _dual_valence_color(value: float) -> str:
    if value >= 2:
        return "color:#7c3aed;font-weight:600"
    return "color:#6b7280"


def _highlight_covid_row(row: pd.Series) -> List[str]:
    if row.get("Period") == "Deep COVID period":
        return ["background-color:#2b1905;color:#f8fafc;font-weight:600"] * len(row)
    return [""] * len(row)


def generate_overall_summary(metrics: Dict[str, Any], reviews: pd.DataFrame) -> str:
    graph = metrics.get("graph", {})
    advanced = metrics.get("advanced", {})
    communities = advanced.get("communities", {}).get("communities", [])
    paths = advanced.get("metapaths", {}).get("paths", [])
    motifs = advanced.get("motifs", {}).get("motifs", [])
    flow = advanced.get("sentiment_flow", {})
    top_theme = communities[0]["community_name"] if communities else "no clear theme"
    top_path = paths[0]["path"].replace(" -> ", " to ").replace("_", " ") if paths else "no clear journey"
    top_motif = motifs[0]["entity_composition"].replace("_", " ") if motifs else "no repeated pattern"
    review_count = len(reviews)
    node_count = graph.get("nodes", 0)
    edge_count = graph.get("edges", 0)
    homophily = flow.get("homophily_score", 0)
    return (
        f"<strong>Overall summary:</strong> The dataset contains {review_count:,} visitor reviews. "
        f"From these reviews, the system found {node_count:,} visitor ideas and {edge_count:,} connections between them. "
        f"The biggest experience theme is <strong>{top_theme}</strong>. "
        f"The most common visitor journey is <strong>{top_path}</strong>. "
        f"The most repeated experience pattern is <strong>{top_motif}</strong>. "
        f"The feeling togetherness score is <strong>{homophily:.2f}</strong>, which shows how often similar emotions connect in the visitor story map."
    )


if __name__ == "__main__":
    main()
