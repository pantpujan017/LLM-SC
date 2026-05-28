# app/main.py

from dotenv import load_dotenv
from loguru import logger
import os
import sys
from pathlib import Path

from app.config.logging import setup_logger
from app.scraper.tripadvisor import TripAdvisorScraper
from app.pipeline.executor import PipelineExecutor

load_dotenv()


def main() -> None:
    """
    Main entry point for PHASE 1 (scraping) or PHASE 2 (cleaning).
    
    Mode selection:
    - PIPELINE_MODE=scrape: Run TripAdvisor scraper (PHASE 1)
    - PIPELINE_MODE=clean: Run data cleaning pipeline (PHASE 2)
    
    Default: clean (PHASE 2)
    """
    
    # Setup logging
    setup_logger()
    
    # Get mode from environment, default to 'clean'
    mode = os.getenv("PIPELINE_MODE", "clean").lower()
    
    logger.info(f"Starting pipeline in '{mode}' mode")
    
    if mode == "scrape":
        # ============================================================
        # PHASE 1: SCRAPING
        # ============================================================
        _run_scraper()
    
    elif mode == "clean":
        # ============================================================
        # PHASE 2: CLEANING & STRUCTURING
        # ============================================================
        _run_cleaner()
    
    else:
        logger.error(f"Unknown mode: {mode}")
        logger.info("Valid modes: 'scrape' or 'clean'")
        sys.exit(1)


def _run_scraper() -> None:
    """Run PHASE 1: TripAdvisor scraping."""
    
    logger.info("PHASE 1: TripAdvisor Review Scraping")
    
    api_key = os.getenv("TRAVEL_API_KEY")
    
    if not api_key:
        logger.error("TRAVEL_API_KEY not found in .env")
        sys.exit(1)
    
    try:
        scraper = TripAdvisorScraper(
            api_key=api_key,
            query="Pashupatinath Temple",
        )
        
        scraper.scrape()
        logger.success("PHASE 1: Scraping completed successfully")
    
    except Exception as e:
        logger.error(f"PHASE 1 failed: {e}", exc_info=True)
        sys.exit(1)


def _run_cleaner() -> None:
    """Run PHASE 2: Data cleaning and structuring."""
    
    logger.info("PHASE 2: Data Cleaning & Dataset Structuring")
    
    raw_path = Path("app/storage/pashupatinath_reviews_raw.json")
    output_dir = Path("app/storage/processed")
    
    # Validate raw data exists
    if not raw_path.exists():
        logger.error(f"Raw data not found: {raw_path}")
        logger.info("Run PHASE 1 first: PIPELINE_MODE=scrape python -m app.main")
        sys.exit(1)
    
    try:
        executor = PipelineExecutor(
            raw_json_path=raw_path,
            output_dir=output_dir
        )
        
        metadata = executor.execute()
        
        logger.success("\nPIPELINE SUCCESS")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Files created:")
        logger.info(f"  - pashupatinath_reviews_clean.csv")
        logger.info(f"  - pashupatinath_reviews_clean.parquet")
        logger.info(f"  - pipeline_metadata.json")
    
    except Exception as e:
        logger.error(f"PHASE 2 failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
