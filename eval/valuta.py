"""Valutazione di Jarvis sui golden set.

1. Router: per ogni domanda di golden_set.json controlla se l'orchestratore
   sceglie la categoria giusta (azioni / ricerca / rifiuta).
2. Soglia della ricerca semantica: con golden_rag.json prova alcune soglie e
   conta quante note giuste trova e quante domande senza risposta scarta.

Uso:
    python -m eval.valuta
"""
import json
from pathlib import Path

from langchain_core.messages import HumanMessage

from multiagente import nodo_orchestratore
from rag.ricerca import cerca_chunk_rilevanti

CARTELLA_EVAL = Path(__file__).parent


def carica(nome: str) -> list[dict]:
    with open(CARTELLA_EVAL / nome, encoding="utf-8") as f:
        return json.load(f)


# --- 1. Router ---
casi = carica("golden_set.json")
corretti = 0
for caso in casi:
    stato = {"messages": [HumanMessage(caso["domanda"])]}
    predetta = nodo_orchestratore(stato)["prossimo_agente"]

    if predetta == caso["categoria"]:
        corretti += 1
        print(f"[OK]  {caso['domanda']}")
    else:
        print(f"[ERR] {caso['domanda']} -> {predetta} (atteso {caso['categoria']})")

print(f"\nAccuratezza del router: {corretti}/{len(casi)} ({corretti / len(casi):.0%})")


# --- 2. Soglia della ricerca semantica ---
# Valuto solo la parte semantica, perché la soglia agisce solo lì (BM25 ha il suo filtro)
casi_rag = carica("golden_rag.json")
positivi = [c for c in casi_rag if c["note_attese"]]      # la risposta è nelle note
negativi = [c for c in casi_rag if not c["note_attese"]]  # la risposta NON c'è

print("\nSoglia | note trovate | domande scartate correttamente")
for soglia in [0.6, 0.7, 0.85, 1.0]:
    trovate = 0
    for caso in positivi:
        titoli = [r["titolo_nota"] for r in cerca_chunk_rilevanti(caso["domanda"], k=5, soglia_distanza=soglia)]
        if any(t in caso["note_attese"] for t in titoli):
            trovate += 1

    scartate = 0
    for caso in negativi:
        if not cerca_chunk_rilevanti(caso["domanda"], k=5, soglia_distanza=soglia):
            scartate += 1

    print(f"{soglia:6} | {f'{trovate}/{len(positivi)}':12} | {scartate}/{len(negativi)}")
