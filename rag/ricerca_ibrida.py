import re
from pathlib import Path
from rank_bm25 import BM25Okapi
from rag.indicizzazione import leggi_tutte_le_note
from rag.chunking import chunking
from rag.ricerca import cerca_chunk_rilevanti

_bm25_index = None
_bm25_corpus = None
_bm25_metadati = None




# Parole troppo comuni: senza filtrarle BM25 trova "qualcosa" per quasi ogni domanda
STOPWORDS = {
    "a", "ad", "al", "allo", "ai", "agli", "all", "alla", "alle", "con", "col", "da", "dal", "dallo",
    "dai", "dagli", "dall", "dalla", "dalle", "di", "del", "dello", "dei", "degli", "dell", "della",
    "delle", "in", "nel", "nello", "nei", "negli", "nell", "nella", "nelle", "su", "sul", "sullo",
    "sui", "sugli", "sull", "sulla", "sulle", "per", "tra", "fra", "il", "lo", "la", "i", "gli", "le",
    "l", "un", "uno", "una", "e", "ed", "o", "ma", "se", "che", "chi", "cosa", "come", "dove", "quando",
    "quale", "quali", "quanto", "perché", "perche", "non", "mi", "ti", "ci", "vi", "si", "ne", "io",
    "tu", "lui", "lei", "noi", "voi", "loro", "mio", "mia", "miei", "mie", "tuo", "tua", "è", "e'",
    "sono", "sei", "siamo", "siete", "ho", "hai", "ha", "abbiamo", "avete", "hanno", "fa", "fare",
    "sai", "ciao", "questo", "questa", "quello", "quella", "anche", "più", "molto", "c", "cè",
}


def _tokenizza(testo: str) -> list[str]:
    """Spezza un testo in parole minuscole, ignorando punteggiatura e stopword."""
    return [t for t in re.findall(r"\w+", testo.lower()) if t not in STOPWORDS]


def _costruisci_indice_bm25(cartella_note: Path) -> None:
    global _bm25_index, _bm25_corpus, _bm25_metadati
    
    note = leggi_tutte_le_note(cartella_note)
    
    corpus = []
    metadati = []
    for nota in note:
        for testo_chunk in chunking(nota["contenuto"]):
            corpus.append(testo_chunk)
            metadati.append({"titolo_nota": nota["titolo"]})
    
    corpus_tokenizzato = [_tokenizza(testo) for testo in corpus]
    
    _bm25_index = BM25Okapi(corpus_tokenizzato) if corpus else False
    _bm25_corpus = corpus
    _bm25_metadati = metadati
    
    
def cerca_bm25(domanda: str, cartella_note: Path, k: int = 5) -> list[dict]:
    if _bm25_index is None:
        _costruisci_indice_bm25(cartella_note)
    if not _bm25_corpus:
        return []
    
    query_tokenizzata = _tokenizza(domanda)
    punteggi = _bm25_index.get_scores(query_tokenizzata)
    
    indici_ordinati = sorted(range(len(punteggi)), key=lambda i: punteggi[i], reverse=True)
    
    risultati = []
    for i in indici_ordinati[:k]:
        if punteggi[i] > 0:   # solo risultati con almeno una parola in comune
            risultati.append({
                "titolo_nota": _bm25_metadati[i]["titolo_nota"],
                "testo": _bm25_corpus[i],
                "punteggio_bm25": punteggi[i]
            })
    return risultati


def cerca_ibrida(domanda: str, cartella_note: Path, k: int = 5, soglia: float = 0.85) -> list[dict]:
    risultati_semantici = cerca_chunk_rilevanti(domanda, k=k, soglia_distanza= soglia)
    risultati_bm25 = cerca_bm25(domanda, cartella_note, k=k)
    
    visti = set()
    combinati = []
    
    for r in risultati_bm25 + risultati_semantici:
        chiave = r["titolo_nota"]
        if chiave not in visti:
            visti.add(chiave)
            combinati.append(r)
    
    return combinati[:k]