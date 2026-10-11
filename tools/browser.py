import subprocess
import webbrowser


def apri_sito(url: str) -> str:
    print(f"URL ricevuto dal modello: {url}")

    webbrowser.open(url)
    return f"Ho aperto: {url}"



PROGRAMMI_CONSENTITI = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calcolatrice": "calc.exe",
    "vscode": "code.exe",
    "explorer": "explorer.exe",
}

def apri_programma(programma:str) ->str:
    print(f"Programma ricevuto dal modello: {programma}")
    
    chiave= programma.strip().lower()
    
    if chiave not in PROGRAMMI_CONSENTITI:
        return f"'{programma}' non è tra i programmi consentiti. Disponibili: {', '.join(PROGRAMMI_CONSENTITI.keys())}"
    
    percorso = PROGRAMMI_CONSENTITI[chiave]
    subprocess.Popen(percorso)
    return f"Ho aperto: {programma}"