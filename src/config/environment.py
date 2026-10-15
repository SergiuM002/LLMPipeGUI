import platform
import sys
from pathlib import Path

OPERATING_SYSTEM = platform.system()

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent.parent))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "src" / "data"
SESSIONS_PATH = DATA_DIR / "sessions"
LASTLOGIN_FILE = DATA_DIR / "lastlogin.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

if not LASTLOGIN_FILE.exists():
    LASTLOGIN_FILE.write_text("[]")