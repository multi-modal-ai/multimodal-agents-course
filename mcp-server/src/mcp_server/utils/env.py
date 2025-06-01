import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def load_env_file(env_file: Optional[str] = None) -> None:
    """Load environment variables from a .env file.

    Args:
        env_file: Optional path to the .env file. If not provided, will look for .env in:
            1. Current working directory
            2. Project root directory (2 levels up from this file)
    """
    if env_file is None:
        # Try current directory first
        if os.path.exists(".env"):
            load_dotenv(".env")
            return

        # Try project root (2 levels up from this file)
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            return

        raise FileNotFoundError(
            "No .env file found in current directory or project root. "
            "Please create a .env file with your environment variables."
        )
    else:
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Specified .env file not found: {env_file}")
        load_dotenv(env_file)
