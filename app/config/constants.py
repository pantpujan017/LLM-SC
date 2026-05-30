# app/config/constants.py

"""
Configuration constants for PHASE 2 data cleaning pipeline.
Curated for Pashupatinath Temple research, expandable for future sites.
"""

# ============================================================
# TRIP TYPE NORMALIZATION MAPPING
# ============================================================
# Maps raw trip_type values from API to canonical research labels
TRIP_TYPE_MAPPING = {
    "solo": "solo",
    "family": "family",
    "friends": "friends",
    "couples": "couples",
    "business": "business",
    # Add more as needed for other sites
}

# ============================================================
# TEMPORAL PERIOD MAPPING
# ============================================================
# Maps years to research periods for Pashupatinath context
# Chosen to reflect:
# - Pre-pandemic baseline (early_period, growth_period, pre_covid_peak)
# - COVID-19 impact period (covid_onset, covid_deep)
# - Recovery trajectory (recovery_early, recovery_late, post_recovery)
PERIOD_MAPPING = {
    (2008, 2012): "early_period",       # Initial online review era
    (2013, 2017): "growth_period",      # Rapid growth in tourism
    (2018, 2019): "pre_covid_peak",     # Peak pre-pandemic years
    (2020, 2020): "covid_onset",        # Pandemic begins
    (2021, 2021): "covid_deep",         # Deepest pandemic period
    (2022, 2022): "recovery_early",     # Early recovery
    (2023, 2023): "recovery_late",      # Continued recovery
    (2024, 9999): "post_recovery",      # Post-recovery normalization
}

# ============================================================
# SACRED KEYWORDS FOR RELIGIOUS CONTENT DETECTION
# ============================================================
# Curated list of sacred/religious terms for Pashupatinath
# Expandable for future sacred sites (add prefix: e.g., "borobudur_*")
SACRED_KEYWORDS = {
    # Sanskrit/Hindu concepts
    "darshan",
    "shiv",
    "shiva",
    "mahadev",
    "sadhu",
    "aarti",
    "aarati",
    "ganga aarti",
    "moksha",
    "ritual",
    "worship",
    "blessing",
    "divine",
    "holy",
    "sacred",
    
    # Pashupatinath-specific
    "pashupatinath",
    "bagmati",
    "ghat",
    
    # Temple/religious infrastructure
    "temple",
    "cremation",
    "funeral",
    "prayer",
    "ceremony",
    
    # Religious identity
    "spiritual",
    "hindu",
}

# ============================================================
# SENTIMENT CLASSIFICATION RULES
# ============================================================
# Rule-based sentiment from rating (no ML models)
SENTIMENT_RULES = {
    # positive: highly satisfied
    5: "positive",
    4: "positive",
    # neutral: moderate
    3: "neutral",
    # negative: dissatisfied
    2: "negative",
    1: "negative",
}

# ============================================================
# REVIEWER TYPE CLASSIFICATION
# ============================================================
# Infer from contribution count
REVIEWER_TYPE_THRESHOLDS = {
    "elite": 100,        # >= 100 contributions
    "experienced": 25,   # >= 25 contributions
    "casual": 0,         # < 25 contributions
}

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

ENTITY_TYPE_FIXES = {
    "cremation ceremony": "ritual",
    "crowd_management":   "problem",
    "description":        "scenic_spot",
    "environment":        "sacred_space",
    "contrast":           "general_sentiment",
}

SENTIMENT_LABEL_FIXES = {
    "mixed": "neutral",
    "dual_valence": "neutral",
}

RELATION_TYPE_FIXES = {
    "cultural_rule": "description",
}

# Canonical sets for validation
VALID_ENTITY_TYPES = {
    "scenic_spot", "problem", "facility_service", "general_sentiment",
    "ritual", "religious_actor", "sacred_space", "spiritual_emotion",
    "festival_event", "cultural_rule", "sacred_object", "dual_valence"
}

VALID_SENTIMENTS = {"positive", "neutral", "negative"}

VALID_RELATIONS = {"co_occurrence", "causal", "description", "contrast"}

# ============================================================
# TEXT CLEANING CONFIGURATION
# ============================================================
# Unicode normalization form
UNICODE_NORM_FORM = "NFD"  # Decomposed form

# Collapse excessive punctuation
PUNCTUATION_COLLAPSE_RULES = {
    r"!{2,}": "!",
    r"\?{2,}": "?",
    r"\.{2,}": ".",
}

# HTML entities to unescape
HTML_ENTITIES = {
    "&quot;": '"',
    "&apos;": "'",
    "&lt;": "<",
    "&gt;": ">",
    "&amp;": "&",
}

# ============================================================
# PIPELINE CONFIGURATION
# ============================================================
PIPELINE_VERSION = "2.0"
DEFAULT_YEAR_MISSING = 2024  # Default year if unparseable
DEFAULT_RATING_MISSING = 3   # Default rating if missing
