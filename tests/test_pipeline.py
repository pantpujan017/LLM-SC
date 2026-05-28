# tests/test_pipeline.py

import pytest
from pathlib import Path
import json
import tempfile
from app.pipeline.loader import DataLoader
from app.pipeline.flattener import ReviewFlattener
from app.pipeline.engineer import FeatureEngineer
from app.models.dataset import CleanedReview


class TestDataLoader:
    """Test JSON loading functionality."""
    
    def test_load_valid_json(self):
        """Should load valid JSON array."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = [
                {"results": [{"review_id": "1"}]},
                {"results": [{"review_id": "2"}]},
            ]
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            loader = DataLoader()
            data = loader.load_json(Path(temp_path))
            
            assert len(data) == 2
            assert data[0]["results"][0]["review_id"] == "1"
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_file(self):
        """Should raise FileNotFoundError for missing file."""
        loader = DataLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_json(Path("/nonexistent/path.json"))
    
    def test_load_invalid_json(self):
        """Should raise JSONDecodeError for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            loader = DataLoader()
            with pytest.raises(json.JSONDecodeError):
                loader.load_json(Path(temp_path))
        finally:
            Path(temp_path).unlink()
    
    def test_load_non_array_json(self):
        """Should raise ValueError if JSON is not an array."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"not": "an array"}, f)
            temp_path = f.name
        
        try:
            loader = DataLoader()
            with pytest.raises(ValueError):
                loader.load_json(Path(temp_path))
        finally:
            Path(temp_path).unlink()


class TestReviewFlattener:
    """Test review flattening logic."""
    
    def test_flatten_single_page(self):
        """Should flatten single page correctly."""
        pages = [
            {
                "results": [
                    {"review_id": "1", "text": "Great place"},
                    {"review_id": "2", "text": "Amazing"},
                ]
            }
        ]
        
        flattener = ReviewFlattener()
        flat = flattener.flatten(pages)
        
        assert len(flat) == 2
        assert flat[0]["review_id"] == "1"
        assert flat[1]["review_id"] == "2"
    
    def test_flatten_multiple_pages(self):
        """Should flatten multiple pages."""
        pages = [
            {"results": [{"review_id": "1"}]},
            {"results": [{"review_id": "2"}, {"review_id": "3"}]},
            {"results": []},
        ]
        
        flattener = ReviewFlattener()
        flat = flattener.flatten(pages)
        
        assert len(flat) == 3
    
    def test_flatten_handles_missing_results(self):
        """Should handle pages without 'results' key."""
        pages = [
            {"results": [{"review_id": "1"}]},
            {"no_results": "key"},
        ]
        
        flattener = ReviewFlattener()
        flat = flattener.flatten(pages)
        
        assert len(flat) == 1


class TestFeatureEngineer:
    """Test feature engineering."""
    
    @pytest.fixture
    def engineer(self):
        return FeatureEngineer()
    
    def test_extract_rating_valid(self, engineer):
        """Should extract valid rating."""
        review = {"rating": 4}
        rating = engineer._extract_rating(review)
        
        assert rating == 4
    
    def test_extract_rating_invalid_defaults(self, engineer):
        """Should default to 3 for invalid ratings."""
        assert engineer._extract_rating({"rating": 6}) == 3
        assert engineer._extract_rating({"rating": 0}) == 3
        assert engineer._extract_rating({"rating": None}) == 3
        assert engineer._extract_rating({}) == 3
    
    def test_extract_year_from_iso_date(self, engineer):
        """Should extract year from ISO date."""
        year = engineer._extract_year("2026-04-16")
        assert year == 2026
    
    def test_extract_year_invalid_defaults(self, engineer):
        """Should default to 2024 for invalid dates."""
        assert engineer._extract_year(None) == 2024
        assert engineer._extract_year("invalid-date") == 2024
        assert engineer._extract_year("") == 2024
    
    def test_classify_sentiment(self, engineer):
        """Should classify sentiment based on rating."""
        assert engineer._classify_sentiment(5) == "positive"
        assert engineer._classify_sentiment(4) == "positive"
        assert engineer._classify_sentiment(3) == "neutral"
        assert engineer._classify_sentiment(2) == "negative"
        assert engineer._classify_sentiment(1) == "negative"
    
    def test_normalize_trip_type(self, engineer):
        """Should normalize trip types."""
        assert engineer._normalize_trip_type("solo") == "solo"
        assert engineer._normalize_trip_type("family") == "family"
        assert engineer._normalize_trip_type("couples") == "couples"
        assert engineer._normalize_trip_type(None) == "unknown"
        assert engineer._normalize_trip_type("unknown_type") == "unknown"
    
    def test_infer_reviewer_type(self, engineer):
        """Should infer reviewer type from contributions."""
        assert engineer._infer_reviewer_type(150) == "elite"
        assert engineer._infer_reviewer_type(100) == "elite"
        assert engineer._infer_reviewer_type(50) == "experienced"
        assert engineer._infer_reviewer_type(25) == "experienced"
        assert engineer._infer_reviewer_type(10) == "casual"
        assert engineer._infer_reviewer_type(0) == "casual"
        assert engineer._infer_reviewer_type(None) == "unknown"
    
    def test_map_period(self, engineer):
        """Should map year to period cohort."""
        assert engineer._map_period(2010) == "early_period"
        assert engineer._map_period(2015) == "growth_period"
        assert engineer._map_period(2019) == "pre_covid_peak"
        assert engineer._map_period(2020) == "covid_onset"
        assert engineer._map_period(2021) == "covid_deep"
        assert engineer._map_period(2022) == "recovery_early"
        assert engineer._map_period(2023) == "recovery_late"
        assert engineer._map_period(2025) == "post_recovery"
    
    def test_process_single_review(self, engineer):
        """Should process single review into CleanedReview."""
        raw_review = {
            "review_id": "123",
            "text": "Amazing darshan at the temple aarti ceremony",
            "rating": 5,
            "published_at_date": "2023-06-15",
            "trip": {"trip_type": "solo"},
            "reviewer": {"contribution_count": 150},
        }
        
        cleaned = engineer._process_single(raw_review)
        
        assert isinstance(cleaned, CleanedReview)
        assert cleaned.review_id == "123"
        assert cleaned.rating == 5
        assert cleaned.sentiment_class == "positive"
        assert cleaned.year == 2023
        assert cleaned.trip_type == "solo"
        assert cleaned.reviewer_type == "elite"
        assert cleaned.has_sacred_content is True
        assert cleaned.period == "recovery_late"
        assert cleaned.word_count > 0
    
    def test_process_batch(self, engineer):
        """Should process batch of reviews."""
        reviews = [
            {
                "review_id": "1",
                "text": "Great",
                "rating": 5,
                "published_at_date": "2023-01-01",
                "trip": {},
                "reviewer": {},
            },
            {
                "review_id": "2",
                "text": "Okay",
                "rating": 3,
                "published_at_date": "2023-01-02",
                "trip": {},
                "reviewer": {},
            },
        ]
        
        cleaned = engineer.process_batch(reviews)
        
        assert len(cleaned) == 2
        assert all(isinstance(r, CleanedReview) for r in cleaned)
