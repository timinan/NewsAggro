"""Project config. Override here, or via env vars.

Uses Groq's OpenAI-compatible endpoint by default. Swap the base_url
and model names to use another provider (Gemini, OpenAI, OpenRouter,
Anthropic, Ollama).
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Worker model: curator, summarizer
MODEL = os.getenv("NEWSAGGRO_MODEL", "llama-3.1-8b-instant")

# Editor model (intro / markdown synthesis)
EDITOR_MODEL = os.getenv("NEWSAGGRO_EDITOR_MODEL", "llama-3.1-8b-instant")

# How many stories to keep after the curator
TOP_K = int(os.getenv("NEWSAGGRO_TOP_K", "7"))

# Categories that MUST appear in every brief (one story each, latest by RSS order).
# Curator fills the remaining slots from any category.
REQUIRED_CATEGORIES = ["arsenal", "canada", "vancouver"]

# Output directory for daily briefs
BRIEFS_DIR = os.getenv("NEWSAGGRO_BRIEFS_DIR", "briefs")

# Min seconds between calls. Groq free tier is 30 RPM, so 2.1s/call keeps us safe.
MIN_CALL_INTERVAL_SECONDS = float(os.getenv("NEWSAGGRO_CALL_INTERVAL", "2.1"))

# Provider config. Default: Groq.
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
