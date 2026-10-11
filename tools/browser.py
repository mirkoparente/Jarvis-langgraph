import subprocess
import webbrowser
import logging

logger = logging.getLogger(__name__)

# Ricordato al modello dopo ogni apertura, così non dichiara azioni fatte "dentro" la pagina
AVVISO_PAGINA = ". Nota: sulla pagina non posso fare altro, il resto lo fa l'utente."


def apri_sito(url: str) -> str:
    logger.info(f"URL ricevuto dal modello: {url}")

    webbrowser.open(url)
    return f"Ho aperto: {url}" + AVVISO_PAGINA



PROGRAMMI_CONSENTITI = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calcolatrice": "calc.exe",
    "vscode": "code.exe",
    "explorer": "explorer.exe",
}

# Programmi che accettano un URL come argomento da riga di comando
BROWSER = {"chrome"}

def apri_programma(programma:str, url: str | None = None) ->str:
    logger.info(f"Programma ricevuto dal modello: {programma} (url: {url})")
    
    chiave= programma.strip().lower()
    
    if chiave not in PROGRAMMI_CONSENTITI:
        return f"'{programma}' non è tra i programmi consentiti. Disponibili: {', '.join(PROGRAMMI_CONSENTITI.keys())}"
    
    percorso = PROGRAMMI_CONSENTITI[chiave]
    if url and chiave in BROWSER:
        subprocess.Popen([percorso, url])
        return f"Ho aperto {url} in {programma}" + AVVISO_PAGINA
    
    subprocess.Popen(percorso)
    if url:
        return f"Ho aperto: {programma}. " + apri_sito(url)
    return f"Ho aperto: {programma}"