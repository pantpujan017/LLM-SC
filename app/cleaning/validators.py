# app/cleaning/validators.py

from typing import List, Tuple
from loguru import logger
from app.models.dataset import CleanedReview


class DatasetValidator:
    """
    Multi-stage validation for cleaned dataset.
    
    Validates:
    - Pydantic schema compliance
    - Required fields populated
    - Value ranges and constraints
    - Data quality metrics
    """
    
    @staticmethod
    def validate_batch(reviews: List[CleanedReview]) -> Tuple[List[CleanedReview], int]:
        """
        Validate all reviews.
        
        Args:
            reviews: List of CleanedReview objects
            
        Returns:
            Tuple of (valid_reviews, failed_count)
        """
        valid = []
        failed = 0
        
        for review in reviews:
            if DatasetValidator.check_review(review):
                valid.append(review)
            else:
                failed += 1
        
        logger.info(f"Validation: {len(valid)} valid, {failed} failed")
        return valid, failed
    
    @staticmethod
    def check_review(review: CleanedReview) -> bool:
        """
        Comprehensive check of single review.
        
        Args:
            review: CleanedReview object
            
        Returns:
            True if valid, False if any check fails
        """
        # Check required fields
        if not DatasetValidator._check_required_fields(review):
            logger.debug(f"Review {review.review_id}: missing required fields")
            return False
        
        # Check value ranges
        if not DatasetValidator._check_value_ranges(review):
            logger.debug(f"Review {review.review_id}: invalid value ranges")
            return False
        
        return True
    
    @staticmethod
    def _check_required_fields(review: CleanedReview) -> bool:
        """Ensure all critical fields are populated."""
        
        required_fields = [
            'review_id',
            'text_clean',
            'rating',
            'sentiment_class',
            'year',
            'period',
            'trip_type',
            'reviewer_type',
            'word_count',
            'has_sacred_content'
        ]
        
        for field in required_fields:
            value = getattr(review, field, None)
            
            # Allow False for booleans
            if field == 'has_sacred_content':
                if value is None:
                    return False
            elif value is None or (isinstance(value, str) and value == ""):
                return False
        
        return True
    
    @staticmethod
    def _check_value_ranges(review: CleanedReview) -> bool:
        """Validate value ranges and constraints."""
        
        # Rating: 1-5
        if not (1 <= review.rating <= 5):
            return False
        
        # Word count: non-negative
        if review.word_count < 0:
            return False
        
        # Year: reasonable range
        if not (1990 <= review.year <= 2100):
            return False
        
        # Sentiment: one of three values
        valid_sentiments = {"positive", "neutral", "negative"}
        if review.sentiment_class not in valid_sentiments:
            return False
        
        # Trip type: known or unknown
        valid_trip_types = {"solo", "family", "friends", "couples", "business", "unknown"}
        if review.trip_type not in valid_trip_types:
            return False
        
        # Reviewer type: known or unknown
        valid_reviewer_types = {"elite", "experienced", "casual", "unknown"}
        if review.reviewer_type not in valid_reviewer_types:
            return False
        
        # Period: known or unknown
        valid_periods = {
            "early_period", "growth_period", "pre_covid_peak",
            "covid_onset", "covid_deep", "recovery_early",
            "recovery_late", "post_recovery", "unknown"
        }
        if review.period not in valid_periods:
            return False
        
        return True
