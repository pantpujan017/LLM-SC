# tests/test_cleaning.py

import pytest
from app.cleaning.text_cleaning import TextCleaner
from app.cleaning.sacred_keywords import SacredContentDetector


class TestTextCleaner:
    """Test text cleaning with preservation of sacred/multilingual content."""
    
    @pytest.fixture
    def cleaner(self):
        return TextCleaner()
    
    def test_clean_preserves_sacred_terms(self, cleaner):
        """Sacred keywords should survive cleaning."""
        text = "I felt a darshan of Shiva at the ghat"
        cleaned = cleaner.clean(text)
        
        assert "darshan" in cleaned.lower()
        assert "shiva" in cleaned.lower()
        assert "ghat" in cleaned.lower()
    
    def test_clean_lowercase_conversion(self, cleaner):
        """Text should be converted to lowercase."""
        text = "AMAZING Divine Energy and HOLY Temple"
        cleaned = cleaner.clean(text)
        
        assert cleaned == cleaned.lower()
    
    def test_clean_removes_excessive_punctuation(self, cleaner):
        """Multiple consecutive punctuation should collapse."""
        text = "Amazing!!! Really??? This is great..."
        cleaned = cleaner.clean(text)
        
        assert "!!!" not in cleaned
        assert "???" not in cleaned
        assert "..." not in cleaned
        assert cleaned == "amazing! really? this is great."
    
    def test_clean_normalizes_whitespace(self, cleaner):
        """Multiple spaces and newlines should collapse to single space."""
        text = "This is  a\n\ntest with\t\ttabs"
        cleaned = cleaner.clean(text)
        
        assert "  " not in cleaned
        assert "\n" not in cleaned
        assert cleaned == "this is a test with tabs"
    
    def test_clean_removes_html_entities(self, cleaner):
        """HTML entities should be unescaped."""
        text = "She said &quot;Amazing!&quot; and I said &apos;Yes&apos;"
        cleaned = cleaner.clean(text)
        
        assert "&quot;" not in cleaned
        assert "&apos;" not in cleaned
        assert '"' in cleaned
        assert "'" in cleaned
    
    def test_clean_handles_none_input(self, cleaner):
        """None input should return empty string."""
        assert cleaner.clean(None) == ""
    
    def test_clean_handles_empty_string(self, cleaner):
        """Empty string should return empty string."""
        assert cleaner.clean("") == ""
    
    def test_word_count_accurate(self, cleaner):
        """Word count should match token split."""
        text = "This is a test review text"
        count = cleaner.word_count(text)
        
        assert count == 6
    
    def test_word_count_handles_empty(self, cleaner):
        """Empty text should have zero word count."""
        assert cleaner.word_count("") == 0
    
    def test_preserves_urls_as_is(self, cleaner):
        """URLs should be preserved in output."""
        text = "Check out https://www.tripadvisor.com for more"
        cleaned = cleaner.clean(text)
        
        # URL structure preserved (protocol and domain still visible)
        assert "https" in cleaned or "www" in cleaned
    
    def test_preserves_nepali_transliterations(self, cleaner):
        """Nepali transliterations should be preserved."""
        # Unicode combining marks that represent Nepali diacritics
        text = "Kathmandu Valley and Bagmati River"
        cleaned = cleaner.clean(text)
        
        # Key location names preserved
        assert "kathmandu" in cleaned
        assert "bagmati" in cleaned


class TestSacredContentDetector:
    """Test sacred keyword detection."""
    
    @pytest.fixture
    def detector(self):
        return SacredContentDetector()
    
    def test_detects_single_sacred_keyword(self, detector):
        """Should detect reviews with sacred content."""
        assert detector.has_sacred_content("Amazing aarti ceremony") is True
    
    def test_detects_multiple_sacred_keywords(self, detector):
        """Should detect multiple sacred keywords."""
        text = "Darshan of Shiva at the ghat with holy rituals"
        assert detector.has_sacred_content(text) is True
    
    def test_no_sacred_content_found(self, detector):
        """Should return False for non-sacred content."""
        assert detector.has_sacred_content("Nice view and good food") is False
    
    def test_case_insensitive_detection(self, detector):
        """Detection should be case-insensitive."""
        assert detector.has_sacred_content("DARSHAN OF SHIVA") is True
        assert detector.has_sacred_content("Darshan of Shiva") is True
        assert detector.has_sacred_content("darshan of shiva") is True
    
    def test_word_boundary_matching(self, detector):
        """Should use word boundaries, not substring matching."""
        # "tem" in "temple" should match, but "te" alone should not
        assert detector.has_sacred_content("temple is sacred") is True
        assert detector.has_sacred_content("Item was nice") is False
    
    def test_find_matches_returns_set(self, detector):
        """find_matches should return set of matched keywords."""
        text = "Darshan of Shiva at the ghat"
        matches = detector.find_matches(text)
        
        assert isinstance(matches, set)
        assert "darshan" in matches
        assert "shiva" in matches
        assert "ghat" in matches
    
    def test_find_matches_empty_on_no_content(self, detector):
        """Should return empty set for text without sacred content."""
        matches = detector.find_matches("Nice place to visit")
        assert matches == set()
    
    def test_handles_none_input(self, detector):
        """Should handle None input gracefully."""
        assert detector.has_sacred_content(None) is False
        assert detector.find_matches(None) == set()
    
    def test_detects_ganga_aarti(self, detector):
        """Should detect multi-word sacred terms."""
        # "ganga aarti" is in the keywords list
        assert detector.has_sacred_content("We attended the ganga aarti") is True
    
    def test_detects_pashupatinath_specific_terms(self, detector):
        """Should detect Pashupatinath-specific keywords."""
        sacred_terms = ["pashupatinath", "bagmati", "cremation", "funeral"]
        for term in sacred_terms:
            assert detector.has_sacred_content(f"Visit {term}") is True
