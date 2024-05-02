from typing import List
from .subscriber import Subscriber

class DiameterSession:
    subscriber: Subscriber
    session_id: str
    start_time: str
    end_time: str
    
    def __init__(self, subscriber, session_id: str):
        self.subscriber = subscriber
        self.session_id = session_id
        self.start_time = None
        self.end_time = None
   
    def set_start_time(self, start_time: str):
        self.start_time = start_time

    def set_end_time(self, end_time: str):
        self.end_time = end_time



class DiameterSessions:
    def __init__(self):
        self.diameter_sessions = {}  # Dicionário para armazenar as sessões

    def add_diameter_session(self, diameter_session: DiameterSession):
        # Adiciona a sessão usando o session_id como chave
        self.diameter_sessions[diameter_session.session_id] = diameter_session

    def get_diameter_session(self, session_id: str) -> DiameterSession:
        # Retorna a sessão com o session_id especificado ou levanta uma exceção se não encontrado
        if session_id in self.diameter_sessions:
            return self.diameter_sessions[session_id]
        raise ValueError("DiameterSession not found")

    def remove_diameter_session(self, session_id: str):
        # Remove a sessão com o session_id especificado ou levanta uma exceção se não encontrado
        if session_id in self.diameter_sessions:
            del self.diameter_sessions[session_id]
            return
        raise ValueError("DiameterSession not found")
