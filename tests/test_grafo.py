from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END

from multiagente import dopo_azioni, dopo_ricerca


def messaggio_con_tool_call(nome: str) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": nome, "args": {}, "id": "1"}])


def test_dopo_ricerca_esegue_tool_se_richiesto():
    stato = {"messages": [HumanMessage("cosa ho scritto su X?"), messaggio_con_tool_call("cerca_note")]}
    assert dopo_ricerca(stato) == "strumenti_ricerca"


def test_dopo_ricerca_passa_ad_azioni_se_nessun_risultato():
    stato = {"messages": [
        HumanMessage("cosa ho scritto su X?"),
        messaggio_con_tool_call("cerca_note"),
        ToolMessage(content="NESSUN RISULTATO PERTINENTE TROVATO nelle note.", tool_call_id="1"),
        AIMessage(content="Non ho trovato nulla."),
    ]}
    assert dopo_ricerca(stato) == "agente_azioni"


def test_dopo_ricerca_termina_se_trova_risultati():
    stato = {"messages": [
        HumanMessage("cosa ho scritto su X?"),
        messaggio_con_tool_call("cerca_note"),
        ToolMessage(content="Dalla nota 'X': ...", tool_call_id="1"),
        AIMessage(content="Nella nota X hai scritto..."),
    ]}
    assert dopo_ricerca(stato) == END


def test_dopo_azioni_esegue_tool_se_richiesto():
    stato = {"messages": [HumanMessage("che ore sono?"), messaggio_con_tool_call("ora_corrente")]}
    assert dopo_azioni(stato) == "strumenti_azioni"


def test_dopo_azioni_va_a_non_so_se_nessuna_azione():
    stato = {"messages": [
        HumanMessage("prenotami un volo"),
        messaggio_con_tool_call("nessuna_azione_disponibile"),
        ToolMessage(content="NESSUNA_AZIONE_DISPONIBILE", tool_call_id="1"),
        AIMessage(content="Non posso."),
    ]}
    assert dopo_azioni(stato) == "non_so"


def test_dopo_azioni_termina_dopo_risposta():
    stato = {"messages": [
        HumanMessage("che ore sono?"),
        messaggio_con_tool_call("ora_corrente"),
        ToolMessage(content="Sono le 15:00:00", tool_call_id="1"),
        AIMessage(content="Sono le 15:00."),
    ]}
    assert dopo_azioni(stato) == END
