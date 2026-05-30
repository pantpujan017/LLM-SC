# app/main.py

from dotenv import load_dotenv
from loguru import logger
import os
import sys
from pathlib import Path

from app.config.logging import setup_logger
from app.scraper.tripadvisor import TripAdvisorScraper
from app.pipeline.executor import PipelineExecutor
from app.pipeline.table_executor import TablePipelineExecutor
from app.social.pipeline import Phase3Pipeline

load_dotenv()


def main() -> None:
    """
    Main entry point for PHASE 1 (scraping), PHASE 2 (cleaning), PHASE 2.5 (table cleaning), or PHASE 3 (social computing).
    
    Mode selection:
    - PIPELINE_MODE=scrape: Run TripAdvisor scraper (PHASE 1)
    - PIPELINE_MODE=clean: Run data cleaning pipeline (PHASE 2)
    - PIPELINE_MODE=clean_tables: Run table cleaning pipeline (PHASE 2.5)
    - PIPELINE_MODE=social: Run social network computing (PHASE 3)
    
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
    
    elif mode == "clean_tables":
        # ============================================================
        # PHASE 2.5: TABLE CLEANING
        # ============================================================
        _run_table_cleaner()
    
    elif mode == "social":
        # ============================================================
        # PHASE 3: SOCIAL NETWORK COMPUTING
        # ============================================================
        _run_social_computing()
    
    elif mode == "dashboard":
        # ============================================================
        # HIN EXPERIENCE DASHBOARD
        # ============================================================
        _run_dashboard()
    
    else:
        logger.error(f"Unknown mode: {mode}")
        logger.info("Valid modes: 'scrape', 'clean', 'clean_tables', 'social', or 'dashboard'")
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


def _run_social_computing() -> None:
    """Run PHASE 3: Social Network Computing."""
    
    logger.info("PHASE 3: Social Network Computing")
    
    # Input: cleaned PHASE 2.5 tables
    data_dir = Path("app/storage/tables/processed")
    output_dir = Path("app/storage/social_network_output")
    
    # Validate cleaned tables exist
    required_files = [
        data_dir / "entities_clean.csv",
        data_dir / "relations_clean.csv",
        data_dir / "sentiments_clean.csv",
    ]
    
    for required_file in required_files:
        if not required_file.exists():
            logger.error(f"Required file not found: {required_file}")
            logger.info("Run PHASE 2.5 first: PIPELINE_MODE=clean_tables python -m app.main")
            sys.exit(1)
    
    try:
        # Execute PHASE 3 pipeline
        pipeline = Phase3Pipeline(data_dir=data_dir, output_dir=output_dir)
        results = pipeline.execute()
        
        logger.success("\nPHASE 3: COMPLETE")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Files created:")
        logger.info(f"  - network.graphml (for Gephi/Cytoscape)")
        logger.info(f"  - network_metrics.json (comprehensive metrics)")
        logger.info(f"  - node_data.json (detailed node attributes)")
        logger.info(f"  - PHASE3_REPORT.md (markdown report)")
        logger.info(f"  - graph_explorer.html (interactive graph explorer)")
    
    except Exception as e:
        logger.error(f"PHASE 3 failed: {e}", exc_info=True)
        sys.exit(1)

def _run_table_cleaner() -> None:
    """Run PHASE 2.5: Table Cleaning."""
    
    logger.info("PHASE 2.5: Table Cleaning & Semantic Alignment")
    
    raw_dir = Path("app/storage/tables/raw")
    processed_dir = Path("app/storage/tables/processed")
    
    # Validate raw data exists
    required_files = [
        raw_dir / "entities_table.csv",
        raw_dir / "relations_table.csv",
        raw_dir / "sentiments_table.csv",
    ]
    
    for required_file in required_files:
        if not required_file.exists():
            logger.error(f"Raw table not found: {required_file}")
            sys.exit(1)
    
    try:
        executor = TablePipelineExecutor(
            raw_dir=raw_dir,
            processed_dir=processed_dir
        )
        summary = executor.execute()
        
        logger.success("\nTABLE CLEANING SUCCESS")
        logger.info(f"Processed tables saved to: {processed_dir}")
        for table, count in summary.items():
            logger.info(f"  - {table}: {count:,} rows")
            
    except Exception as e:
        logger.error(f"PHASE 2.5 failed: {e}", exc_info=True)
        sys.exit(1)


def _run_dashboard() -> None:
    """Launch the HIN Experience Dashboard."""
    logger.info("Launching HIN Experience Dashboard...")
    logger.info(f"Executing: {sys.executable} -m streamlit run app/social/dashboard.py")
    
    # Use sys.executable to ensure streamlit runs in the current virtual environment
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app/social/dashboard.py"], check=True)
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")
        sys.exit(1)




if __name__ == "__main__":
    main()
