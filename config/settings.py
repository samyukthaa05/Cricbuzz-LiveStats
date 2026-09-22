"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
# Check both project root and workspace parent for .env
if (ROOT_DIR / ".env").exists():
    load_dotenv(ROOT_DIR / ".env")
elif (ROOT_DIR.parent / ".env").exists():
    load_dotenv(ROOT_DIR.parent / ".env")
else:
    load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_key: str = os.getenv("CRICBUZZ_API_KEY", "")
    api_host: str = os.getenv("CRICBUZZ_API_HOST", "") or "cricbuzz-cricket.p.rapidapi.com"
    api_base_url: str = os.getenv("CRICBUZZ_API_BASE_URL", "https://cricbuzz-cricket.p.rapidapi.com")
    timeout_seconds: int = int(os.getenv("CRICBUZZ_TIMEOUT_SECONDS", "10"))
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/cricbuzz_livestats.db"))
    verify_ssl: bool = os.getenv("CRICBUZZ_VERIFY_SSL", "true").lower() in ("true", "1", "yes")

    def resolved_database_path(self) -> Path:
        path = self.database_path
        return path if path.is_absolute() else ROOT_DIR / path


settings = Settings()