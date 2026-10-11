from tools.tempo import ottieni_ora_corrente

def test_ottieni_ora_corrente_restituisce_stringa():
    risultato = ottieni_ora_corrente()
    assert isinstance(risultato, str)
    
def test_ottieni_ora_corrente_ha_formato_corretto():
    risultato = ottieni_ora_corrente()
    assert risultato.startswith("Sono le ")
    assert len(risultato) == len("Sono le HH:MM:SS")