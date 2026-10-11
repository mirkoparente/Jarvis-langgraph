from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from multiagente import gestisci_domanda
from database_orm import crea_sessione, sessione_esistente
from logging_config import configura_logging
import logging

configura_logging()
logger = logging.getLogger(__name__)


app = FastAPI()

class DomandaInput(BaseModel):
    sessione_id:str
    messaggio: str
    
class RispostaOutput(BaseModel):
    risposta: str
    
class SessioneOutput(BaseModel):
    sessione_id: str
    
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/sessioni", response_model=SessioneOutput)
def nuova_sessione():
    sessione_id = crea_sessione()
    logger.info("sessione creata")
    return SessioneOutput(sessione_id = sessione_id)

@app.post("/ask", response_model=RispostaOutput)
def ask(domanda: DomandaInput):
    if not sessione_esistente(domanda.sessione_id):
        logger.warning(f"Sessione non trovata {domanda.sessione_id}")
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    
    if not domanda.messaggio.strip():
        logger.warning(f"il messaggio è vuoto {domanda.messaggio}" )
        raise HTTPException(status_code=400, detail="Il messaggio non puo essere vuoto")
    try:
        risposta = gestisci_domanda(domanda.sessione_id, domanda.messaggio)
        return RispostaOutput(risposta=risposta)
    except Exception as e:
        logger.error(f"Errore gestione domanda {e}",exc_info=True)
        raise HTTPException(status_code=500, detail="Errore interno del server")