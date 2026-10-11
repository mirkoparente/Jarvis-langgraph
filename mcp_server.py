from mcp.server.mcpserver import MCPServer
from tools import ottieni_meteo, ottieni_ora_corrente, crea_nota,leggi_nota,apri_sito,aggiungi_a_nota,webhook
from logging_config import configura_logging
import logging

from tools.browser import apri_programma
configura_logging()

logger = logging.getLogger(__name__)

mcp = MCPServer("Jarvis")


@mcp.tool()
def ora_corrente() ->str:
    """Restituisce l'ora corrente del sistema"""
    return ottieni_ora_corrente()


@mcp.tool()
def meteo(citta:str) ->str:
    """Restituisce il meteo per una città specificata"""
    return ottieni_meteo(citta)


@mcp.tool()
def apri_sito_web(url: str) -> str:
    """Apre un sito web nel browser dell'utente."""
    return apri_sito(url)


@mcp.tool()
def crea_nuova_nota(titolo: str, contenuto: str) -> str:
    """Crea una nuova nota con un titolo e un contenuto, sovrascrivendo qualsiasi nota esistente con lo stesso titolo"""
    return crea_nota(titolo, contenuto)


@mcp.tool()
def aggiungi_alla_nota(titolo: str, contenuto: str) -> str:
    """Aggiunge del testo in fondo a una nota esistente, senza cancellare il contenuto precedente"""
    return aggiungi_a_nota(titolo, contenuto)


@mcp.tool()
def leggi_una_nota(titolo: str) -> str:
    """Legge e restituisce il contenuto di una nota salvata in precedenza"""
    return leggi_nota(titolo)

@mcp.tool()
def apri_programmi(programma:str) ->str:
    """Apre un programma indicato dall'utente"""
    return apri_programma(programma)

@mcp.tool()
def n8n(messaggio:str):
    """Classifica il messaggio di un cliente di un'azienda di energia, mobile e internet
    e restituisce categoria (fatturazione, guasto, cambio_offerta, altro), urgenza e una risposta suggerita.
    Usalo quando l'utente chiede di classificare, analizzare o rispondere al messaggio/reclamo di un cliente.

    Args:
        messaggio: il testo del messaggio del cliente, riportato così com'è
    """
    return webhook(messaggio)
 
if __name__ == "__main__":  
    mcp.run()