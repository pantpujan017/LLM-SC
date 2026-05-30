# app/social/loaders/__init__.py

"""
PHASE 3 Data Loaders: CSV ingestion with normalization

Loads entities, relations, and sentiments from cleaned CSV files.
"""

from .csv_loader import CSVLoader

__all__ = ["CSVLoader"]
