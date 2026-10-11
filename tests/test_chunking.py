from rag.chunking import chunking


def test_chunking_testo_corto_un_solo_chunk():
    assert chunking("ciao", dimensione=500, overlap=50) == ["ciao"]


def test_chunking_testo_vuoto():
    assert chunking("") == []


def test_chunking_rispetta_dimensione_e_overlap():
    testo = "a" * 100 + "b" * 100
    chunk = chunking(testo, dimensione=120, overlap=20)
    assert all(len(c) <= 120 for c in chunk)
    # l'inizio di ogni chunk ripete la fine del precedente
    assert chunk[0][-20:] == chunk[1][:20]


def test_chunking_copre_tutto_il_testo():
    testo = "".join(str(i % 10) for i in range(1234))
    chunk = chunking(testo, dimensione=100, overlap=10)
    ricostruito = chunk[0] + "".join(c[10:] for c in chunk[1:])
    assert ricostruito == testo
