from datetime import datetime

def ottieni_ora_corrente() -> str:
    ora = datetime.now().strftime("%H:%M:%S")
    return f"Sono le {ora}"