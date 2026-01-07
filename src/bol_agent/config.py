import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Settings:
    bol_client_id: str
    bol_client_secret: str
    bol_api_base: str
    export_dir: str
    state_dir: str

def load_settings() -> Settings:
    # Load .env from the project root (current working directory)
    load_dotenv()
    return Settings(
        bol_client_id=os.environ["BOL_CLIENT_ID"],
        bol_client_secret=os.environ["BOL_CLIENT_SECRET"],
        bol_api_base=os.getenv("BOL_API_BASE", "https://api.bol.com/retailer"),
        export_dir=os.getenv("EXPORT_DIR", "./data/exports"),
        state_dir=os.getenv("STATE_DIR", "./data/state"),
    )
