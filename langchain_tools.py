from langchain_core.tools import tool
from tools import aggiungi_a_nota,apri_sito,crea_nota,leggi_nota,ottieni_meteo,ottieni_ora_corrente,cerca_nelle_note,webhook
from tools.browser import PROGRAMMI_CONSENTITI, apri_programma

@tool 
def ora_corrente()->str:
    """Restituisce l'ora corrente del sistema"""
    return ottieni_ora_corrente()


@tool
def meteo_attuale(citta:str)->str:
    """Ottiene il meteo attuale di una città specificata
    Args:
        citta:il nome della città di cui vuoi sapere il meteo
    """
    return ottieni_meteo(citta)

@tool
def apri(cosa: str) -> str:
    """Apre un programma sul computer O un sito web, in base a cosa viene richiesto.
    Se 'cosa' è il nome di un programma noto (chrome, notepad, calcolatrice, vscode, explorer), 
    apre quel programma. Altrimenti, se è un URL o un sito, apre quello nel browser.
    
    Args:
        cosa: nome di un programma (es. 'chrome') oppure un URL completo (es. 'https://google.com')
    """
    if cosa.strip().lower() in PROGRAMMI_CONSENTITI:
        return apri_programma(cosa)
    return apri_sito(cosa)

@tool
def scrivi_nota(titolo: str, contenuto: str, sovrascrivi: bool = False) -> str:
    """Scrive contenuto in una nota. Se 'sovrascrivi' è True, sostituisce completamente 
    il contenuto esistente (usa questo per creare una nota nuova o rifarla da zero). 
    Se False (default), aggiunge il contenuto in fondo alla nota esistente senza cancellare nulla.
    
    Args:
        titolo: titolo della nota
        contenuto: testo da scrivere/aggiungere
        sovrascrivi: True per creare/sostituire, False per aggiungere (default)
    """
    if sovrascrivi:
        return crea_nota(titolo, contenuto)
    return aggiungi_a_nota(titolo, contenuto)


@tool
def leggi_la_nota(titolo:str)->str:
    """Leggi la nota con il titolo specificato. se non esiste di non esiste nessuna nota con il titolo indicato
    Args:
        titolo: titolo della nota da leggere
    """
    return leggi_nota(titolo)


@tool
def cerca_note(domanda:str)->str:
    """Cerca informazioni nelle note personali dell'utente su qualsiasi argomento:
    appunti tecnici, progetti, idee, task, promemoria. Usa SEMPRE questo strumento
    quando l'utente fa una domanda che potrebbe essere documentata nelle sue note.
    
    Args:
        domanda: la domanda o argomento da cercare nelle note
    """
    return cerca_nelle_note(domanda)

@tool
def nessuna_azione_disponibile()->str:
    """Chiama SOLO questo strumento se nessuna delle altre azioni disponibili (meteo, ora, apri sito, note) può soddisfare la richiesta dell'utente."""
    return "NESSUNA_AZIONE_DISPONIBILE"


@tool
def n8n(messaggio:str):
    """Classifica il messaggio di un cliente di un'azienda di energia, mobile e internet
    e restituisce categoria (fatturazione, guasto, cambio_offerta, altro), urgenza e una risposta suggerita.
    Usalo quando l'utente chiede di classificare, analizzare o rispondere al messaggio/reclamo di un cliente.

    Args:
        messaggio: il testo del messaggio del cliente, riportato così com'è
    """
    return webhook(messaggio)

strumenti=[meteo_attuale,ora_corrente,scrivi_nota,leggi_la_nota,cerca_note,nessuna_azione_disponibile,apri, n8n]