# PHASE 2: Quick Start Guide

## One-Command Execution

### Run the Pipeline

```bash
# Navigate to project
cd /Users/aash/codehub/nepal-llm-sc

# Activate virtual environment
source .venv/bin/activate

# Run PHASE 2 cleaning
export PIPELINE_MODE=clean
python -m app.main
```

### Expected Output

```
2026-05-27 17:05:49 | INFO | Starting pipeline in 'clean' mode
2026-05-27 17:05:49 | INFO | PHASE 2: Data Cleaning & Dataset Structuring
2026-05-27 17:05:49 | INFO | ============================================================

[1/5] Loading raw JSON...
   Loaded 199 pages
   Total raw reviews: 3,945

[2/5] Flattening paginated structure...
   Flattened reviews: 3,945

[3/5] Engineering features...
   Engineered reviews: 3,945

[4/5] Deduplicating by review_id...
   Unique reviews: 3,944
   Duplicates removed: 1

[5/5] Validating schema...
   Valid reviews: 3,944
   Failed validation: 0

Exporting to CSV/Parquet/Metadata...
✓ Exported CSV (3944 rows) → app/storage/processed/pashupatinath_reviews_clean.csv
✓ Exported Parquet (3944 rows) → app/storage/processed/pashupatinath_reviews_clean.parquet
✓ Exported metadata → app/storage/processed/pipeline_metadata.json

============================================================
✓ PHASE 2 COMPLETE in 1.92s
============================================================
Raw reviews:        3,945
Cleaned reviews:    3,944
Sacred content:     3,352 (85.0%)
Sentiment dist:     {'positive': 3414, 'neutral': 347, 'negative': 183}
============================================================

✓ PIPELINE SUCCESS
Output directory: app/storage/processed
Files created:
  - pashupatinath_reviews_clean.csv
  - pashupatinath_reviews_clean.parquet
  - pipeline_metadata.json
```

---

## Verify Output Files

```bash
# Check files exist
ls -lh app/storage/processed/

# Output:
# -rw-r--r-- 1 aash staff  1.6M pashupatinath_reviews_clean.csv
# -rw-r--r-- 1 aash staff  881K pashupatinath_reviews_clean.parquet
# -rw-r--r-- 1 aash staff  849B pipeline_metadata.json
```

---

## Quick Data Inspection

### View CSV

```bash
# First 5 rows
head -5 app/storage/processed/pashupatinath_reviews_clean.csv

# Count total rows
wc -l app/storage/processed/pashupatinath_reviews_clean.csv

# View with columns
cut -d',' -f1,2,3,4,5,6 app/storage/processed/pashupatinath_reviews_clean.csv | head -3
```

### Python Inspection

```python
import pandas as pd
import json

# Load CSV
df = pd.read_csv("app/storage/processed/pashupatinath_reviews_clean.csv")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Sacred content: {df['has_sacred_content'].sum()} / {len(df)}")

# Load metadata
with open("app/storage/processed/pipeline_metadata.json") as f:
    meta = json.load(f)
    print(f"Processing time: {meta['processing_time_seconds']}s")
    print(f"Duplicates: {meta['duplicates_found']}")

# Sample reviews
print(df[['review_id', 'text_clean', 'sentiment_class', 'period']].head(3))
```

---

## Run Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_cleaning.py -v

# Specific test
python -m pytest tests/test_cleaning.py::TestTextCleaner::test_clean_preserves_sacred_terms -v
```

---

## Dataset Schema

The cleaned CSV has **10 columns**:

| # | Column | Type | Example | Notes |
|---|--------|------|---------|-------|
| 1 | review_id | int | 1056790466 | Unique identifier |
| 2 | text_clean | str | "pashupatinath temple..." | Cleaned, normalized text |
| 3 | rating | int | 5 | 1-5 star rating |
| 4 | sentiment_class | str | "positive" | Rule-based from rating |
| 5 | year | int | 2026 | Extracted from published_at_date |
| 6 | trip_type | str | "solo" | solo/family/friends/couples/business/unknown |
| 7 | reviewer_type | str | "elite" | elite/experienced/casual/unknown |
| 8 | word_count | int | 96 | Tokens after cleaning |
| 9 | has_sacred_content | bool | true | Contains sacred terminology |
| 10 | period | str | "post_recovery" | Temporal cohort |

---

## Key Statistics

```
Total Reviews:       3,944
Raw Reviews:         3,945
Duplicates Removed:  1

Sentiment Distribution:
  Positive (4-5 stars):  3,414 (86.6%)
  Neutral (3 stars):     347 (8.8%)
  Negative (1-2 stars):  183 (4.6%)

Sacred Content:      3,352 (85.0%)

Trip Type:
  Friends:  993 (25.2%)
  Couples:  833 (21.1%)
  Solo:     796 (20.2%)
  Family:   651 (16.5%)
  Business: 218 (5.5%)
  Unknown:  453 (11.5%)

Reviewer Type:
  Elite:       1,468 (37.2%)
  Casual:      1,280 (32.5%)
  Experienced: 1,196 (30.3%)

Temporal Period:
  Growth (2013-2017):    2,396 (60.8%)
  Pre-COVID (2018-2019): 955 (24.2%)
  Early (2008-2012):     320 (8.1%)
  Post-Recovery (2024+): 98 (2.5%)
  COVID Recovery:        129 (3.3%)
  COVID Period:          89 (2.3%)
```

---

## Use Cases

### Research Analysis

```python
# Load dataset
df = pd.read_csv("app/storage/processed/pashupatinath_reviews_clean.csv")

# 1. Sentiment over time
df.groupby('year')['sentiment_class'].value_counts()

# 2. Sacred content analysis
sacred = df[df['has_sacred_content'] == True]
print(f"Sacred reviews average rating: {sacred['rating'].mean():.2f}")

# 3. Reviewer expertise pattern
df.groupby('reviewer_type')['rating'].mean()

# 4. Trip type impact
df.groupby('trip_type')['sentiment_class'].value_counts()

# 5. Temporal trends
df.groupby('period')['word_count'].mean()
```

### Export to Different Formats

```python
import pandas as pd

df = pd.read_csv("app/storage/processed/pashupatinath_reviews_clean.csv")

# To Excel
df.to_excel("pashupatinath_reviews_clean.xlsx", index=False)

# To JSON
df.to_json("pashupatinath_reviews_clean.json", orient='records')

# To SQL
import sqlite3
conn = sqlite3.connect('reviews.db')
df.to_sql('reviews', conn, if_exists='replace', index=False)

# Filter subset
sacred = df[df['has_sacred_content'] == True]
sacred.to_csv("sacred_reviews.csv", index=False)
```

---

## Troubleshooting

### Raw Data Not Found

```
Error: Raw data not found: app/storage/pashupatinath_reviews_raw.json
```

**Solution**: Run PHASE 1 first
```bash
export PIPELINE_MODE=scrape
python -m app.main
```

### Virtual Environment Not Activated

```bash
# Activate venv
source .venv/bin/activate

# You should see (.venv) in terminal prompt
```

### Import Errors

```bash
# Ensure all dependencies installed
pip install pydantic pandas loguru python-dotenv requests pyarrow

# Check venv packages
pip list
```

### Permission Issues

```bash
# Make script executable
chmod +x app/main.py

# Or run with python directly
python app/main.py
```

---

## Pipeline Architecture

```
Raw JSON (3,945 reviews)
    ↓
DataLoader → Validate JSON structure
    ↓
ReviewFlattener → Extract from nested 'results'
    ↓
FeatureEngineer → Clean text, extract features
    ├── TextCleaner (unicode normalization)
    ├── SacredContentDetector (keyword matching)
    └── Feature extraction (year, sentiment, etc.)
    ↓
Deduplicator → Keep-first by review_id
    ↓
DatasetValidator → Schema + value range checks
    ↓
DatasetExporter → Three output formats
    ├── CSV (1.6 MB)
    ├── Parquet (881 KB)
    └── Metadata JSON (849 B)
    ↓
Research-Ready Dataset (3,944 rows × 10 columns)
```

---

## Next Steps

1. **Explore the data**
   ```python
   import pandas as pd
   df = pd.read_csv("app/storage/processed/pashupatinath_reviews_clean.csv")
   df.head()
   df.describe()
   df.info()
   ```

2. **Analyze sacred content**
   ```python
   sacred = df[df['has_sacred_content']]
   print(f"Sacred reviews: {len(sacred)}")
   print(f"Average rating: {sacred['rating'].mean():.2f}")
   ```

3. **Temporal analysis**
   ```python
   df.groupby('period')['rating'].mean().plot()
   ```

4. **Prepare for PHASE 3 (NLP analysis)**
   - Topic modeling
   - Aspect extraction
   - Sentiment analysis
   - Entity recognition

---

## Support

- **Documentation**: See `PHASE2.md` and `IMPLEMENTATION.md`
- **Code**: All modules in `app/` with inline documentation
- **Tests**: Run `pytest tests/ -v`
- **Issues**: Check inline comments in source code

---

**Ready to analyze! 🚀**
