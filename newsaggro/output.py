"""Write briefs to disk."""
import os
from datetime import date
from .config import BRIEFS_DIR


def save_brief(markdown: str) -> str:
    """Write the brief to briefs/brief_YYYY-MM-DD.md and return the path."""
    os.makedirs(BRIEFS_DIR, exist_ok=True)
    today = date.today().isoformat()
    path = os.path.join(BRIEFS_DIR, f"brief_{today}.md")
    with open(path, "w") as f:
        f.write(markdown)
    return path
