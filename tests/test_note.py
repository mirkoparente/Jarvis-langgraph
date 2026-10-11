from tools.note import titolo_sicuro

def test_titolo_sicuro_accetta_titoli_normali():
    assert titolo_sicuro("spesa") is True
    assert titolo_sicuro("nota_1") is True
    assert titolo_sicuro("Nota Importante") is True

def test_titolo_sicuro_rifiuta_path_traversal():
    assert titolo_sicuro("../../../test") is False
    assert titolo_sicuro("../segreti") is False

def test_titolo_sicuro_rifiuta_vuoto():
    assert titolo_sicuro("") is False