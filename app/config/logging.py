# app/config/logging.py

from loguru import logger
import sys
from pathlib import Path


def setup_logger(log_file: str = "logs/pipeline.log") -> None:
    """Configure loguru for PHASE 2 pipeline."""
    
    logger.remove()  # Remove default handler
    
    # Stdout: INFO and above (colorized)
    logger.add(
        sys.stdout,
        level="INFO",
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{message}"
        ),
    )
    
    # File: DEBUG and above (detailed logging)
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_path),
        level="DEBUG",
        rotation="100 MB",
        retention="30 days",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} | {message}"
        ),
    )