import json
from pathlib import Path

from config.environment import SESSIONS_PATH


def save_session_info(hostname: str, username: str, session_info: dict):
    """Create or update one session record in the user's sessions file."""
    SAVE_PATH = SESSIONS_PATH / hostname / username / "sessions.json"
    
    # Persist only relevant fields
    wanted_info = ["name", "sequence_count", "sequence_progress", "progress", "finished"]
    clean_info = {k: v for k, v in session_info.items() if k in wanted_info} 
    
    try:
        with open(SAVE_PATH, "r") as f:
            saved_sessions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Treat missing or invalid session storage as an empty list.
        saved_sessions = []
        
    replaced = False
    for i, session in enumerate(saved_sessions):
        if session.get("name") == clean_info.get("name"):
            saved_sessions[i] = clean_info
            replaced = True
            break
        
    if not replaced:
        saved_sessions.append(clean_info)
        
    Path(SAVE_PATH).parent.mkdir(parents=True, exist_ok=True)
        
    with open(SAVE_PATH, "w") as f:
        json.dump(saved_sessions, f, indent=4)


def save_sessions_info(hostname: str, username: str, sessions_info: list):
    """Replace the user's stored session records with the supplied records."""
    SAVE_PATH = SESSIONS_PATH / hostname / username / "sessions.json"
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Exclude unwanted fields before writing session data to disk
    wanted_info = {"name", "sequence_count", "sequence_progress", "progress", "finished"}
    clean_sessions = [
        {key: value for key, value in session_info.items() if key in wanted_info}
        for session_info in sessions_info
    ]

    with open(SAVE_PATH, "w") as f:
        json.dump(clean_sessions, f, indent=4)
        
def load_sessions_info(hostname: str, username: str):
    """Load a user's sessions and annotate each record with its server and user."""
    SAVE_PATH = SESSIONS_PATH / hostname / username / "sessions.json"
    
    try:
        with open(SAVE_PATH, "r") as f:
            saved_sessions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Initialize absent or invalid session storage as an empty JSON array
        Path(SAVE_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(SAVE_PATH, "w") as f:
            json.dump([], f)
            saved_sessions = []
            
    for i in range(len(saved_sessions)):
        saved_sessions[i]["server"] = hostname
        saved_sessions[i]["user"] = username
        
    return saved_sessions


def load_all_sessions_info():
    """Load session records for every server and user under the sessions path."""
    sessions_info = []

    if not SESSIONS_PATH.is_dir():
        return sessions_info

    for hostname_path in SESSIONS_PATH.iterdir():
        if not hostname_path.is_dir():
            continue

        for username_path in hostname_path.iterdir():
            if not username_path.is_dir():
                continue

            sessions_path = username_path / "sessions.json"
            if not sessions_path.is_file():
                continue

            for session_info in load_sessions_info(hostname_path.name, username_path.name):
                session_info["server"] = hostname_path.name
                session_info["user"] = username_path.name
                sessions_info.append(session_info)

    return sessions_info

def delete_session(hostname: str, username: str, session_name: str):
    """Remove a named session from the user's stored session records."""
    SAVE_PATH = SESSIONS_PATH / hostname / username / "sessions.json"
    
    if not Path(SAVE_PATH).exists():
        raise FileNotFoundError
    
    sessions = load_sessions_info(hostname, username)
    
    deleted = False
    for session in sessions:
        if session["name"] == session_name:
            sessions.remove(session)
            deleted = True
            
    if not deleted:
        raise RuntimeError
            
    with open(SAVE_PATH, "w") as f:
        json.dump(sessions, f, indent=4)
        
