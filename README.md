# Jarvis — assistente personale multi-agente con LangGraph

Jarvis è un assistente personale che gira **interamente in locale** grazie a [Ollama](https://ollama.com).
È costruito con [LangGraph](https://github.com/langchain-ai/langgraph): un orchestratore classifica ogni
richiesta e la passa all'agente più adatto. Può eseguire azioni pratiche (meteo, ora, note, aprire siti e
programmi, classificare messaggi tramite un workflow n8n) e rispondere a domande sulle tue note personali in Markdown tramite **RAG ibrido** (BM25 + ricerca semantica).

Puoi usarlo in quattro modi: da terminale, con un'interfaccia grafica web (**Streamlit**), tramite API REST
(FastAPI) oppure come server **MCP** per client come Claude Desktop.

## Architettura

```
                    ┌──────────────┐
   domanda ───────▶ │ orchestratore│  (output strutturato: azioni | ricerca | rifiuta)
                    └──────┬───────┘
          ┌────────────────┴─────────────────┐
          ▼ azioni                           ▼ ricerca / rifiuta
  ┌───────────────┐                  ┌───────────────┐
  │ agente_azioni │                  │agente_ricerca │
  └──────┬────────┘                  └──────┬────────┘
         ▼                                  ▼
  strumenti_azioni                   strumenti_ricerca ──(nessun risultato)──▶ agente_azioni
  meteo, ora, note,  cerca_note (RAG ibrido)
  apri sito/programma,
  n8n (webhook)
         │
         └──(nessuna azione disponibile)──▶ non_so
```

- **Orchestratore**: usa un LLM con output strutturato (Pydantic) per scegliere la categoria, guardando gli
  ultimi 4 messaggi della conversazione (così capisce anche le domande di seguito, es. "e a Roma?").
  Le domande su nomi che non sono cultura generale (un progetto, un'app, un cliente) vanno in `ricerca`.
- **Domande "rifiuta"**: invece di essere scartate subito passano comunque dall'agente ricerca, per evitare
  falsi rifiuti su argomenti presenti nelle note. Se nelle note non c'è nulla e non esiste un'azione adatta,
  Jarvis risponde che non può aiutare (`non_so`).
- **Agente azioni**: tool calling su meteo ([Open-Meteo](https://open-meteo.com), senza API key), ora corrente,
  lettura/scrittura note, apertura di siti web e di un elenco ristretto di programmi.
- **Integrazione n8n**: lo strumento `n8n` invia il messaggio a un webhook n8n, dove un LLM lo classifica
  (categoria, urgenza, risposta suggerita) e il risultato viene salvato su PostgreSQL. Il workflow è nel repository [n8n_classificatore](https://github.com/mirkoparente/n8n_classificatore).
- **Agente ricerca**: interroga le note personali con BM25 + embedding Chroma a ogni domanda e risponde solo
  con ciò che trova. Se non trova nulla, passa la richiesta all'agente azioni.
- **Memoria**: la cronologia delle conversazioni è salvata per sessione in SQLite (SQLAlchemy).

## Struttura del progetto

| File / cartella | Descrizione |
| --- | --- |
| `main.py` | Chat da terminale |
| `app_chat.py` | Interfaccia grafica di chat con Streamlit |
| `api.py` | API REST con FastAPI |
| `mcp_server.py` | Server MCP che espone gli strumenti |
| `multiagente.py` | Grafo LangGraph multi-agente (versione principale) |
| `langchain_tools.py` | Definizione dei tool per LangChain |
| `tools/` | Implementazione degli strumenti (meteo, ora, note, browser, ricerca, webhook n8n) |
| `rag/` | Chunking, indicizzazione Chroma, ricerca semantica e ibrida |
| `model/models.py`, `database_orm.py` | Modelli e accesso al DB con SQLAlchemy |
| `config.py` | Configurazione tramite variabili d'ambiente |
| `logging_config.py` | Configurazione del logging (file `jarvis.log`) |
| `tests/` | Test unitari (pytest) |
| `eval/` | Golden set e script di valutazione |
| `dati/` | Generata in automatico: database, indice vettoriale, note create dall'agente |

## Requisiti

- Python 3.11+
- [Ollama](https://ollama.com) in esecuzione in locale
- Windows per lo strumento "apri programma" (i percorsi dei programmi sono specifici di Windows);
  il resto funziona su qualsiasi sistema

## Installazione

```bash
git clone https://github.com/mirkoparente/Jarvis-langgraph.git
cd Jarvis-langgraph

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

# Modelli Ollama
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

## Configurazione

Le impostazioni si leggono dal file `.env` nella cartella del progetto, oppure da variabili d'ambiente.
Tutte sono facoltative. Per partire copia il file di esempio:

```bash
cp .env.example .env   # Windows: copy .env.example .env
```

| Variabile | Default | Descrizione |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Indirizzo di Ollama |
| `JARVIS_MODELLO` | `qwen3:8b` | Modello per orchestratore e agenti (deve supportare il tool calling) |
| `JARVIS_MODELLO_EMBEDDING` | `nomic-embed-text` | Modello di embedding per il RAG |
| `JARVIS_CARTELLA_NOTE` | `./note` | Cartella con le note `.md` da indicizzare (es. un vault Obsidian) |
| `JARVIS_N8N_WEBHOOK_URL` | — | URL di produzione del webhook n8n (es. `http://localhost:5678/webhook/chiedi`) |

Le variabili d'ambiente già impostate hanno la precedenza sul file `.env`.

## Indicizzare le note

Prima di usare la ricerca sulle note costruisci l'indice vettoriale (ripetilo quando le note cambiano):

```bash
python -m rag.indicizzazione
```

Vengono letti tutti i file `.md` della cartella (anche nelle sottocartelle); l'eventuale front matter YAML viene rimosso.
L'indice BM25 invece viene costruito in memoria alla prima ricerca.

## Utilizzo

### Terminale

```bash
python main.py
```

Scrivi `esci` per terminare.

### Interfaccia grafica (Streamlit)

```bash
streamlit run app_chat.py
```

Si apre nel browser su http://localhost:8501. Ogni scheda del browser usa una nuova sessione di conversazione.

### API REST

```bash
uvicorn api:app --reload
```

Documentazione interattiva su http://localhost:8000/docs.

| Metodo | Endpoint | Descrizione |
| --- | --- | --- |
| `GET` | `/health` | Stato del servizio |
| `POST` | `/sessioni` | Crea una nuova sessione e restituisce `sessione_id` |
| `POST` | `/ask` | Invia un messaggio: `{"sessione_id": "...", "messaggio": "..."}` |

```bash
curl -X POST http://localhost:8000/sessioni
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"sessione_id": "<id>", "messaggio": "Che tempo fa a Milano?"}'
```

### Server MCP

```bash
python mcp_server.py
```

Per usarlo con Claude Desktop aggiungi a `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jarvis": {
      "command": "C:\\percorso\\Jarvis-langgraph\\venv\\Scripts\\python.exe",
      "args": ["C:\\percorso\\Jarvis-langgraph\\mcp_server.py"]
    }
  }
}
```

## Test

```bash
pytest
```

I test non richiedono Ollama: le chiamate esterne (Open-Meteo, LLM) sono simulate con dei mock. Coprono gli strumenti, il chunking,
la logica di instradamento del grafo e gli endpoint dell'API.

## Valutazione (golden set)

`eval/golden_set.json` contiene domande etichettate con la categoria attesa (`azioni`, `ricerca`, `rifiuta`).
Lo script le passa una per una all'orchestratore e conta quante volte sceglie la categoria giusta,
stampando le domande sbagliate.

`eval/golden_rag.json` contiene domande sulle note con le note attese (lista vuota = la risposta non c'è).
Lo script prova alcune soglie di distanza per la ricerca semantica e, per ognuna, mostra quante note giuste
trova e quante domande senza risposta scarta: serve a scegliere la soglia usata in `cerca_ibrida`.
Copia `eval/golden_rag.example.json` in `eval/golden_rag.json` e scrivi domande sulle tue note.

Serve Ollama in esecuzione e l'indice delle note già costruito.

```bash
python -m eval.valuta
```

È utile per confrontare modelli diversi (`JARVIS_MODELLO`) o modifiche al prompt del router.

## Esempi di richieste

- "Che ore sono?" → agente azioni
- "Che tempo fa a Roma?" → agente azioni (Open-Meteo)
- "Crea una nota spesa con latte e pane" → agente azioni
- "Apri vscode" / "Apri https://github.com" → agente azioni
- "Classifica questo messaggio di un cliente: mi è arrivata una bolletta di 400 euro" → agente azioni (n8n)
- "Cosa ho scritto sull'architettura del progetto X?" → agente ricerca (RAG)
- "Dimmi com'è fatta l'app Y" → agente ricerca (nome non di cultura generale)
- "Chi ha vinto i mondiali del 2006?" → nessun risultato nelle note → non può aiutare (fuori ambito)

## Sicurezza

- L'agente può aprire solo i programmi presenti in `PROGRAMMI_CONSENTITI` (`tools/browser.py`);
  i siti devono essere URL che iniziano con `http://` o `https://`.
- I titoli delle note accettano solo lettere, numeri, spazi e underscore, per evitare path traversal.
- L'API non ha autenticazione: tienila su `localhost` e non esporla in rete.
