import os
from pathlib import Path

from dotenv import load_dotenv

CARTELLA_PROGETTO = Path(__file__).parent
load_dotenv(CARTELLA_PROGETTO / ".env")
CARTELLA_DATI = CARTELLA_PROGETTO / "dati"
CARTELLA_DATI.mkdir(exist_ok=True)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODELLO_LLM = os.getenv("JARVIS_MODELLO", "qwen3:8b")
MODELLO_EMBEDDING = os.getenv("JARVIS_MODELLO_EMBEDDING", "nomic-embed-text")

# Cartella con le note Markdown (es. un vault Obsidian) usate dal RAG
CARTELLA_NOTE = Path(os.getenv("JARVIS_CARTELLA_NOTE", CARTELLA_PROGETTO / "note"))

# webhook n8n
N8N_WEBHOOK_URL = os.getenv("JARVIS_N8N_WEBHOOK_URL")