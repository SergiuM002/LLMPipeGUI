import platform
import sys
from pathlib import Path

# Record the operating system for platform-specific configuration
OPERATING_SYSTEM = platform.system()

# Use the bundled application directory when frozen; otherwise use the
# repository root relative to this file.
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent.parent))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define paths for application data and session-related files
DATA_DIR = BASE_DIR / "src" / "data"
SESSIONS_PATH = DATA_DIR / "sessions"
LASTLOGIN_FILE = DATA_DIR / "lastlogin.json"

# Ensure the data directory and default last-login file exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

if not LASTLOGIN_FILE.exists():
    LASTLOGIN_FILE.write_text("[]")