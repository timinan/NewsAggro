"""Write briefs to disk in Markdown and HTML."""
import os
from datetime import date
from .config import BRIEFS_DIR


def save_brief(markdown: str) -> str:
    """Write the Markdown brief to briefs/brief_YYYY-MM-DD.md."""
    os.makedirs(BRIEFS_DIR, exist_ok=True)
    today = date.today().isoformat()
    path = os.path.join(BRIEFS_DIR, f"brief_{today}.md")
    with open(path, "w") as f:
        f.write(markdown)
    return path


def save_brief_html(html: str) -> tuple[str, str]:
    """Write the HTML brief to briefs/brief_YYYY-MM-DD.html and update
    briefs/index.html to point at the latest."""
    os.makedirs(BRIEFS_DIR, exist_ok=True)
    today = date.today().isoformat()
    dated_path = os.path.join(BRIEFS_DIR, f"brief_{today}.html")
    index_path = os.path.join(BRIEFS_DIR, "index.html")
    with open(dated_path, "w") as f:
        f.write(html)
    with open(index_path, "w") as f:
        f.write(html)
    return dated_path, index_path
