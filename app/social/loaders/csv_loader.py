# app/social/loaders/csv_loader.py

"""
CSV Data Loader for PHASE 3

Loads entities, relations, and sentiments from cleaned PHASE 2 outputs.
Handles normalization and validation.
"""

from pathlib import Path
from typing import Tuple, Dict, List
import pandas as pd
from loguru import logger

from app.social.utils.normalization import normalize_entity_name


class CSVLoader:
    """
    Loads cleaned PHASE 2 CSV files:
    - entities_clean.csv: Entity definitions (name, type, year, period, trip_type, etc.)
    - relations_clean.csv: Relation definitions (source, target, relation_type, review_id)
    - sentiments_clean.csv: Sentiment data (entity, aspect, score, sentiment, review_id)
    """
    
    def __init__(self, data_dir: Path | str):
        """
        Initialize loader with data directory.
        
        Args:
            data_dir: Path to directory containing cleaned CSV files
        """
        self.data_dir = Path(data_dir)
        self.entities_df = None
        self.relations_df = None
        self.sentiments_df = None
    
    def load_all(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load all three CSV files.
        
        Returns:
            Tuple of (entities_df, relations_df, sentiments_df)
        """
        logger.info(f"Loading PHASE 3 data from {self.data_dir}")
        
        self.entities_df = self.load_entities()
        self.relations_df = self.load_relations()
        self.sentiments_df = self.load_sentiments()
        
        logger.info(f"  Entities: {len(self.entities_df):,} rows")
        logger.info(f"  Relations: {len(self.relations_df):,} rows")
        logger.info(f"  Sentiments: {len(self.sentiments_df):,} rows")
        
        return self.entities_df, self.relations_df, self.sentiments_df
    
    def load_entities(self) -> pd.DataFrame:
        """Load entities CSV"""
        path = self.data_dir / "entities_clean.csv"
        
        if not path.exists():
            logger.error(f"Entities file not found: {path}")
            raise FileNotFoundError(f"Expected file: {path}")
        
        df = pd.read_csv(path)
        logger.debug(f"Loaded {len(df)} entity rows")
        return df
    
    def load_relations(self) -> pd.DataFrame:
        """Load relations CSV"""
        path = self.data_dir / "relations_clean.csv"
        
        if not path.exists():
            logger.error(f"Relations file not found: {path}")
            raise FileNotFoundError(f"Expected file: {path}")
        
        df = pd.read_csv(path)
        logger.debug(f"Loaded {len(df)} relation rows")
        return df
    
    def load_sentiments(self) -> pd.DataFrame:
        """Load sentiments CSV"""
        path = self.data_dir / "sentiments_clean.csv"
        
        if not path.exists():
            logger.error(f"Sentiments file not found: {path}")
            raise FileNotFoundError(f"Expected file: {path}")
        
        df = pd.read_csv(path)
        logger.debug(f"Loaded {len(df)} sentiment rows")
        return df
    
    @staticmethod
    def normalize_entity_name(name: str) -> str:
        """
        Normalize entity name: lowercase + strip whitespace.
        
        Used for deduplication at concept-level.
        """
        return normalize_entity_name(name)
