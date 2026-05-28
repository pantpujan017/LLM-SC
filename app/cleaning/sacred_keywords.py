# app/cleaning/sacred_keywords.py

import re
from typing import Set, Pattern
from app.config.constants import SACRED_KEYWORDS


class SacredContentDetector:
    """
    Detect sacred/religious terminology in review text.
    
    Uses case-insensitive regex with word boundaries to identify
    sacred and religious terms relevant to Pashupatinath Temple.
    
    Expandable: Add new keywords to SACRED_KEYWORDS in constants.py
    for other sacred sites.
    """
    
    def __init__(self):
        """Initialize compiled regex pattern from constants."""
        # Escape special regex characters and join with OR
        keywords_escaped = [re.escape(k) for k in SACRED_KEYWORDS]
        pattern_str = r'\b(' + '|'.join(keywords_escaped) + r')\b'
        
        # Compile once for efficiency
        self.compiled_pattern: Pattern = re.compile(
            pattern_str,
            re.IGNORECASE | re.UNICODE
        )
    
    def has_sacred_content(self, text: str) -> bool:
        """
        Check if text contains sacred terminology.
        
        Args:
            text: Cleaned review text
            
        Returns:
            True if any sacred keyword is present, False otherwise
        """
        if not text:
            return False
        
        return bool(self.compiled_pattern.search(text))
    
    def find_matches(self, text: str) -> Set[str]:
        """
        Find all matched sacred keywords in text.
        
        Useful for analysis and debugging.
        
        Args:
            text: Cleaned review text
            
        Returns:
            Set of matched keywords (lowercased)
        """
        if not text:
            return set()
        
        matches = self.compiled_pattern.findall(text)
        return {m.lower() for m in matches}
