"""Aspect-level sentiment summaries for story-map reporting."""

from __future__ import annotations

from typing import Dict

import pandas as pd
from loguru import logger

from app.social.config.constants import (
    ASPECT_INTERPRETATIONS,
    ORIGINAL_SENTIMENT_ASPECTS,
    SACRED_SENTIMENT_ASPECTS,
    SENTIMENT_ASPECTS,
)


class AspectSentimentAnalyzer:
    """Summarize sentiment by visitor-experience aspect."""

    name = "aspect_sentiment"

    def __init__(self, sentiments_df: pd.DataFrame):
        self.sentiments_df = sentiments_df

    def analyze(self) -> Dict[str, Dict]:
        logger.info("Computing aspect-level sentiment intelligence...")
        rows: Dict[str, Dict] = {}
        for aspect in SENTIMENT_ASPECTS:
            aspect_df = self.sentiments_df[self.sentiments_df["aspect"] == aspect]
            count = len(aspect_df)
            positive = int((aspect_df["sentiment"] == "positive").sum()) if count else 0
            negative = int((aspect_df["sentiment"] == "negative").sum()) if count else 0
            avg_score = float(aspect_df["score"].mean()) if count else 0.0
            rows[aspect] = {
                "aspect": aspect,
                "label": aspect.replace("_", " ").title(),
                "count": count,
                "positive_pct": (positive / count * 100) if count else 0.0,
                "negative_pct": (negative / count * 100) if count else 0.0,
                "avg_score": avg_score,
                "type": self._aspect_type(aspect),
                "interpretation": ASPECT_INTERPRETATIONS.get(aspect, SENTIMENT_ASPECTS.get(aspect, "")),
            }
        return rows

    @staticmethod
    def _aspect_type(aspect: str) -> str:
        if aspect in SACRED_SENTIMENT_ASPECTS:
            return "Sacred"
        if aspect in ORIGINAL_SENTIMENT_ASPECTS:
            return "Original"
        return "Other"

