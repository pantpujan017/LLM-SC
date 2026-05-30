"""Shared analyzer protocol."""

from __future__ import annotations

from typing import Protocol, TypeVar

from app.social.models.results import NetworkContext


T = TypeVar("T")


class Analyzer(Protocol[T]):
    """Common interface for independently executable analyzers."""

    name: str

    def analyze(self, context: NetworkContext) -> T:
        ...

