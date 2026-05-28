# app/pipeline/executor.py

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger
import time

from app.models.dataset import CleanedReview, DatasetMetadata
from app.pipeline.loader import DataLoader
from app.pipeline.flattener import ReviewFlattener
from app.pipeline.engineer import FeatureEngineer
from app.pipeline.exporter import DatasetExporter
from app.cleaning.validators import DatasetValidator
from app.config.constants import PIPELINE_VERSION


class PipelineExecutor:
    """
    Orchestrates the complete PHASE 2 data cleaning pipeline.
    
    Flow:
    1. Load raw JSON from PHASE 1
    2. Flatten paginated structure
    3. Engineer features for research
    4. Deduplicate by review_id
    5. Validate dataset schema
    6. Export to CSV/Parquet/Metadata
    
    Fully idempotent: same input always produces identical output
    (except execution_timestamp).
    """
    
    def __init__(self, raw_json_path: Path, output_dir: Path):
        """
        Initialize pipeline.
        
        Args:
            raw_json_path: Path to raw JSON from PHASE 1
            output_dir: Directory for cleaned dataset outputs
        """
        self.raw_json_path = Path(raw_json_path)
        self.output_dir = Path(output_dir)
        
        # Initialize submodules
        self.loader = DataLoader()
        self.flattener = ReviewFlattener()
        self.engineer = FeatureEngineer()
        self.exporter = DatasetExporter(output_dir=self.output_dir)
        self.validator = DatasetValidator()
    
    def execute(self) -> Dict[str, Any]:
        """
        Run full PHASE 2 pipeline.
        
        Returns:
            Metadata dictionary with execution statistics
        """
        
        start_time = time.time()
        logger.info("=" * 60)
        logger.info("PHASE 2: Data Cleaning & Dataset Structuring")
        logger.info("=" * 60)
        
        try:
            # ============================================================
            # STEP 1: LOAD RAW JSON
            # ============================================================
            logger.info("\n[1/5] Loading raw JSON...")
            raw_pages = self.loader.load_json(self.raw_json_path)
            
            total_raw = sum(len(p.get("results", [])) for p in raw_pages)
            logger.info(f"    Loaded {len(raw_pages)} pages")
            logger.info(f"    Total raw reviews: {total_raw}")
            
            # ============================================================
            # STEP 2: FLATTEN NESTED STRUCTURE
            # ============================================================
            logger.info("\n[2/5] Flattening paginated structure...")
            flat_reviews = self.flattener.flatten(raw_pages)
            logger.info(f"    Flattened reviews: {len(flat_reviews)}")
            
            # ============================================================
            # STEP 3: FEATURE ENGINEERING
            # ============================================================
            logger.info("\n[3/5] Engineering features...")
            cleaned_reviews = self.engineer.process_batch(flat_reviews)
            logger.info(f"    Engineered reviews: {len(cleaned_reviews)}")
            
            # ============================================================
            # STEP 4: DEDUPLICATION
            # ============================================================
            logger.info("\n[4/5] Deduplicating by review_id...")
            unique_reviews, dup_count = self._deduplicate(cleaned_reviews)
            logger.info(f"    Unique reviews: {len(unique_reviews)}")
            logger.info(f"    Duplicates removed: {dup_count}")
            
            # ============================================================
            # STEP 5: VALIDATION
            # ============================================================
            logger.info("\n[5/5] Validating schema...")
            valid_reviews, failed_count = self.validator.validate_batch(unique_reviews)
            logger.info(f"    Valid reviews: {len(valid_reviews)}")
            logger.info(f"    Failed validation: {failed_count}")
            
            # ============================================================
            # EXPORT
            # ============================================================
            logger.info("\nExporting to CSV/Parquet/Metadata...")
            self.exporter.export(valid_reviews)
            
            # ============================================================
            # METADATA
            # ============================================================
            elapsed = time.time() - start_time
            metadata = self._compute_metadata(
                total_raw=total_raw,
                total_cleaned=len(valid_reviews),
                duplicates_found=dup_count,
                failed_validations=failed_count,
                execution_time=elapsed,
                reviews=valid_reviews
            )
            self.exporter.export_metadata(metadata)
            
            # ============================================================
            # SUMMARY
            # ============================================================
            logger.info("\n" + "=" * 60)
            logger.success(f"PHASE 2 COMPLETE in {elapsed:.2f}s")
            logger.info("=" * 60)
            logger.info(f"Raw reviews:        {total_raw:,}")
            logger.info(f"Cleaned reviews:    {len(valid_reviews):,}")
            logger.info(f"Sacred content:     {metadata['sacred_content_count']:,}")
            logger.info(f"Sentiment dist:     {metadata['sentiment_distribution']}")
            logger.info("=" * 60 + "\n")
            
            return metadata
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _deduplicate(reviews: List[CleanedReview]) -> tuple[List[CleanedReview], int]:
        """
        Keep-first deduplication by review_id.
        
        Preserves original ordering, removes subsequent occurrences.
        
        Args:
            reviews: List of CleanedReview objects
            
        Returns:
            Tuple of (unique_reviews, duplicate_count)
        """
        seen = set()
        unique = []
        duplicates = 0
        
        for review in reviews:
            if review.review_id not in seen:
                seen.add(review.review_id)
                unique.append(review)
            else:
                duplicates += 1
        
        return unique, duplicates
    
    @staticmethod
    def _compute_metadata(
        total_raw: int,
        total_cleaned: int,
        duplicates_found: int,
        failed_validations: int,
        execution_time: float,
        reviews: List[CleanedReview]
    ) -> Dict[str, Any]:
        """
        Compute comprehensive pipeline execution metadata.
        
        Args:
            total_raw: Raw reviews from JSON
            total_cleaned: After all processing
            duplicates_found: Removed by deduplication
            failed_validations: Failed schema validation
            execution_time: Pipeline runtime in seconds
            reviews: Final validated reviews
            
        Returns:
            Metadata dictionary
        """
        
        # Distribution by sentiment
        sentiment_dist = {}
        for sentiment in ["positive", "neutral", "negative"]:
            sentiment_dist[sentiment] = sum(
                1 for r in reviews if r.sentiment_class == sentiment
            )
        
        # Distribution by period
        period_dist = PipelineExecutor._count_by_field(reviews, "period")
        
        # Distribution by trip type
        trip_type_dist = PipelineExecutor._count_by_field(reviews, "trip_type")
        
        # Distribution by reviewer type
        reviewer_type_dist = PipelineExecutor._count_by_field(reviews, "reviewer_type")
        
        return {
            "total_raw_reviews": total_raw,
            "total_cleaned_reviews": total_cleaned,
            "duplicates_found": duplicates_found,
            "failed_validations": failed_validations,
            "processing_time_seconds": round(execution_time, 2),
            "pipeline_version": PIPELINE_VERSION,
            "execution_timestamp": datetime.utcnow().isoformat() + "Z",
            "sacred_content_count": sum(1 for r in reviews if r.has_sacred_content),
            "sentiment_distribution": sentiment_dist,
            "period_distribution": period_dist,
            "trip_type_distribution": trip_type_dist,
            "reviewer_type_distribution": reviewer_type_dist,
        }
    
    @staticmethod
    def _count_by_field(reviews: List[CleanedReview], field: str) -> Dict[str, int]:
        """
        Count reviews grouped by field value.
        
        Args:
            reviews: List of CleanedReview objects
            field: Field name to group by
            
        Returns:
            Dictionary of {value: count}
        """
        counts = {}
        for review in reviews:
            val = getattr(review, field)
            counts[val] = counts.get(val, 0) + 1
        return counts
