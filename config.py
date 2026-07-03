import os
from dotenv import load_dotenv

# Toggle for prefilled demo data in UI
DEMO_PREFILL = True

def load_env(env_file: str = "apikey.env") -> None:
    """Load environment variables from a local env file."""
    load_dotenv(env_file)


def get_env_variable(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)