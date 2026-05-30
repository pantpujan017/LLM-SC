"""Data loading services for the social network pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger

from app.social.loaders import CSVLoader
from app.social.models.results import SocialDataBundle


class SocialDataService:
    """Load social network input tables and optional review-level data."""

    def __init__(self, data_dir: Path | str, reviews_path: Optional[Path | str] = None):
        self.data_dir = Path(data_dir)
        self.reviews_path = Path(reviews_path) if reviews_path else None

    def load(self) -> SocialDataBundle:
        loader = CSVLoader(self.data_dir)
        entities, relations, sentiments = loader.load_all()
        reviews = self._load_reviews()
        return SocialDataBundle(
            entities=entities,
            relations=relations,
            sentiments=sentiments,
            reviews=reviews,
        )

    def _load_reviews(self) -> Optional[pd.DataFrame]:
        if not self.reviews_path or not self.reviews_path.exists():
            return None
        logger.info(f"Loading review analytics data from {self.reviews_path}")
        if self.reviews_path.suffix == ".parquet":
            return pd.read_parquet(self.reviews_path)
        return pd.read_csv(self.reviews_path)

