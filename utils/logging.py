"""
Logging configuration for Amnesia
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def get_logger(
    name: str = "amnesia",
    level: str = "INFO",
    log_file: Optional[str] = None
):
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (used as prefix)
        level: Logging level
        log_file: Optional file path for logging
        
    Returns:
        Configured logger instance
    """
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=level,
        colorize=True,
    )
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=level,
            rotation="10 MB",
            retention="30 days",
            compression="gz",
        )
    
    return logger.bind(name=name)


# Global logger instance
log = get_logger()