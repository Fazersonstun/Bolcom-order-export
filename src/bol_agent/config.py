import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class Settings:
    """Application configuration settings."""
    bol_client_id: str
    bol_client_secret: str
    bol_api_base: str
    export_dir: str
    state_dir: str
    log_dir: str

def load_settings() -> Settings:
    """
    Load application settings from environment variables.

    Validates that all required credentials are present.

    Returns:
        Settings instance with validated configuration

    Raises:
        ValueError: If required environment variables are missing
    """
    # Load .env from the project root (current working directory)
    load_dotenv()

    # Validate required credentials
    required_vars = {
        "BOL_CLIENT_ID": os.getenv("BOL_CLIENT_ID"),
        "BOL_CLIENT_SECRET": os.getenv("BOL_CLIENT_SECRET"),
    }

    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Log configuration (without sensitive data)
    logger.info("Configuration loaded successfully")
    logger.debug(f"API Base: {os.getenv('BOL_API_BASE', 'https://api.bol.com/retailer')}")

    return Settings(
        bol_client_id=required_vars["BOL_CLIENT_ID"],
        bol_client_secret=required_vars["BOL_CLIENT_SECRET"],
        bol_api_base=os.getenv("BOL_API_BASE", "https://api.bol.com/retailer"),
        export_dir=os.getenv("EXPORT_DIR", "./data/exports"),
        state_dir=os.getenv("STATE_DIR", "./data/state"),
        log_dir=os.getenv("LOG_DIR", "./logs"),
    )
