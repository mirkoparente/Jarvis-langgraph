from config import CARTELLA_DATI

percorso_note = CARTELLA_DATI


def titolo_sicuro(titolo: str) -> bool:
    caratteri_ammessi = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ ")
    return len(titolo) > 0 and all(carattere in caratteri_ammessi for carattere in titolo)


def crea_nota(titolo: str, contenuto: str) -> str:
    if not titolo_sicuro(titolo):
        return f"Titolo non valido: '{titolo}'. Usa solo lettere, numeri, spazi e underscore."
    
    with open(percorso_note / f"{titolo}.txt", "w", encoding="utf-8") as file:
        file.write(contenuto + "\n")
    return f"Nota '{titolo}' creata con: {contenuto}"


def aggiungi_a_nota(titolo: str, contenuto: str) -> str:
    if not titolo_sicuro(titolo):
        return f"Titolo non valido: '{titolo}'. Usa solo lettere, numeri, spazi e underscore."
    
    with open(percorso_note / f"{titolo}.txt", "a", encoding="utf-8") as file:
        file.write(contenuto + "\n")
    return f"Aggiunto a '{titolo}': {contenuto}"


def leggi_nota(titolo: str) -> str:
    if not titolo_sicuro(titolo):
        return f"Titolo non valido: '{titolo}'. Usa solo lettere, numeri, spazi e underscore."
    
    try:
        with open(percorso_note / f"{titolo}.txt", "r", encoding="utf-8") as file:
            contenuto = file.read()
    except FileNotFoundError:
        contenuto = "Nessuna nota con questo titolo."
    return f"Contenuto di '{titolo}': {contenuto}"