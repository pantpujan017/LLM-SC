# app/cleaning/text_cleaning.py

import re
import unicodedata
from typing import Optional
from app.config.constants import UNICODE_NORM_FORM, HTML_ENTITIES, PUNCTUATION_COLLAPSE_RULES


class TextCleaner:
    """
    Text cleaning utility preserving sacred/multilingual content.
    
    Applies deterministic transformations:
    1. Unicode normalization (NFD decomposition)
    2. Control character removal
    3. Whitespace normalization
    4. HTML entity unescaping
    5. Excessive punctuation collapse
    6. Lowercase conversion
    7. Edge trimming
    
    PRESERVES:
    - Sacred terminology (darshan, shiva, etc.)
    - Nepali transliterations (ṁ, ñ, etc.)
    - Mixed-language reviews
    - Emotional expressions
    - URLs and special characters
    """
    
    @staticmethod
    def clean(text: Optional[str]) -> str:
        """
        Clean review text while preserving cultural semantics.
        
        Args:
            text: Raw review text
            
        Returns:
            Cleaned, normalized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # 1. Unicode normalization (NFD = decomposed form)
        # Decomposition separates base characters from combining marks
        text = unicodedata.normalize(UNICODE_NORM_FORM, text)
        
        # 2. Remove control characters but preserve newlines temporarily
        # Control characters have category C* (Cc, Cf, Cs, Co, Cn)
        text = ''.join(
            c if (unicodedata.category(c)[0] != 'C' or c in '\n\r\t')
            else ''
            for c in text
        )
        
        # 3. Unescape HTML entities
        for entity, replacement in HTML_ENTITIES.items():
            text = text.replace(entity, replacement)
        
        # 4. Collapse excessive punctuation patterns
        for pattern, replacement in PUNCTUATION_COLLAPSE_RULES.items():
            text = re.sub(pattern, replacement, text)
        
        # 5. Collapse multiple whitespace/newlines to single space
        text = re.sub(r'\s+', ' ', text)
        
        # 6. Lowercase (preserves unicode letters for multilingual support)
        text = text.lower()
        
        # 7. Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def word_count(text: str) -> int:
        """
        Count tokens (space-separated words).
        
        Args:
            text: Cleaned text
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(text.split())
