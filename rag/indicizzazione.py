from pathlib import Path
import re
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from tqdm import tqdm

from config import CARTELLA_DATI, CARTELLA_NOTE, MODELLO_EMBEDDING, OLLAMA_BASE_URL
from rag.chunking import chunking

def rimuovi_formatter(testo:str)->str:
    return re.sub(r"^---\n.*?\n---\n","",testo,flags=re.DOTALL)


def leggi_tutte_le_note(cartella:Path)->list[dict]:
    note=[]
    for percorso_file in cartella.glob("**/*.md"):
        with open(percorso_file, "r", encoding="utf-8") as f:
            contenuto=f.read()
        note.append({
            "titolo":percorso_file.stem,
            "percorso":str(percorso_file.relative_to(cartella)),
            "modificato_il":str(percorso_file.stat().st_mtime),
            "contenuto":rimuovi_formatter(contenuto)
        })
    return note

def ottieni_vectorstore()->Chroma:
    embeddings= OllamaEmbeddings(
        model=MODELLO_EMBEDDING,
        base_url=OLLAMA_BASE_URL
    )

    return Chroma(
        collection_name="note_personali",
        embedding_function=embeddings,
        persist_directory=str(CARTELLA_DATI / "chroma_db")
    )

def costruisci_indice(percorso:Path = CARTELLA_NOTE):
    percorso = Path(percorso)
    if not percorso.is_dir():
        raise SystemExit(f"Cartella note non trovata: {percorso}. Controlla JARVIS_CARTELLA_NOTE nel file .env")
    note=leggi_tutte_le_note(percorso)
    if not note:
        raise SystemExit(f"Nessun file .md trovato in {percorso}")
    vectorstore=ottieni_vectorstore()
    documenti = []
    ids =[]
    for nota in tqdm(note, desc="Calcolo embedding"):
        chunk_testo= chunking(nota["contenuto"])
        for i, testo_chunk in enumerate(chunk_testo):
           documento=Document(
               page_content=testo_chunk,
               metadata={
                   "titolo_nota":nota["titolo"],
                   "percorso":nota["percorso"]
               }
           )
           documenti.append(documento)
           ids.append(f"{nota['percorso']}_{i}")
           
    vectorstore.add_documents(documenti, ids=ids)
    print(f"Indice creato: {len(documenti)} chunk salvati")


if __name__ == "__main__":
    costruisci_indice()
