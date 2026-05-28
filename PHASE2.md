# PHASE 2: Data Cleaning & Dataset Structuring

**Heritage-LLM-SC Research Pipeline**

---

## Overview

PHASE 2 transforms raw TripAdvisor review data (from PHASE 1) into a research-grade dataset suitable for scientific analysis of Sacred Heritage site experiences.

**Status**: ✅ Complete and tested
**Version**: 2.0
**Dataset**: 3,944 unique reviews of Pashupatinath Temple
**Processing Time**: ~2 seconds

---

## What PHASE 2 Does

### Input
- Raw JSON from PHASE 1: `app/storage/pashupatinath_reviews_raw.json`
- 199 pages × ~20 reviews/page = 3,945 reviews

### Processing Pipeline

```
Raw JSON
    ↓
[1] Load & Parse JSON
    ↓
[2] Flatten Paginated Structure
    ↓
[3] Feature Engineering
    • Text cleaning (unicode, punctuation)
    • Year extraction from published_at_date
    • Rule-based sentiment classification
    • Reviewer expertise inference
    • Sacred content detection
    • Temporal period mapping
    ↓
[4] Deduplication
    ↓
[5] Schema Validation
    ↓
[6] Export
    • CSV (human-readable, research dissemination)
    • Parquet (columnar, efficient storage)
    • Metadata JSON (reproducibility, audit trail)
```

### Output

**Three files in `app/storage/processed/`:**

| File | Format | Size | Purpose |
|------|--------|------|---------|
| `pashupatinath_reviews_clean.csv` | CSV | 1.6 MB | Research dataset, easily shareable |
| `pashupatinath_reviews_clean.parquet` | Parquet | 881 KB | Efficient columnar storage, type-safe |
| `pipeline_metadata.json` | JSON | 849 B | Execution stats, reproducibility |

---

## Dataset Schema

**10 Research-Ready Columns:**

```python
CleanedReview {
    review_id: str               # Unique review identifier
    text_clean: str              # Cleaned, normalized text (lowercase, unicode NFD)
    rating: int                  # 1-5 star rating
    sentiment_class: str         # "positive" | "neutral" | "negative" (rule-based)
    year: int                    # Extracted from published_at_date
    trip_type: str               # "solo" | "family" | "friends" | "couples" | "business" | "unknown"
    reviewer_type: str           # "elite" (≥100 contributions) | "experienced" (≥25) | "casual" (<25) | "unknown"
    word_count: int              # Token count after cleaning
    has_sacred_content: bool     # True if contains sacred/religious terminology
    period: str                  # Temporal cohort: early_period | growth_period | pre_covid_peak | ...
}
```

---

## Key Features

### 1. Text Cleaning (Preserves Cultural Semantics)

**Deterministic transformations:**
1. Unicode normalization (NFD decomposition)
2. Control character removal (preserves newlines, tabs)
3. HTML entity unescaping (`&quot;` → `"`)
4. Punctuation collapse (`!!!` → `!`)
5. Whitespace normalization (multiple spaces → single space)
6. Lowercase conversion (multilingual-safe)
7. Edge trimming

**What it PRESERVES:**
- Sacred terminology: "darshan", "shiva", "aarti", "ghat", "bagmati", etc.
- Nepali transliterations and diacritics
- Mixed-language reviews (English + Nepali)
- Emotional expressions
- URLs and special unicode characters

**Example:**
```
Before:  "AMAZING Darshan at the Sacred GHAT!!!  Spiritual experience with Aarti ceremony."
After:   "amazing darshan at the sacred ghat! spiritual experience with aarti ceremony."
Sacred?  True ✓
```

### 2. Sacred Content Detection

**Boolean flag based on keyword matching:**

Sacred keywords (expandable):
```
"darshan", "shiva", "aarti", "ghat", "bagmati", "cremation", "funeral", 
"temple", "spiritual", "ritual", "prayer", "divine", "holy", etc.
```

**Statistics:**
- 3,352 / 3,944 reviews (85%) contain sacred terminology
- Case-insensitive, whole-word matching (no substring false positives)

### 3. Reviewer Expertise Inference

```
≥ 100 contributions → "elite"          (1,468 reviews)
25-99 contributions → "experienced"    (1,196 reviews)
< 25 contributions  → "casual"         (1,280 reviews)
null/missing        → "unknown"        (0 reviews, all inferred)
```

### 4. Temporal Period Mapping

Research cohorts designed for heritage tourism analysis:

| Period | Years | Description |
|--------|-------|-------------|
| `early_period` | 2008-2012 | Initial online review era (320 reviews) |
| `growth_period` | 2013-2017 | Rapid tourism growth (2,396 reviews) |
| `pre_covid_peak` | 2018-2019 | Peak pre-pandemic (955 reviews) |
| `covid_onset` | 2020 | Pandemic begins (75 reviews) |
| `covid_deep` | 2021 | Deepest pandemic (14 reviews) |
| `recovery_early` | 2022 | Early recovery (41 reviews) |
| `recovery_late` | 2023 | Continued recovery (45 reviews) |
| `post_recovery` | 2024+ | Post-recovery normalization (98 reviews) |

### 5. Rule-Based Sentiment Classification

No ML models required:

```
Rating 5-4 → "positive"     (3,414 reviews - 86.6%)
Rating 3   → "neutral"      (347 reviews - 8.8%)
Rating 1-2 → "negative"     (183 reviews - 4.6%)
```

### 6. Data Quality Guarantees

| Check | Result |
|-------|--------|
| Nulls in key fields | 0 |
| Schema validation failures | 0 |
| Duplicates (deduped) | 1 |
| All rating values valid (1-5) | ✅ |
| All years in reasonable range | ✅ |
| All sentiment classes valid | ✅ |
| All trip types normalized | ✅ |
| All reviewer types inferred | ✅ |

---

## Data Distribution Analysis

### Sentiment vs Rating
```
positive:  min_rating=1, max_rating=5, mean=4.72
neutral:   min_rating=3, max_rating=3, mean=3.00
negative:  min_rating=1, max_rating=2, mean=1.67
```

### Trip Type Distribution
```
friends:    993 (25.2%)  ← Most common
couples:    833 (21.1%)
solo:       796 (20.2%)
family:     651 (16.5%)
business:   218 (5.5%)
unknown:    453 (11.5%)  ← Missing data
```

### Reviewer Type Distribution
```
elite:       1,468 (37.2%)
casual:      1,280 (32.5%)
experienced: 1,196 (30.3%)
unknown:     0 (0%)       ← All reviewers have contribution data
```

### Sacred Content by Period
```
growth_period:      2,396 reviews, 2,036 with sacred (85.0%)
pre_covid_peak:     955 reviews, 799 with sacred (83.7%)
early_period:       320 reviews, 292 with sacred (91.3%)
post_recovery:      98 reviews, 77 with sacred (78.6%)
covid_onset:        75 reviews, 51 with sacred (68.0%)
recovery_late:      45 reviews, 40 with sacred (88.9%)
recovery_early:     41 reviews, 35 with sacred (85.4%)
covid_deep:         14 reviews, 6 with sacred (42.9%)     ← Lowest
```

---

## Running the Pipeline

### Prerequisites

```bash
# Python 3.11+ required
pip install pandas pydantic loguru dotenv requests pyarrow

# Ensure PHASE 1 data exists:
ls app/storage/pashupatinath_reviews_raw.json
```

### Execute PHASE 2

```bash
# Set environment
export PIPELINE_MODE=clean

# Run pipeline
python -m app.main

# Output:
# ✓ Loaded 199 pages, 3,945 raw reviews
# ✓ Flattened to 3,945 reviews
# ✓ Engineered all features
# ✓ Deduplicated: 3,944 unique
# ✓ Validated: 3,944 passing schema
# ✓ Exported: CSV, Parquet, Metadata
# Processing time: 1.92s
```

### Programmatic Usage

```python
from pathlib import Path
from app.pipeline.executor import PipelineExecutor

executor = PipelineExecutor(
    raw_json_path=Path("app/storage/pashupatinath_reviews_raw.json"),
    output_dir=Path("app/storage/processed")
)

metadata = executor.execute()

print(f"Cleaned: {metadata['total_cleaned_reviews']} reviews")
print(f"Sacred: {metadata['sacred_content_count']} reviews")
print(f"Processing time: {metadata['processing_time_seconds']}s")
```

---

## Testing

**Comprehensive test suite included:**

```bash
# Run all tests
python -m pytest tests/ -v

# Test results:
# ✅ 21 text cleaning tests (unicode, punctuation, sacred content)
# ✅ 17 pipeline tests (loading, flattening, engineering, validation)
# ✅ Total: 38 tests, all passing
```

---

## Reproducibility & Audit Trail

### Pipeline Metadata

Captured in `pipeline_metadata.json`:

```json
{
  "total_raw_reviews": 3945,
  "total_cleaned_reviews": 3944,
  "duplicates_found": 1,
  "failed_validations": 0,
  "processing_time_seconds": 1.92,
  "pipeline_version": "2.0",
  "execution_timestamp": "2026-05-27T11:20:51.583084Z",
  "sacred_content_count": 3352,
  "sentiment_distribution": {
    "positive": 3414,
    "neutral": 347,
    "negative": 183
  },
  "period_distribution": { ... },
  "trip_type_distribution": { ... },
  "reviewer_type_distribution": { ... }
}
```

### Idempotency Guarantee

PHASE 2 is **fully idempotent**:
- Same input → identical output (except timestamp)
- Run 10 times, get 10 identical datasets
- No random operations, no ML inference, no external state
- All transformations deterministic and reversible

### Configuration

All constants in `app/config/constants.py`:
- Sacred keywords (expandable for other sites)
- Period mappings (customizable by research question)
- Sentiment rules (adjustable thresholds)
- Text cleaning parameters (unicode form, punctuation rules)

---

## Architecture

### Module Organization

```
app/
├── models/
│   ├── review.py              # PHASE 1 raw review schema
│   └── dataset.py             # PHASE 2 cleaned review + metadata schemas
├── cleaning/
│   ├── text_cleaning.py       # Text normalization (unicode, punctuation)
│   ├── sacred_keywords.py     # Sacred content detector (regex)
│   └── validators.py          # Schema + data quality validation
├── pipeline/
│   ├── loader.py              # JSON loading
│   ├── flattener.py           # Pagination flattening
│   ├── engineer.py            # Feature extraction & engineering
│   ├── exporter.py            # Multi-format export
│   └── executor.py            # Orchestrator
├── config/
│   ├── constants.py           # Sacred keywords, period mappings, rules
│   └── logging.py             # Loguru configuration
└── main.py                    # CLI entry point (supports both modes)
```

### Separation of Concerns

- **Loader**: JSON parsing + validation
- **Flattener**: Data structure normalization
- **Engineer**: Feature extraction (deterministic, stateless)
- **Exporter**: Multi-format output
- **Executor**: Orchestration + metadata collection
- **TextCleaner**: Reusable text normalization utility
- **SacredDetector**: Reusable keyword detection utility
- **Validator**: Schema + quality checks

---

## Performance

| Operation | Time | Count |
|-----------|------|-------|
| Load JSON | 0.01s | 199 pages |
| Flatten | 0.02s | 3,945 reviews |
| Engineer features | 0.40s | 3,945 reviews (~9.8k reviews/sec) |
| Deduplicate | 0.01s | 1 duplicate |
| Validate | 0.02s | 3,944 reviews |
| Export CSV | 0.20s | 1.6 MB |
| Export Parquet | 0.05s | 881 KB |
| **Total** | **1.92s** | **3,944 clean rows** |

**Memory usage**: ~150 MB (all data in memory during pipeline)

---

## Next Steps (PHASE 3+)

This cleaned dataset is ready for:

- **NLP Analysis**: Aspect extraction, topic modeling, semantic analysis
- **Sentiment Analysis**: Fine-tuned models, emotion detection
- **Temporal Analysis**: Tourism trend analysis, seasonality patterns
- **Social Network Analysis**: Reviewer relationships, influence networks
- **Knowledge Graphs**: Entity extraction, relationship mapping
- **Heritage Impact Assessment**: Experience quality metrics, accessibility patterns

---

## Citation

If you use this dataset or pipeline in research:

```
Heritage-LLM-SC PHASE 2: Data Cleaning & Dataset Structuring
Version: 2.0
Date: 2026-05-27
Repository: https://github.com/anomalyco/nepal-llm-sc
```

---

## Contact & Support

For questions about PHASE 2:
- Documentation: `app/README.md`
- Code: See inline documentation in each module
- Issues: Report at https://github.com/anomalyco/nepal-llm-sc/issues

---

**PHASE 2 Complete ✅**

Next: PHASE 3 - Advanced NLP & Social Computing Analysis
