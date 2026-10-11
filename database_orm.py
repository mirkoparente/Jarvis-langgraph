from model.models import Messaggio, SessionLocal, Sessione
import uuid


def crea_sessione()-> str:
    sessione_id = str(uuid.uuid4())
    
    with SessionLocal() as db:
        nuova_sessione = Sessione(id=sessione_id)
        db.add(nuova_sessione)
        db.commit()    
    return sessione_id

def sessione_esistente(sessione_id:str) -> bool:
    with SessionLocal() as db:
        risultato = db.query(Sessione).filter(Sessione.id == sessione_id).first()
    return risultato is not None

def salva_messaggi(sessione_id:str,ruolo:str,contenuto:str)-> None:
    with SessionLocal() as db:
        nuovo_messaggio = Messaggio(
            id=str(uuid.uuid4()),
            sessione_id=sessione_id,
            ruolo=ruolo,
            contenuto = contenuto
        )
        db.add(nuovo_messaggio)
        db.commit()
    
def carica_messaggi(sessione_id: str) -> list[dict]:
    with SessionLocal() as db:
        sessione = db.query(Sessione).filter(Sessione.id == sessione_id).first()
        
        if sessione is None:
            return []
        
        risultato = [{"role": m.ruolo, "content": m.contenuto} for m in sessione.messaggi]
    return risultato
