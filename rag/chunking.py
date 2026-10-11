def chunking(testo:str, dimensione:int = 500, overlap:int=50)->list[str]:
    chunk=[]
    inizio = 0
    
    while inizio < len(testo):
        fine=inizio + dimensione
        chunk.append(testo[inizio:fine])
        inizio += dimensione - overlap
    return chunk