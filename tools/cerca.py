from config import CARTELLA_NOTE
from rag.ricerca_ibrida import cerca_ibrida


def cerca_nelle_note(domanda:str)->str:
    risultati=cerca_ibrida(domanda, CARTELLA_NOTE)
    
    if not risultati:
        return "NESSUN RISULTATO PERTINENTE TROVATO nelle note. Non inventare o suggerire contenuto: comunica chiaramente all'utente che non hai trovato nulla di specifico su questo argomento nelle sue note."
    
    output="Ecco le informazioni più rilevanti trovate nelle note:\n"
    
    for r in risultati:
        output+=f"Dalla nota '{r['titolo_nota']}': \n {r['testo']}\n\n"
        
    return output


