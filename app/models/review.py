# app/models/review.py

from __future__ import annotations

from pydantic import BaseModel, Field


class Review(BaseModel):
    """Raw review model from PHASE 1 scraping."""
    
    review_id: str
    title: str
    text: str
    rating: int | None = None
    published_date: str | None = None
    username: str | None = None
    user_location: str | None = None
    contributions: int | None = None
    trip_type: str | None = None
    language: str | None = None
    source: str