import json
from typing import Annotated, Literal
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from database_orm import carica_messaggi, salva_messaggi
from langchain_tools import scrivi_nota,apri,cerca_note, leggi_la_nota, meteo_attuale, ora_corrente, nessuna_azione_disponibile,n8n
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from config import MODELLO_LLM, OLLAMA_BASE_URL
import logging

logger = logging.getLogger(__name__)

class StatoMultiAgente(TypedDict):
    messages :Annotated[list, add_messages]
    prossimo_agente:str
    
class DecisioneRouting(BaseModel):
    categoria: Literal["azioni", "ricerca", "rifiuta"] = Field(
    description="""Sei un router. Classifica la richiesta dell'utente in UNA categoria:
- azioni: dati in tempo reale o comandi da eseguire ora (ora attuale, meteo, aprire siti/programmi, creare/leggere/modificare note, classificare il messaggio o reclamo di un cliente). Es: "che ore sono?", "che tempo fa a Milano?", "apri chrome", "leggi la nota spesa", "classifica questo messaggio di un cliente: mi è arrivata una bolletta di 400 euro".
- ricerca: recuperare cose che l'utente ha GIA' scritto nelle sue note, compresi i suoi progetti e le app che ha sviluppato. Se la domanda riguarda un nome che non è cultura generale (un progetto, un'app, un cliente), scegli ricerca. Es: "cosa ho scritto sull'architettura?", "quali task avevo per il progetto X?", "dimmi com'è fatta l'app Y".
- rifiuta: SOLO cultura generale nota a tutti (storia, scienza, personaggi famosi), non legata all'utente. Es: "chi era Napoleone?"."""
)
    
    
    
modello_router = ChatOllama(model=MODELLO_LLM, base_url=OLLAMA_BASE_URL, temperature=0)
modello_router_strutturato = modello_router.with_structured_output(DecisioneRouting).with_retry(
    stop_after_attempt=3
)

PROMPT_ROUTER = SystemMessage(content="""Sei un router. Classifica la richiesta dell'utente in UNA categoria:
- azioni: dati in tempo reale o comandi da eseguire ora (ora attuale, meteo, aprire siti/programmi, creare/leggere/modificare note, classificare il messaggio o reclamo di un cliente). Es: "che ore sono?", "che tempo fa a Milano?", "apri chrome", "leggi la nota spesa", "classifica questo messaggio di un cliente: mi è arrivata una bolletta di 400 euro".
- ricerca: recuperare cose che l'utente ha GIA' scritto nelle sue note, compresi i suoi progetti e le app che ha sviluppato. Se la domanda riguarda un nome che non è cultura generale (un progetto, un'app, un cliente), scegli ricerca. Es: "cosa ho scritto sull'architettura?", "quali task avevo per il progetto X?", "dimmi com'è fatta l'app Y".
- rifiuta: SOLO cultura generale nota a tutti (storia, scienza, personaggi famosi), non legata all'utente. Es: "chi era Napoleone?".""")

def nodo_orchestratore(stato: StatoMultiAgente) -> dict:
    ultimi_messaggi = stato["messages"][-4:]

    decisione = modello_router_strutturato.invoke(
        [PROMPT_ROUTER] + ultimi_messaggi)
    
    logger.info(f"[ORCHESTRATORE] Categoria: {decisione.categoria}")
    
    return {"prossimo_agente": decisione.categoria}

strumenti_azioni = [ora_corrente, meteo_attuale, apri,leggi_la_nota,scrivi_nota,nessuna_azione_disponibile,n8n]
strumenti_ricerca = [cerca_note]

modello = ChatOllama(model=MODELLO_LLM, base_url=OLLAMA_BASE_URL, temperature=0)
modello_azioni= modello.bind_tools(strumenti_azioni).with_retry(stop_after_attempt=3)
modello_ricerca = modello.bind_tools(strumenti_ricerca).with_retry(stop_after_attempt=3)

nodo_strumenti_azioni = ToolNode(strumenti_azioni)
nodo_strumenti_ricerca = ToolNode(strumenti_ricerca)

def nodo_agente_azioni(stato: StatoMultiAgente) -> dict:
    system_prompt = SystemMessage(content="""Rispondi SOLO in italiano. Mai inglese, cinese o altre lingue.
    Sei un assistente per azioni pratiche: ora, meteo, aprire siti o programmi, gestire note, classificare messaggi dei clienti.
    Esegui subito l'azione richiesta e rispondi in una o due frasi.
    Se l'utente ti chiede di classificare o analizzare il messaggio di un cliente, usa lo strumento n8n passando il messaggio del cliente così com'è, senza riassumerlo, e riporta categoria, urgenza e risposta suggerita.
    Puoi fare SOLO ciò che fanno gli strumenti: non puoi cliccare, prenotare, pagare o compilare moduli.
    Se l'utente chiede anche queste cose, fai la parte possibile e digli che il resto deve farlo lui.""")
    messaggi_con_sistema = [system_prompt] + stato["messages"]
    risposta = modello_azioni.invoke(messaggi_con_sistema)
    logger.info("[AGENTE AZIONI] richiamato")

    if risposta.tool_calls and _solo_chiamate_ripetute(stato["messages"], risposta.tool_calls):
        # Il modello ripete un'azione già eseguita (es. riaprire lo stesso sito): non rieseguirla
        logger.info("[AGENTE AZIONI] chiamata ripetuta ignorata")
        risultati = [m.content for m in stato["messages"] if isinstance(m, ToolMessage)]
        risposta = AIMessage(content=risultati[-1])

    return {"messages": [risposta]}


def _solo_chiamate_ripetute(messaggi: list, nuove_chiamate: list) -> bool:
    gia_eseguite = {
        (c["name"], json.dumps(c["args"], sort_keys=True))
        for m in messaggi if isinstance(m, AIMessage)
        for c in m.tool_calls
    }
    return all((c["name"], json.dumps(c["args"], sort_keys=True)) in gia_eseguite for c in nuove_chiamate)


def nodo_agente_ricerca(stato: StatoMultiAgente) -> dict:
    system_prompt = SystemMessage(content="""Sei un assistente specializzato nel recuperare informazioni dalle note personali dell'utente.
    REGOLE FERREE, da rispettare sempre:
    - Per OGNI domanda chiama SEMPRE lo strumento cerca_note prima di rispondere, anche se nella conversazione ci sono già informazioni sull'argomento. Non dire mai che le note non contengono qualcosa senza aver appena cercato.
    - Riporta SOLO testo che appare letteralmente nel risultato dello strumento di ricerca. Non aggiungere MAI date, fonti, titoli o dettagli che non sono esplicitamente presenti nel risultato.
    - Se lo strumento restituisce "NESSUN RISULTATO PERTINENTE TROVATO", dillo chiaramente e fermati — non proporre contenuto alternativo o inventato.
    - Se i risultati trovati sembrano solo vagamente collegati alla domanda (non specifici), dillo esplicitamente invece di presentarli con sicurezza come se fossero la risposta esatta.
    - Non rispondere MAI usando conoscenza generale non presente nelle note.
    - Rispondi sempre e solo in italiano, senza parole inglesi o cinesi.""")
    
    messaggi_con_sistema = [system_prompt] + stato["messages"]
    risposta = modello_ricerca.invoke(messaggi_con_sistema)
    logger.info("[AGENTE RICERCA] richiamato")

    return {"messages": [risposta]}


def nodo_rifiuta(stato: StatoMultiAgente) -> dict:
    messaggio = AIMessage(content="Posso aiutarti solo con le tue note personali o con azioni pratiche (meteo, ora, aprire siti, gestire note). Questa domanda non rientra tra le mie capacità.")
    logger.info("[AGENTE RIFIUTA] richiamato")
    return {"messages": [messaggio]}

def nodo_non_so(stato:StatoMultiAgente) -> dict:
    messaggio = AIMessage(content="Non posso farlo: al momento so solo dirti l'ora e il meteo, aprire siti o programmi e gestire le note.")
    return {"messages": [messaggio]}

def serve_tool_azioni(stato: StatoMultiAgente) -> str:
    ultimo_messaggio = stato["messages"][-1]
    if ultimo_messaggio.tool_calls:
        return "strumenti_azioni"
    return END


def serve_tool_ricerca(stato: StatoMultiAgente) -> str:
    ultimo_messaggio = stato["messages"][-1]
    if ultimo_messaggio.tool_calls:
        return "strumenti_ricerca"
    return END

def dopo_ricerca(stato: StatoMultiAgente) -> str:
    ultimo = stato["messages"][-1]
    if getattr(ultimo, "tool_calls", None):
        return "strumenti_ricerca"
    for m in reversed(stato["messages"]):
        if isinstance(m, ToolMessage):
            if "NESSUN RISULTATO PERTINENTE" in m.content:
                return "agente_azioni"
            break
    return END


def dopo_azioni(stato: StatoMultiAgente) -> str:
    ultimo = stato["messages"][-1]
    if getattr(ultimo, "tool_calls", None):
        return "strumenti_azioni"
    for m in reversed(stato["messages"]):
        if isinstance(m, ToolMessage):
            if "NESSUNA_AZIONE_DISPONIBILE" in m.content:
                return "non_so"
            break
    return END
grafo = StateGraph(StatoMultiAgente)

grafo.add_node("orchestratore", nodo_orchestratore)
grafo.add_node("agente_ricerca", nodo_agente_ricerca)
grafo.add_node("agente_azioni", nodo_agente_azioni)
grafo.add_node("strumenti_ricerca", nodo_strumenti_ricerca)
grafo.add_node("strumenti_azioni", nodo_strumenti_azioni)
grafo.add_node("non_so", nodo_non_so)
grafo.add_node("rifiuta", nodo_rifiuta)

grafo.set_entry_point("orchestratore")

grafo.add_conditional_edges(
    "orchestratore",
    lambda s: s["prossimo_agente"],
{"azioni": "agente_azioni", "ricerca": "agente_ricerca", "rifiuta": "agente_ricerca"}
)

grafo.add_conditional_edges("agente_ricerca", dopo_ricerca)
grafo.add_conditional_edges("agente_azioni", dopo_azioni)

grafo.add_edge("strumenti_ricerca", "agente_ricerca")
grafo.add_edge("strumenti_azioni", "agente_azioni")
grafo.add_edge("non_so", END)
grafo.add_edge("rifiuta", END)

app_grafo = grafo.compile()

def gestisci_domanda(sessione_id: str, domanda_utente: str) -> str:
    storico = carica_messaggi(sessione_id)
    storico.append({"role": "user", "content": domanda_utente})
    salva_messaggi(sessione_id, "user", domanda_utente)
    
    risposta = app_grafo.invoke({"messages": storico})
    contenuto_risposta = risposta["messages"][-1].content
    
    salva_messaggi(sessione_id, "assistant", contenuto_risposta)
    return contenuto_risposta
