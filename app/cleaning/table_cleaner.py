# app/cleaning/table_cleaner.py

"""
Table Cleaner for PHASE 2.5

Implements semantic alignment and cleaning for LLM-extracted
entities, relations, and sentiments.
"""

import pandas as pd
from loguru import logger
from app.config.constants import (
    ENTITY_TYPE_FIXES,
    SENTIMENT_LABEL_FIXES,
    RELATION_TYPE_FIXES,
    VALID_ENTITY_TYPES,
    VALID_SENTIMENTS,
    VALID_RELATIONS,
)


class TableCleaner:
    """
    Cleans and aligns tabular data extracted by LLMs to 
    canonical research schemas.
    """
    
    def clean_entities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean entities table:
        - Map noisy types to canonical types
        - Normalize entity names
        - Validate final types
        """
        logger.info("Cleaning entities table...")
        df = df.copy()
        
        # 1. Map entity types
        before = len(df[~df["entity_type"].isin(VALID_ENTITY_TYPES)])
        df["entity_type"] = df["entity_type"].replace(ENTITY_TYPE_FIXES)
        after = len(df[~df["entity_type"].isin(VALID_ENTITY_TYPES)])
        logger.info(f"  Entity type violations fixed: {before} -> {after}")
        
        # 2. Normalize entity names
        df["entity_name_norm"] = df["entity_name"].str.strip().str.lower()
        
        return df
    
    def clean_sentiments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean sentiments table:
        - Map labels to positive/neutral/negative
        - Validate final labels
        """
        logger.info("Cleaning sentiments table...")
        df = df.copy()
        
        # Map sentiment labels
        before = len(df[~df["sentiment"].isin(VALID_SENTIMENTS)])
        df["sentiment"] = df["sentiment"].replace(SENTIMENT_LABEL_FIXES)
        after = len(df[~df["sentiment"].isin(VALID_SENTIMENTS)])
        logger.info(f"  Sentiment label violations fixed: {before} -> {after}")
        
        return df
    
    def clean_relations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean relations table:
        - Map relation types
        - Remove self-relations
        - Validate final relation types
        """
        logger.info("Cleaning relations table...")
        df = df.copy()
        
        # 1. Map relation types
        before = len(df[~df["relation"].isin(VALID_RELATIONS)])
        df["relation"] = df["relation"].replace(RELATION_TYPE_FIXES)
        after = len(df[~df["relation"].isin(VALID_RELATIONS)])
        logger.info(f"  Relation type violations fixed: {before} -> {after}")
        
        # 2. Remove self-relations
        before_sr = len(df)
        df = df[df["source_node"] != df["target_node"]].copy()
        logger.info(f"  Self-relations removed: {before_sr - len(df)}")
        
        return df
