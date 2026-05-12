"""Project config. Override here, or via env vars.

Uses Google's Gemini API via its OpenAI-compatible endpoint. Swap the
base_url and model names below to use another provider (Groq, OpenAI,
OpenRouter, Ollama, etc.).
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Worker model for curator, summarizer, commentators (fast/cheap)
MODEL = os.getenv("NEWSAGGRO_MODEL", "gemini-2.5-flash-lite")

# Editor gets a stronger pass for the final synthesis
EDITOR_MODEL = os.getenv("NEWSAGGRO_EDITOR_MODEL", "gemini-2.5-flash-lite")

# Min seconds between calls. Gemini free tier is 15 RPM, so 4s/call keeps us safe.
MIN_CALL_INTERVAL_SECONDS = float(os.getenv("NEWSAGGRO_CALL_INTERVAL", "4.5"))

# How many stories to keep after the curator
TOP_K = int(os.getenv("NEWSAGGRO_TOP_K", "5"))

# Commentator personas. Add/remove to change voices in the brief.
PERSONAS = [
    "Builder",
    "Skeptic",
    "Degen",
]

# Output directory for daily briefs
BRIEFS_DIR = os.getenv("NEWSAGGRO_BRIEFS_DIR", "briefs")

# Provider config. Default: Gemini via OpenAI-compatible endpoint.
# Other providers (uncomment + set the matching env var):
#   Groq:     base_url="https://api.groq.com/openai/v1", key=GROQ_API_KEY
#   OpenAI:   base_url=None (default), key=OPENAI_API_KEY
#   Ollama:   base_url="http://localhost:11434/v1", key="ollama"
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
