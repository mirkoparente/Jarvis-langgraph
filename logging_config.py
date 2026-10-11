import logging
from config import CARTELLA_PROGETTO

def configura_logging() -> None:
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler(CARTELLA_PROGETTO / "jarvis.log", encoding="utf-8")
        ]

    )
    # Le richieste HTTP verso Ollama sporcano la chat: mostra solo avvisi ed errori
    logging.getLogger("httpx").setLevel(logging.WARNING)