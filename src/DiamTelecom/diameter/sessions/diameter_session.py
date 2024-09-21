
from DiamTelecom.telecom import Subscriber
from ..message import Message, DiameterMessage, DiameterMessages, create_diameter_message_from_message
from typing import Dict, List, Set
import time

class DiameterSession:
    subscriber: Subscriber
    session_id: str
    active: bool
    error: bool
    messages: DiameterMessages
    start_time: str
    end_time: str

    def __init__(self, subscriber: Subscriber, session_id: str):
        if not isinstance(subscriber, Subscriber):
            raise ValueError("Subscriber must be an instance of Subscriber")
        if not isinstance(session_id, str):
            raise ValueError("session_id must be a string")
        self.subscriber = subscriber
        self.session_id = session_id
        self.active = False
        self.error = False
        self.messages = DiameterMessages()
        #
        self.start_time = None
        self.end_time = None

    def __hash__(self) -> int:
        return hash(self.session_id)
    
    def __eq__(self, other) -> bool:
        return self.session_id == other.session_id
    
    def __repr__(self):
        return f"DiameterSession(n_messages={self.n_messages}, last_message={self.last_message})"
   
    def set_start_time(self, start_time: str):
        self.start_time = start_time
        self.active = True

    def start(self):
        self.set_start_time(str(time.time()))

    def end(self):
        self.set_end_time(str(time.time()))

    def set_end_time(self, end_time: str):
        self.end_time = end_time
        self.active = False

    def add_message(self, message):
        if isinstance(message, DiameterMessage):
            diameter_message = message
        elif isinstance(message, Message):
            diameter_message = create_diameter_message_from_message(message)
        diameter_message.msisdn = self.subscriber.msisdn
        return self.messages.add_message(diameter_message)

    def get_messages(self):
        return self.messages.messages

    @property
    def last_message(self):
        return self.messages.last_message
    
    @property
    def n_messages(self):
        return self.messages.n_messages

    @property
    def msisdn(self):
        return self.subscriber.msisdn
    
    @property
    def imsi(self):
        return self.subscriber.imsi
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return int(float(self.end_time) - float(self.start_time))
        return None

class DiameterSessions:
    diameter_sessions: Dict[str, DiameterSession]
    msisdn_to_session_id: Dict[str, Set[str]]

    def __init__(self):
        self.diameter_sessions = {}  # Dicionário para armazenar as sessões
        self.msisdn_to_session_id = {}  # Dicionário para mapear MSISDNs para session_ids

    def get(self, session_id: str) -> DiameterSession:
        return self.diameter_sessions.get(session_id, None)

    def add_session(self, diameter_session: DiameterSession):
        # Adiciona a sessão usando o session_id como chave
        self.diameter_sessions[diameter_session.session_id] = diameter_session
        # Mapeia o MSISDN para o session_id
        if not diameter_session.subscriber.msisdn in self.msisdn_to_session_id:
            self.msisdn_to_session_id[diameter_session.subscriber.msisdn] = set()
        self.msisdn_to_session_id[diameter_session.subscriber.msisdn].add(diameter_session.session_id)

    def get_session(self, session_id: str) -> DiameterSession:
        return self.diameter_sessions.get(session_id)

    def remove_session(self, session_id: str):
        if session_id in self.diameter_sessions:
            del self.diameter_sessions[session_id]
            return
        raise ValueError("DiameterSession not found")
    
    def get_msisdn_sessions(self, msisdn: str) -> List[DiameterSession]:
        if msisdn in self.msisdn_to_session_id:
            return [self.diameter_sessions[session_id] for session_id in self.msisdn_to_session_id[msisdn]]
        return []
    
    def get_subscriber_active_session(self, msisdn: int):
        if self.get_msisdn_sessions(msisdn):
            for session in self.get_msisdn_sessions(msisdn):
                if session.active:
                    return session

    def create_diameter_session(self, subscriber: Subscriber, session_id: str) -> DiameterSession:
        # Needs to be implemented in the upper classes
        pass
    
    def add_message(self, session_id: str, message: DiameterMessage):
        self.get_session(session_id).add_message(message)

    def get_all(self) -> List[DiameterSession]:
        return list(self.diameter_sessions.values())
    
    @property
    def all_msisdn(self):
        return list(self.msisdn_to_session_id.keys())
