import requests
from config import N8N_WEBHOOK_URL
import logging

logger = logging.getLogger(__name__)


def webhook(messaggio: str) -> str:
    n8n = requests.post(N8N_WEBHOOK_URL,json={"messaggio": messaggio}, timeout=60)
    logger.info(f"Risposta da n8n: {n8n}")
    res = n8n.json()
    return f"Ho categorizzato il messaggio in: {res.get('categoria')} con urgenza: {res.get('urgenza')}. \n {res.get('risposta_suggerita')}"