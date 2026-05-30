# app/pipeline/table_executor.py

"""
Table Pipeline Executor for PHASE 2.5

Orchestrates the cleaning of raw tabular data (entities, relations, sentiments)
and saves them to the processed storage.
"""

from pathlib import Path
import pandas as pd
from loguru import logger

from app.cleaning.table_cleaner import TableCleaner


class TablePipelineExecutor:
    """
    Executes the table cleaning pipeline.
    
    Input: /app/storage/tables/raw/
    Output: /app/storage/tables/processed/
    """
    
    def __init__(
        self, 
        raw_dir: Path | str, 
        processed_dir: Path | str
    ):
        """Initialize executor with paths"""
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.cleaner = TableCleaner()
        
        # Ensure output directory exists
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self) -> Dict[str, int]:
        """
        Run the full table cleaning pipeline.
        
        Returns:
            Summary of processed row counts
        """
        logger.info("=" * 70)
        logger.info("PHASE 2.5: TABLE CLEANING PIPELINE")
        logger.info("=" * 70)
        
        # Define table mapping (filename -> cleaner_method)
        tables = {
            "entities_table.csv": self.cleaner.clean_entities,
            "sentiments_table.csv": self.cleaner.clean_sentiments,
            "relations_table.csv": self.cleaner.clean_relations,
        }
        
        summary = {}
        
        for filename, clean_method in tables.items():
            raw_path = self.raw_dir / filename
            processed_path = self.processed_dir / filename.replace("_table", "_clean")
            
            if not raw_path.exists():
                logger.error(f"Raw table not found: {raw_path}")
                continue
                
            logger.info(f"Processing {filename}...")
            
            # Load
            df = pd.read_csv(raw_path)
            
            # Clean
            cleaned_df = clean_method(df)
            
            # Save
            cleaned_df.to_csv(processed_path, index=False)
            
            summary[filename] = len(cleaned_df)
            logger.success(f"✓ Saved cleaned table: {processed_path}")
        
        logger.info("=" * 70)
        logger.info("TABLE CLEANING COMPLETE")
        logger.info("=" * 70)
        
        return summary
