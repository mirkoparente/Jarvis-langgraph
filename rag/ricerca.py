from rag.indicizzazione import ottieni_vectorstore


def cerca_chunk_rilevanti(domanda:str , k:int =3, soglia_distanza: float = 0.6):
    vectorstore= ottieni_vectorstore()
    risultati_con_punteggio= vectorstore.similarity_search_with_score(domanda,k=k)
    
    risultati_rilevanti = [{
        "titolo_nota": r.metadata["titolo_nota"], "testo": r.page_content, "distanza":punteggio }
        for r, punteggio in risultati_con_punteggio
        if punteggio <= soglia_distanza
    ]
    return risultati_rilevanti
