# app/pipeline/exporter.py

import json
from pathlib import Path
from typing import List
from loguru import logger
import pandas as pd

from app.models.dataset import CleanedReview


class DatasetExporter:
    """
    Export cleaned reviews to multiple formats.
    
    Outputs:
    - CSV: Human-readable, research dissemination
    - Parquet: Efficient columnar storage, fast querying
    - Metadata JSON: Pipeline reproducibility and statistics
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize exporter.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, reviews: List[CleanedReview]) -> None:
        """
        Export cleaned reviews to CSV and Parquet.
        
        Args:
            reviews: List of CleanedReview objects
        """
        
        if not reviews:
            logger.warning("No reviews to export")
            return
        
        # Convert to DataFrame
        data = [r.model_dump() for r in reviews]
        df = pd.DataFrame(data)
        
        # Ensure correct column order for research consistency
        column_order = [
            "review_id",
            "text_clean",
            "rating",
            "sentiment_class",
            "year",
            "trip_type",
            "reviewer_type",
            "word_count",
            "has_sacred_content",
            "period",
        ]
        df = df[column_order]
        
        # ============================================================
        # CSV EXPORT
        # ============================================================
        csv_path = self.output_dir / "pashupatinath_reviews_clean.csv"
        df.to_csv(
            csv_path,
            index=False,
            encoding='utf-8'
        )
        logger.success(f"Exported CSV ({len(df)} rows) → {csv_path}")
        
        # ============================================================
        # PARQUET EXPORT (efficient columnar format)
        # ============================================================
        parquet_path = self.output_dir / "pashupatinath_reviews_clean.parquet"
        df.to_parquet(
            parquet_path,
            index=False,
            compression='snappy',
            engine='pyarrow'
        )
        logger.success(f"Exported Parquet ({len(df)} rows) → {parquet_path}")
    
    def export_metadata(self, metadata: dict) -> None:
        """
        Export pipeline metadata for reproducibility.
        
        Args:
            metadata: Dictionary with execution statistics
        """
        
        meta_path = self.output_dir / "pipeline_metadata.json"
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(
                metadata,
                f,
                indent=2,
                ensure_ascii=False
            )
        
        logger.success(f"Exported metadata → {meta_path}")
