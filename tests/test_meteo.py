from unittest.mock import patch, MagicMock

from tools.meteo import ottieni_meteo


def test_ottieni_meteo_mock():
    risposta_geocoding = MagicMock()
    risposta_geocoding.json.return_value = {
        "results": [{"latitude": 41.9, "longitude": 12.5}]
    }
    
    risposta_meteo = MagicMock()
    risposta_meteo.json.return_value = {
        "current": {"temperature_2m": 20.5, "weather_code": 0}        
    }
    
    with patch("tools.meteo.requests.get") as mock_get:
        mock_get.side_effect = [risposta_geocoding,risposta_meteo]
        
        risultato = ottieni_meteo("Roma")        
    assert "20.5" in risultato
    assert "cielo sereno" in risultato
    assert mock_get.call_count == 2

def test_ottieni_meteo_citta_non_trovata():
    risposta_geocoding_vuota = MagicMock()
    risposta_geocoding_vuota.json.return_value = {"results": []}
    
    with patch("tools.meteo.requests.get") as mock_get:
        mock_get.return_value = risposta_geocoding_vuota
        risultato = ottieni_meteo("CittaInventata")
    
    assert "Non ho trovato" in risultato
    assert mock_get.call_count == 1