# app/models/dataset.py

from __future__ import annotations

from pydantic import BaseModel, Field


class CleanedReview(BaseModel):
    """Research-ready cleaned review for PHASE 2."""
    
    review_id: str = Field(..., description="Unique review identifier")
    text_clean: str = Field(..., description="Cleaned and normalized review text")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    sentiment_class: str = Field(
        ...,
        description="Rule-based sentiment: positive/neutral/negative"
    )
    year: int = Field(..., ge=1990, le=2100, description="Year extracted from published_at_date")
    trip_type: str = Field(
        ...,
        description="Normalized trip type: solo/family/friends/couples/business/unknown"
    )
    reviewer_type: str = Field(
        ...,
        description="Inferred from contributions: elite/experienced/casual/unknown"
    )
    word_count: int = Field(..., ge=0, description="Token count after cleaning")
    has_sacred_content: bool = Field(
        ...,
        description="Boolean: True if contains sacred/religious terminology"
    )
    period: str = Field(
        ...,
        description="Temporal cohort mapping from year"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "review_id": "1056790466",
                "text_clean": "pashupatinath temple is one of the must visit places in kathmandu...",
                "rating": 5,
                "sentiment_class": "positive",
                "year": 2026,
                "trip_type": "solo",
                "reviewer_type": "elite",
                "word_count": 87,
                "has_sacred_content": True,
                "period": "post_recovery"
            }
        }


class DatasetMetadata(BaseModel):
    """Pipeline execution metadata for reproducibility and audit."""
    
    total_raw_reviews: int = Field(..., description="Raw reviews from JSON")
    total_cleaned_reviews: int = Field(..., description="After deduplication")
    duplicates_found: int = Field(..., description="Duplicate review_ids removed")
    processing_time_seconds: float = Field(..., description="Pipeline execution time")
    pipeline_version: str = Field(default="2.0", description="PHASE version")
    execution_timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    sacred_content_count: int = Field(..., description="Reviews with sacred content")
    sentiment_distribution: dict = Field(..., description="Count by sentiment_class")
    period_distribution: dict = Field(..., description="Count by period")
    trip_type_distribution: dict = Field(..., description="Count by trip_type")
    reviewer_type_distribution: dict = Field(..., description="Count by reviewer_type")
