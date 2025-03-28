
from DiamTelecom.telecom import Subscriber
from ..message import Message, DiameterMessage, DiameterMessages
from typing import Dict, List, Set
import time
import logging
from diameter.message import dump
from ..helpers import generate_xml
import os
logger = logging.getLogger("DiamTelecom.diameter.session")

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
        self.logger = logging.getLogger("DiamTelecom.diameter.session")

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
        if not self.active:
            self.set_start_time(str(time.time()))

    def end(self):
        if self.active:
            self.set_end_time(str(time.time()))

    def set_end_time(self, end_time: str):
        self.end_time = end_time
        self.active = False
        # self.logger.info(f"Session {self.session_id} ended at {self.end_time}")

    def add_message(self, message):
        if not isinstance(message, Message) and not isinstance(message, DiameterMessage):
            raise ValueError("message must be an instance of Message or DiameterMessage")
        if isinstance(message, DiameterMessage):
            diameter_message = message
        elif isinstance(message, Message):
            diameter_message = DiameterMessage(message)
        else:
            raise ValueError("message must be an instance of Message or DiameterMessage")
        #
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
        elif self.start_time:
            return int(time.time() - float(self.start_time))
        return None
    
    # def dump(self):
    #     for message in self.messages.messages:
    #         print(dump(message))

    # def dump_xml(self, folder_path="output"):
    #     for n, message in enumerate(self.messages.get_messages()):
    #         try:
    #             filename = f"{folder_path}/{self.msisdn}_{n}_{message.name}.xml"
    #             generate_xml(message._message, filename)
    #         except:
    #             pass

class DiameterSessions:
    diameter_sessions: Dict[str, DiameterSession]
    msisdn_to_session_id: Dict[str, Set[str]]

    def __init__(self):
        self.diameter_sessions = {}  # Dicionário para armazenar as sessões
        self.msisdn_to_session_id = {}  # Dicionário para mapear MSISDNs para session_ids

    @property
    def sessions(self):
        return self.diameter_sessions
    
    def values(self):
        return self.diameter_sessions.values()
    
    @property
    def n_active_sessions(self):
        return len([session for session in self.diameter_sessions.values() if session.active])

    def get(self, session_id: str) -> DiameterSession:
        return self.diameter_sessions.get(session_id, None)

    def add_session(self, diameter_session: DiameterSession):
        # Check if the session_id is already in the dictionary
        if diameter_session.session_id in self.diameter_sessions:
            if diameter_session.active:
                raise ValueError("DiameterSession already exists and is active")
        self.diameter_sessions[diameter_session.session_id] = diameter_session
        # Mapeia o MSISDN para o session_id
        if not diameter_session.subscriber.msisdn in self.msisdn_to_session_id:
            self.msisdn_to_session_id[diameter_session.subscriber.msisdn] = set()
        self.msisdn_to_session_id[diameter_session.subscriber.msisdn].add(diameter_session.session_id)

    def get_session(self, session_id: str) -> DiameterSession:
        return self.diameter_sessions.get(session_id)

    def remove_session(self, session_id: str):
        if not isinstance(session_id, str):
            raise ValueError(f"session_id must be a string. Passed: {session_id}")
        if session_id in self.diameter_sessions:
            del self.diameter_sessions[session_id]
            return
        raise ValueError("DiameterSession not found")
    
    def get_msisdn_sessions(self, msisdn: str) -> List[DiameterSession]:
        msisdn_sessions = []
        if msisdn in self.msisdn_to_session_id:
            for session_id in self.msisdn_to_session_id[msisdn]:
                session = self.get_session(session_id)
                if session:
                    msisdn_sessions.append(session)
        return msisdn_sessions
    
    def get_subscriber_active_session(self, msisdn: int):
        active_sessions = []
        if self.get_msisdn_sessions(msisdn):
            for session in self.get_msisdn_sessions(msisdn):
                if session.active:
                    active_sessions.append(session)
        if not active_sessions:
            return None
        if len(active_sessions) > 1:
            logger.warning(f"More than one active session found for MSISDN {msisdn}")
        return active_sessions[0]

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
