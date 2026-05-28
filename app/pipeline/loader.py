# app/pipeline/loader.py

import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger


class DataLoader:
    """
    Load raw JSON from PHASE 1 scraping.
    
    Validates JSON structure and handles loading errors.
    """
    
    @staticmethod
    def load_json(path: Path) -> List[Dict[str, Any]]:
        """
        Load JSON array of pages from raw scraper output.
        
        Expected structure:
        [
            {
                "results": [
                    {...review},
                    {...review},
                    ...
                ],
                ...page metadata...
            },
            ...
        ]
        
        Args:
            path: Path to raw JSON file
            
        Returns:
            List of page dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If structure doesn't match expected format
        """
        
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Raw data file not found: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            raise
        
        # Validate structure
        if not isinstance(data, list):
            raise ValueError(
                f"Expected JSON array of pages, got {type(data).__name__}"
            )
        
        logger.info(f"Loaded {len(data)} pages from {path.name}")
        
        return data
