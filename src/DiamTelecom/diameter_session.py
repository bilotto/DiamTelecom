from .subscriber import Subscriber
from typing import List, Dict

class DiameterSession:
    subscriber: Subscriber
    session_id: str
    active: bool
    error: bool
    messages: list
    start_time: str
    end_time: str

    
    def __init__(self, subscriber, session_id: str):
        self.subscriber = subscriber
        self.session_id = session_id
        self.active = False
        self.error = False
        self.messages = []
        #
        self.start_time = None
        self.end_time = None
   
    def set_start_time(self, start_time: str):
        self.start_time = start_time

    def set_end_time(self, end_time: str):
        self.end_time = end_time

    def add_message(self, message):
        self.messages.append(message)

    @property
    def last_message(self):
        return self.messages[-1]
    
    @property
    def n_messages(self):
        return len(self.messages)

    @property
    def msisdn(self):
        return self.subscriber.msisdn
    
    @property
    def imsi(self):
        return self.subscriber.imsi

class DiameterSessions:
    diameter_sessions: Dict[str, DiameterSession]
    msisdn_to_session_id: Dict[str, List[str]]

    def __init__(self):
        self.diameter_sessions = {}  # Dicionário para armazenar as sessões
        self.msisdn_to_session_id = {}  # Dicionário para mapear MSISDNs para session_ids

    def add_diameter_session(self, diameter_session: DiameterSession):
        # Adiciona a sessão usando o session_id como chave
        self.diameter_sessions[diameter_session.session_id] = diameter_session
        # Mapeia o MSISDN para o session_id
        if not diameter_session.subscriber.msisdn in self.msisdn_to_session_id:
            self.msisdn_to_session_id[diameter_session.subscriber.msisdn] = []
        self.msisdn_to_session_id[diameter_session.subscriber.msisdn].append(diameter_session.session_id)

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
    
    def get_msisdn_sessions(self, msisdn: str) -> List[DiameterSession]:
        # Retorna uma lista de sessões associadas a um MSISDN específico
        if msisdn in self.msisdn_to_session_id:
            return [self.diameter_sessions[session_id] for session_id in self.msisdn_to_session_id[msisdn]]
        return []

    def create_diameter_session(self, subscriber: Subscriber, session_id: str) -> DiameterSession:
        # Cria uma nova sessão e a adiciona ao dicionário de sessões
        diameter_session = DiameterSession(subscriber, session_id)
        self.add_diameter_session(diameter_session)
        return diameter_session