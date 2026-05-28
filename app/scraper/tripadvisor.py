# app/scraper/tripadvisor_scraper.py

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from loguru import logger

from app.models.review import Review


class TripAdvisorScraper:
    """
    Research-grade TripAdvisor scraper using unofficial API.

    Responsibilities:
    - Fetch paginated reviews
    - Store raw API responses
    - Normalize structured review data
    - Save processed datasets
    - Handle retries and failures
    """

    BASE_URL = "https://travel-data-api.omkar.cloud/travel"

    def __init__(
        self,
        api_key: str,
        query: str,
        locale: str = "en-US",
        output_dir: str = "app/storage",
        delay_range: tuple[float, float] = (0.8, 1.8),
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.query = query
        self.locale = locale
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay_range = delay_range

        self.headers = {
            "API-Key": self.api_key,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }

        self.output_dir = Path(output_dir)

        self.raw_dir = self.output_dir

        self.raw_dir.mkdir(parents=True, exist_ok=True)

        self.all_raw_pages: list[dict[str, Any]] = []

    # =========================================================
    # PUBLIC API
    # =========================================================

    def scrape(self) -> None:
        """
        Main scraping pipeline.
        """

        logger.info(f"Starting scrape for query: {self.query}")

        page = 1

        while True:
            logger.info(f"Fetching page {page}")

            data = self._fetch_page(page)

            if not data:
                logger.warning(f"No data returned for page {page}")
                break

            self.all_raw_pages.append(data)

            reviews = data.get("results", [])

            if not reviews:
                logger.info(f"No more reviews found at page {page}")
                break

            logger.info(f"Page {page}: {len(reviews)} reviews")

            page += 1

            time.sleep(0.8)

        logger.success(
            f"Scraping completed. Total pages: {len(self.all_raw_pages)}"
        )

        self._save_raw_json()

    # =========================================================
    # FETCHING
    # =========================================================

    def _fetch_page(self, page: int) -> dict[str, Any] | None:
        """
        Fetch single review page with retries.
        """

        for attempt in range(1, self.max_retries + 1):

            try:
                response = requests.get(
                    f"{self.BASE_URL}/reviews",
                    params={
                        "query": self.query,
                        "page": page,
                        "locale": self.locale,
                    },
                    headers=self.headers,
                    timeout=self.timeout,
                )

                response.raise_for_status()

                return response.json()

            except requests.RequestException as e:
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed "
                    f"for page {page}: {e}"
                )

                time.sleep(2 * attempt)

        logger.error(f"Failed to fetch page {page}")

        return None


    # =========================================================
    # STORAGE
    # =========================================================

    def _save_raw_json(self) -> None:
        """
        Save raw untouched API responses.
        """

        path = self.raw_dir / "pashupatinath_reviews_raw.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                self.all_raw_pages,
                f,
                ensure_ascii=False,
                indent=2,
            )

        logger.success(f"Saved raw JSON → {path}")
