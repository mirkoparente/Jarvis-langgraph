from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from config import CARTELLA_DATI

Base = declarative_base()

class Sessione(Base):
    __tablename__ = "sessioni"
    
    id= Column(String, primary_key=True)
    creata_il = Column(DateTime, default=datetime.now)
    messaggi=relationship("Messaggio",back_populates="sessione")
    
class Messaggio(Base):
    __tablename__ = "messaggi"
    
    id= Column(String,primary_key=True)
    sessione_id= Column(String, ForeignKey("sessioni.id"))
    ruolo = Column(String, nullable=False)
    contenuto = Column(String,nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    
    sessione=relationship("Sessione", back_populates="messaggi")


engine= create_engine(f"sqlite:///{CARTELLA_DATI / 'jarvis.db'}")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)