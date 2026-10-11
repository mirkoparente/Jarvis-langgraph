import os
import subprocess
import webbrowser


def apri_sito(url: str) -> str:
    print(f"URL ricevuto dal modello: {url}")
    if not url.strip().lower().startswith(("http://", "https://")):
        return f"'{url}' non è un indirizzo valido: usa un URL che inizia con http:// o https://"
    webbrowser.open(url)
    return f"Ho aperto: {url}"



PROGRAMMI_CONSENTITI = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calcolatrice": "calc.exe",
    "vscode": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code", "Code.exe"),
    "explorer": "explorer.exe",
}

def apri_programma(programma:str) ->str:
    print(f"Programma ricevuto dal modello: {programma}")
    
    chiave= programma.strip().lower()
    
    if chiave not in PROGRAMMI_CONSENTITI:
        return f"'{programma}' non è tra i programmi consentiti. Disponibili: {', '.join(PROGRAMMI_CONSENTITI.keys())}"
    
    percorso = PROGRAMMI_CONSENTITI[chiave]
    try:
        subprocess.Popen(percorso)
        return f"Ho aperto: {programma}"
    except FileNotFoundError:
        return f"Non trovo {programma} su questo computer."
        
        