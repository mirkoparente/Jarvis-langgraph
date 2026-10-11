from multiagente import gestisci_domanda
from database_orm import crea_sessione
from logging_config import configura_logging


def main() -> None:
    configura_logging()
    sessione_id = crea_sessione()
    print("Ciao, sono Jarvis (v3, LangGraph multi-agente). Scrivi 'esci' per terminare.")
    print(f"(Nuova sessione: {sessione_id})")

    while True:
        prompt = input("Tu: ")
        if prompt.lower() == "esci":
            print("Alla prossima!")
            break
        
        risposta = gestisci_domanda(sessione_id, prompt)
        print(f"Jarvis: {risposta}")


if __name__ == "__main__":
    main()