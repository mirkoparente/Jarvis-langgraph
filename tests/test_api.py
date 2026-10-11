from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health():
    risposta = client.get("/health")
    assert risposta.status_code == 200
    assert risposta.json() == {"status": "ok"}


def test_ask_sessione_inesistente():
    with patch("api.sessione_esistente", return_value=False):
        risposta = client.post("/ask", json={"sessione_id": "non-esiste", "messaggio": "ciao"})
    assert risposta.status_code == 404


def test_ask_messaggio_vuoto():
    with patch("api.sessione_esistente", return_value=True):
        risposta = client.post("/ask", json={"sessione_id": "abc", "messaggio": "   "})
    assert risposta.status_code == 400


def test_ask_risposta_ok():
    with patch("api.sessione_esistente", return_value=True), \
         patch("api.gestisci_domanda", return_value="Sono le 15:00") as mock_gestisci:
        risposta = client.post("/ask", json={"sessione_id": "abc", "messaggio": "che ore sono?"})
    assert risposta.status_code == 200
    assert risposta.json() == {"risposta": "Sono le 15:00"}
    mock_gestisci.assert_called_once_with("abc", "che ore sono?")


def test_ask_errore_interno():
    with patch("api.sessione_esistente", return_value=True), \
         patch("api.gestisci_domanda", side_effect=RuntimeError("Ollama giù")):
        risposta = client.post("/ask", json={"sessione_id": "abc", "messaggio": "ciao"})
    assert risposta.status_code == 500
