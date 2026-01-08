import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir: str = "./logs") -> logging.Logger:
    """
    Configure structured logging for the application.

    Args:
        log_dir: Directory where log files will be stored

    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("bol_agent")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # File handler - detailed logs
    log_file = log_path / f"bol_agent_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler - important messages only
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
