"""Repository resources resolve independently of the caller's working directory."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = PROJECT_ROOT / 'DB'
