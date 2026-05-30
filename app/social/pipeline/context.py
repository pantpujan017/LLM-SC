"""Pipeline context aliases for backwards-compatible imports."""

from app.social.models.results import (
    AdvancedAnalysisResults,
    CoreAnalysisResults,
    NetworkContext,
    PipelineResult,
    SocialDataBundle,
)

__all__ = [
    "SocialDataBundle",
    "NetworkContext",
    "CoreAnalysisResults",
    "AdvancedAnalysisResults",
    "PipelineResult",
]

