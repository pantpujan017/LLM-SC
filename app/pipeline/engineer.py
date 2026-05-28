# app/pipeline/engineer.py

from datetime import datetime
from typing import Optional, List
from loguru import logger

from app.models.dataset import CleanedReview
from app.cleaning.text_cleaning import TextCleaner
from app.cleaning.sacred_keywords import SacredContentDetector
from app.config.constants import (
    TRIP_TYPE_MAPPING,
    PERIOD_MAPPING,
    SENTIMENT_RULES,
    REVIEWER_TYPE_THRESHOLDS,
    DEFAULT_YEAR_MISSING,
    DEFAULT_RATING_MISSING,
)


class FeatureEngineer:
    """
    Extract and engineer features for research dataset.
    
    Transforms raw review data into standardized research fields:
    - Text cleaning with unicode normalization
    - Date parsing and year extraction
    - Rule-based sentiment classification
    - Reviewer expertise inference
    - Sacred content detection
    - Temporal period mapping
    """
    
    def __init__(self):
        """Initialize cleaning and detection utilities."""
        self.cleaner = TextCleaner()
        self.sacred_detector = SacredContentDetector()
    
    def process_batch(self, flat_reviews: List[dict]) -> List[CleanedReview]:
        """
        Process batch of flattened reviews.
        
        Args:
            flat_reviews: List of raw review dictionaries
            
        Returns:
            List of CleanedReview objects
        """
        cleaned = []
        failed = 0
        
        for i, review_dict in enumerate(flat_reviews):
            try:
                cleaned_review = self._process_single(review_dict)
                cleaned.append(cleaned_review)
            except Exception as e:
                logger.debug(f"Failed to process review {i}: {e}")
                failed += 1
                continue
        
        logger.info(
            f"Feature engineering: {len(cleaned)} processed, {failed} failed"
        )
        return cleaned
    
    def _process_single(self, review_dict: dict) -> CleanedReview:
        """
        Process single review, extract all features.
        
        Args:
            review_dict: Raw review dictionary from API
            
        Returns:
            CleanedReview with all engineered features
        """
        
        # ============================================================
        # BASIC FIELDS
        # ============================================================
        
        review_id = str(review_dict.get("review_id", ""))
        rating = self._extract_rating(review_dict)
        raw_text = review_dict.get("text", "") or ""
        
        # ============================================================
        # DATE/YEAR EXTRACTION
        # ============================================================
        # Use published_at_date per requirements
        published_date = review_dict.get("published_at_date")
        year = self._extract_year(published_date)
        
        # ============================================================
        # TEXT CLEANING
        # ============================================================
        text_clean = self.cleaner.clean(raw_text)
        
        # ============================================================
        # FEATURE ENGINEERING
        # ============================================================
        
        # Sentiment: rule-based from rating
        sentiment_class = self._classify_sentiment(rating)
        
        # Trip type: normalize to canonical set
        trip_type = self._normalize_trip_type(
            review_dict.get("trip", {}).get("trip_type")
        )
        
        # Reviewer type: infer from contribution count
        contributions = review_dict.get("reviewer", {}).get("contribution_count")
        reviewer_type = self._infer_reviewer_type(contributions)
        
        # Word count: count tokens in cleaned text
        word_count = self.cleaner.word_count(text_clean)
        
        # Sacred content: boolean flag
        has_sacred = self.sacred_detector.has_sacred_content(text_clean)
        
        # Period: map year to temporal cohort
        period = self._map_period(year)
        
        # ============================================================
        # BUILD CLEANED REVIEW
        # ============================================================
        
        return CleanedReview(
            review_id=review_id,
            text_clean=text_clean,
            rating=rating,
            sentiment_class=sentiment_class,
            year=year,
            trip_type=trip_type,
            reviewer_type=reviewer_type,
            word_count=word_count,
            has_sacred_content=has_sacred,
            period=period,
        )
    
    # ============================================================
    # FIELD EXTRACTION METHODS
    # ============================================================
    
    @staticmethod
    def _extract_rating(review_dict: dict) -> int:
        """
        Extract rating, default to neutral if missing.
        
        Args:
            review_dict: Raw review dictionary
            
        Returns:
            Rating 1-5, or DEFAULT_RATING_MISSING if invalid
        """
        rating = review_dict.get("rating")
        
        if isinstance(rating, int) and 1 <= rating <= 5:
            return rating
        
        return DEFAULT_RATING_MISSING
    
    @staticmethod
    def _extract_year(date_str: Optional[str]) -> int:
        """
        Extract year from ISO 8601 date string.
        
        Args:
            date_str: ISO date string (e.g., "2026-04-16")
            
        Returns:
            Year as integer, or DEFAULT_YEAR_MISSING if unparseable
        """
        if not date_str:
            return DEFAULT_YEAR_MISSING
        
        try:
            # Handle ISO 8601 format: YYYY-MM-DD
            dt = datetime.fromisoformat(date_str)
            return dt.year
        except (ValueError, TypeError):
            return DEFAULT_YEAR_MISSING
    
    @staticmethod
    def _classify_sentiment(rating: int) -> str:
        """
        Rule-based sentiment classification from rating.
        
        Rules:
        - rating >= 4: positive
        - rating == 3: neutral
        - rating <= 2: negative
        
        Args:
            rating: Rating 1-5
            
        Returns:
            Sentiment class: "positive", "neutral", or "negative"
        """
        return SENTIMENT_RULES.get(rating, "neutral")
    
    @staticmethod
    def _normalize_trip_type(trip_type: Optional[str]) -> str:
        """
        Normalize trip type to canonical research set.
        
        Canonical values: solo, family, friends, couples, business, unknown
        
        Args:
            trip_type: Raw trip type from API
            
        Returns:
            Normalized trip type or "unknown"
        """
        if not trip_type:
            return "unknown"
        
        normalized = trip_type.lower().strip()
        
        return TRIP_TYPE_MAPPING.get(normalized, "unknown")
    
    @staticmethod
    def _infer_reviewer_type(contributions: Optional[int]) -> str:
        """
        Infer reviewer expertise level from contribution count.
        
        Classification:
        - contributions >= 100: elite
        - 25 <= contributions < 100: experienced
        - contributions < 25: casual
        - null/missing: unknown
        
        Args:
            contributions: Number of contributions (or None)
            
        Returns:
            Reviewer type: "elite", "experienced", "casual", or "unknown"
        """
        if contributions is None:
            return "unknown"
        
        thresholds = REVIEWER_TYPE_THRESHOLDS
        
        if contributions >= thresholds["elite"]:
            return "elite"
        elif contributions >= thresholds["experienced"]:
            return "experienced"
        else:
            return "casual"
    
    @staticmethod
    def _map_period(year: int) -> str:
        """
        Map year to temporal research period.
        
        Cohorts designed for Pashupatinath tourism analysis:
        - early_period (2008-2012): Initial online review era
        - growth_period (2013-2017): Rapid growth in tourism
        - pre_covid_peak (2018-2019): Peak pre-pandemic years
        - covid_onset (2020): Pandemic begins
        - covid_deep (2021): Deepest pandemic period
        - recovery_early (2022): Early recovery
        - recovery_late (2023): Continued recovery
        - post_recovery (2024+): Post-recovery normalization
        
        Args:
            year: Year (integer)
            
        Returns:
            Period name, or "unknown" if out of range
        """
        for (start, end), period_name in PERIOD_MAPPING.items():
            if start <= year <= end:
                return period_name
        
        return "unknown"
