# app/social/config/constants.py

"""
PHASE 3 Configuration Constants: Social Network Computing

Curated for Pashupatinath Temple research, expandable for future sacred sites.
"""

from typing import Dict, List, Set

# ============================================================
# ASPECT TO ENTITY TYPE MAPPING
# ============================================================
# Maps sentiment aspects to the entity types they describe
ASPECT_TO_ENTITY_TYPE = {
    "service": ["facility_service"],
    "facility": ["facility_service"],
    "environment": ["scenic_spot", "sacred_space"],
    "sacred_atmosphere": ["sacred_space"],
    "spiritual_authenticity": ["spiritual_emotion"],
    "ritual_experience": ["ritual", "festival_event"],
    "cultural_sensitivity": ["cultural_rule"],
    "access_fairness": ["problem"],
    "crowd_management": ["problem"],
    "general_sentiment": ["general_sentiment"],
    "problem": ["problem"],
    "scenic_spot": ["scenic_spot"],
}

# ============================================================
# ENTITY TYPES (12 types: 4 general + 8 sacred-specific)
# ============================================================
ENTITY_TYPES: List[str] = [
    # General/practical types
    "facility_service",      # amenities, infrastructure
    "scenic_spot",           # viewpoint, location
    
    # Sacred-specific types (Pashupatinath context)
    "ritual",                # ceremony, prayer, worship practice
    "religious_actor",       # sadhus, priests, monks
    "sacred_space",          # temple, ghat, cremation area
    "spiritual_emotion",     # moksha-seeking, enlightenment, reverence
    
    # General with sacred implications
    "cultural_rule",         # conduct, taboos, etiquette
    "problem",               # issues, complaints, challenges
    
    # Additional derived types
    "festival_event",        # seasonal celebrations, rituals
    "sacred_object",         # lingam, statue, sacred item
    "dual_valence",          # mixed sentiment (awe + discomfort)
    "general_sentiment",     # overall experience rating
]

# ============================================================
# RELATION TYPES (4 types: co-occurrence, causal, description, contrast)
# ============================================================
RELATION_TYPES: Dict[str, str] = {
    "co_occurrence": "Two entities appear together in same review/sentence",
    "causal": "One entity causes/leads to another (A → B)",
    "description": "One entity describes/characterizes another (A describes B)",
    "contrast": "Two entities are opposed/contrasted (A vs B)",
}

# ============================================================
# SACRED ENTITY CLASSIFICATION
# ============================================================
SACRED_ENTITY_TYPES: Set[str] = {
    "ritual",
    "religious_actor",
    "sacred_space",
    "spiritual_emotion",
    "festival_event",
    "cultural_rule",
    "sacred_object",
    "dual_valence",
}

# ============================================================
# NETWORK CONSTRUCTION PARAMETERS
# ============================================================
# Edge weighting formula: w_ij = α*f_cooccur + β*g_causal
# Weights: co-occurrence dominates, causal adds semantic depth
EDGE_WEIGHT_ALPHA: float = 0.7     # Co-occurrence coefficient
EDGE_WEIGHT_BETA: float = 0.3      # Causal/description/contrast coefficient

# Normalization strategy
NORMALIZE_ENTITY_NAMES: bool = True  # lowercase + strip whitespace
DEDUPLICATION_STRATEGY: str = "concept_level"  # Use concept-level (not instance-level)

# ============================================================
# TEMPORAL PERIODS (8 periods: reflects COVID impact + recovery)
# ============================================================
TEMPORAL_PERIODS: Dict[str, tuple] = {
    "early_period": (2008, 2012),      # Initial online review era
    "growth_period": (2013, 2017),     # Rapid tourism growth
    "pre_covid_peak": (2018, 2019),    # Peak pre-pandemic
    "covid_onset": (2020, 2020),       # Pandemic begins
    "covid_deep": (2021, 2021),        # Deepest pandemic
    "recovery_early": (2022, 2022),    # Early recovery
    "recovery_late": (2023, 2023),     # Continued recovery
    "post_recovery": (2024, 9999),     # Post-recovery normalization
}

# ============================================================
# SENTIMENT ASPECTS (6 aspects: 3 original + 3 sacred-specific)
# ============================================================
SENTIMENT_ASPECTS: Dict[str, str] = {
    # Original TripAdvisor aspects
    "service": "Staff behavior, responsiveness, helpfulness",
    "facility": "Infrastructure, amenities, cleanliness",
    "environment": "Surroundings, atmosphere, aesthetics",
    
    # Sacred-specific aspects for Pashupatinath
    "sacred_atmosphere": "Spiritual feeling, sacredness, holiness perceived",
    "spiritual_authenticity": "Genuineness of religious practice, cultural truth",
    "ritual_experience": "Ceremony participation, prayer, worship quality",
    "cultural_sensitivity": "Respect for customs, reverence shown",
    "access_fairness": "Discrimination, caste considerations, inclusivity",
    "crowd_management": "Visitor flow, respectful density, sacred space integrity",
}

ORIGINAL_SENTIMENT_ASPECTS: Set[str] = {
    "service",
    "facility",
    "environment",
}

SACRED_SENTIMENT_ASPECTS: Set[str] = {
    "sacred_atmosphere",
    "spiritual_authenticity",
    "ritual_experience",
    "cultural_sensitivity",
    "access_fairness",
    "crowd_management",
}

ASPECT_INTERPRETATIONS: Dict[str, str] = {
    "spiritual_authenticity": "Site feels genuinely sacred",
    "sacred_atmosphere": "Visitors feel a strong holy atmosphere",
    "ritual_experience": "Rituals are meaningful to witness",
    "service": "Guides and visitor help shape the experience",
    "facility": "Infrastructure and entry process affect comfort",
    "cultural_sensitivity": "Respect, rules, and tourist behavior create tension",
    "environment": "River pollution and surroundings affect perception",
    "crowd_management": "Crowding makes sacred space harder to experience",
    "access_fairness": "Non-Hindu access rules are the most contentious issue",
}

# ============================================================
# TRIP TYPE CATEGORIES (5 types: from TripAdvisor data)
# ============================================================
TRIP_TYPES: List[str] = [
    "solo",
    "couples",
    "family",
    "friends",
    "business",
]

TRIP_TYPE_PROFILES: Dict[str, str] = {
    "business": "Curious outsider",
    "family": "Likely pilgrim",
    "friends": "Tourist-leaning visitor",
    "solo": "Mixed sacred seeker",
    "couples": "Experiential tourist",
}

PERIOD_LABELS: Dict[str, str] = {
    "early_period": "Early years",
    "growth_period": "Tourism growth",
    "pre_covid_peak": "Before COVID peak",
    "covid_onset": "COVID begins",
    "covid_deep": "Deep COVID period",
    "recovery_early": "Early recovery",
    "recovery_late": "Later recovery",
    "post_recovery": "After recovery",
}

# ============================================================
# CENTRALITY & ANALYSIS THRESHOLDS
# ============================================================
# Top-N nodes to report
TOP_N_NODES: int = 20

# Degree centrality threshold for "hub" status
HUB_CENTRALITY_THRESHOLD: float = 0.05

# Minimum component size to analyze (nodes)
MIN_COMPONENT_SIZE: int = 3

# ============================================================
# GRAPH STATISTICS & METRICS
# ============================================================
# Information entropy baseline for comparison
# Traditional NLP baseline: star-shaped network with few hubs
TRADITIONAL_NLP_ENTROPY_BASELINE: float = 6.1545  # bits (from original paper)

# ============================================================
# OUTPUT CONFIGURATION
# ============================================================
# Export formats
EXPORT_FORMATS: List[str] = [
    "graphml",      # NetworkX-native, opens in Gephi/Cytoscape
    "json",         # Metrics and statistics JSON
    "html_report",  # Human-readable markdown + tables
]

# Output directory relative to project root
OUTPUT_DIR: str = "app/storage/social_network_output/"

# ============================================================
# PIPELINE VERSION
# ============================================================
PHASE_3_VERSION: str = "3.0"

COLOR_PALETTE = {
    "ritual": "#C5A059",            # Heritage Gold
    "religious_actor": "#B22222",   # Sacred Red
    "sacred_space": "#4682B4",      # Steel Blue
    "spiritual_emotion": "#9370DB", # Medium Purple
    "cultural_rule": "#8FBC8F",     # Dark Sea Green
    "festival_event": "#FF69B4",    # Hot Pink
    "sacred_object": "#DAA520",     # Goldenrod
    "dual_valence": "#708090",      # Slate Gray
    "facility_service": "#BDB76B",  # Dark Khaki
    "scenic_spot": "#ADD8E6",       # Light Blue
    "problem": "#CD5C5C",           # Indian Red
    "general_sentiment": "#D3D3D3", # Light Gray
}

# Human-readable labels for technical metrics
METRIC_LABELS = {
    "degree_centrality": "Prominence Score",
    "weighted_degree": "Connection Strength",
    "entropy": "Experience Diversity",
    "density": "Network Cohesion",
}

# Entity type descriptive labels for tooltips
ENTITY_DESCRIPTIONS = {
    "ritual": "Sacred ceremonies and worship practices",
    "religious_actor": "Spiritual leaders, sadhus, and priests",
    "sacred_space": "Holy sites, ghats, and temple areas",
    "spiritual_emotion": "Feelings of awe, reverence, and moksha",
    "cultural_rule": "Traditional conduct and etiquette",
    "festival_event": "Seasonal celebrations and holy days",
    "sacred_object": "Holy artifacts and spiritual symbols",
    "dual_valence": "Experiences of mixed awe and discomfort",
    "facility_service": "Infrastructure and visitor amenities",
    "scenic_spot": "Visual landmarks and viewpoints",
    "problem": "Challenges and areas for improvement",
    "general_sentiment": "Overall visitor impression",
}
