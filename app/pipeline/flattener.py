# app/pipeline/flattener.py

from typing import List, Dict, Any
from loguru import logger


class ReviewFlattener:
    """
    Flatten paginated API responses into individual reviews.
    
    Extracts reviews from nested 'results' key in each page.
    Preserves all original fields from API response.
    """
    
    @staticmethod
    def flatten(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract individual reviews from paginated pages.
        
        Args:
            pages: List of page dictionaries from API
            
        Returns:
            List of individual review dictionaries
        """
        
        flat_reviews = []
        skipped = 0
        
        for page_idx, page in enumerate(pages):
            if not isinstance(page, dict):
                logger.warning(f"Page {page_idx}: expected dict, got {type(page).__name__}")
                skipped += 1
                continue
            
            results = page.get("results", [])
            
            if not isinstance(results, list):
                logger.warning(
                    f"Page {page_idx}: 'results' not a list, got {type(results).__name__}"
                )
                skipped += 1
                continue
            
            for review in results:
                if isinstance(review, dict):
                    flat_reviews.append(review)
        
        logger.info(
            f"Flattened {len(flat_reviews)} reviews from {len(pages)} pages "
            f"({skipped} pages skipped)"
        )
        
        return flat_reviews
