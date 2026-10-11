import requests


def ottieni_meteo(citta:str) -> str:
    cordinate = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={citta}&count=1&language=it")
    results = cordinate.json().get("results")
    if not results:
        return f"Non ho trovato la città '{citta}'"
    
    lat = results[0]["latitude"]
    lon = results[0]["longitude"]
    
    meteo = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code")
    current=meteo.json().get("current")
    temperature = current.get("temperature_2m")
    weather_code = current.get("weather_code")
    
    codici_meteo = {
    0: "cielo sereno",
    1: "prevalentemente sereno",
    2: "parzialmente nuvoloso",
    3: "nuvoloso",
    45: "nebbia",
    61: "pioggia leggera",
    63: "pioggia moderata",
    65: "pioggia forte",
    71: "neve leggera",
    95: "temporale"
    }

    descrizione = codici_meteo.get(weather_code, "condizioni sconosciute")
    
    return f"Il meteo attuale a {citta} è di {temperature}°C con {descrizione}."
