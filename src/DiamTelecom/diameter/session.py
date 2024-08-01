from .constants import *
from .subscriber import Subscriber
from .message import DiameterMessage, DiameterMessages, Message, create_diameter_message_from_message
from typing import List, Dict, Set
import logging
logger = logging.getLogger(__name__)

class DiameterSession:
    subscriber: Subscriber
    session_id: str
    active: bool
    error: bool
    messages: DiameterMessages
    start_time: str
    end_time: str

    def __init__(self, subscriber: Subscriber, session_id: str):
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

    def set_end_time(self, end_time: str):
        self.end_time = end_time
        self.active = False

    def add_message(self, message):
        if isinstance(message, DiameterMessage):
            diameter_message = message
        elif isinstance(message, Message):
            diameter_message = create_diameter_message_from_message(message)
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

class DiameterSessions:
    diameter_sessions: Dict[str, DiameterSession]
    msisdn_to_session_id: Dict[str, Set[str]]

    def __init__(self):
        self.diameter_sessions = {}  # Dicionário para armazenar as sessões
        self.msisdn_to_session_id = {}  # Dicionário para mapear MSISDNs para session_ids

    def get(self, session_id: str) -> DiameterSession:
        return self.diameter_sessions.get(session_id, None)

    def add_session(self, diameter_session: DiameterSession):
        logger.debug(f"Adicionando sessão {diameter_session}")  
        # Adiciona a sessão usando o session_id como chave
        self.diameter_sessions[diameter_session.session_id] = diameter_session
        # Mapeia o MSISDN para o session_id
        if not diameter_session.subscriber.msisdn in self.msisdn_to_session_id:
            self.msisdn_to_session_id[diameter_session.subscriber.msisdn] = set()
        self.msisdn_to_session_id[diameter_session.subscriber.msisdn].add(diameter_session.session_id)

    def get_session(self, session_id: str) -> DiameterSession:
        # Retorna a sessão com o session_id especificado ou levanta uma exceção se não encontrado
        return self.diameter_sessions.get(session_id)

    def remove_session(self, session_id: str):
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
    
    def get_subscriber_active_session(self, msisdn: int):
        if self.get_msisdn_sessions(msisdn):
            for session in self.get_msisdn_sessions(msisdn):
                if session.active:
                    return session

    def create_diameter_session(self, subscriber: Subscriber, session_id: str) -> DiameterSession:
        # Needs to be implemented in the upper classes
        pass
    
    def add_message(self, session_id: str, message: DiameterMessage):
        # Adiciona uma mensagem a uma sessão específica
        self.get_session(session_id).add_message(message)

    def get_all(self) -> List[DiameterSession]:
        # Retorna uma lista de todas as sessões
        return list(self.diameter_sessions.values())
    
    @property
    def all_msisdn(self):
        return list(self.msisdn_to_session_id.keys())

class GxSession(DiameterSession):
    session_id: str
    framed_ip_address: str

    def __init__(self, subscriber, session_id: str, framed_ip_address: str):
        super().__init__(subscriber, session_id)
        self.framed_ip_address = framed_ip_address
        self.cc_request_number = 0
        self.mcc_mnc = None
        self.rat_type = None
        self.apn = None
        self.qos_information = None
        self.pcc_rules = []

    def __repr__(self):
        return (f"\nGxSession(Session ID: {self.session_id},\n"
                f"          IP Address: {self.framed_ip_address},\n"
                f"          MCC/MNC: {self.mcc_mnc},\n"
                f"          RAT Type: {self.rat_type},\n"
                f"          APN: {self.apn},\n"
                f"          QoS Info: {self.qos_information},\n"
                f"          PCC Rules: {self.pcc_rules})")
    
    def incr_cc_request_number(self):
        self.cc_request_number += 1

    
    def add_message(self, message):
        message = super().add_message(message)
        
        # if message.avps.get('qos_information'):
        #     if not self.qos_information:
        #         self.qos_information = message.avps.get('qos_information')
        #     else:
        #         if self.qos_information == message.avps.get('qos_information'):
        #             logger.info("QoS Mirror")
        #         else:
        #             logger.info("QoS not mirror")
        #         self.qos_information = message.avps.get('qos_information')
        # if message.avps.get('charging_rule_install'):
        #     charging_rule_install = message.avps.get('charging_rule_install')
        #     for item in charging_rule_install:
        #         for rule in item.charging_rule_base_name:
        #             self.pcc_rules.append(rule)
        #         for rule in item.charging_rule_name:
        #             self.pcc_rules.append(rule)
        # if message.avps.get('charging_rule_remove'):
        #     charging_rule_remove = message.avps.get('charging_rule_remove')
        #     for item in charging_rule_remove:
        #         for rule in item.charging_rule_base_name:
        #             self.pcc_rules.remove(rule)
        #         for rule in item.charging_rule_name:
        #             self.pcc_rules.remove(rule)
                    
class GxSessions(DiameterSessions):
    framed_ip_address_to_session_id: Dict[str, List[str]]
    # msisdn_to_session_id: Dict[str, List[str]]

    def __init__(self):
        super().__init__()
        self.framed_ip_address_to_session_id = {}
        # self.msisdn_to_session_id = {}

    def add_gx_session(self, gx_session: GxSession):
        self.add_session(gx_session)
        if self.framed_ip_address_to_session_id.get(gx_session.framed_ip_address) is None:
            self.framed_ip_address_to_session_id[gx_session.framed_ip_address] = []
        self.framed_ip_address_to_session_id[gx_session.framed_ip_address].append(gx_session.session_id)

    # def get_gx_session(self, session_id: str) -> GxSession:
    #     return self.get_session(session_id)
    
    def get(self, session_id: str) -> GxSession:
        return self.diameter_sessions.get(session_id, None)
    
    def get_gx_session_by_framed_ip_address(self, framed_ip_address: str) -> GxSession:
        session_id_list = self.framed_ip_address_to_session_id.get(framed_ip_address)
        if session_id_list is None:
            raise ValueError(f"No GxSession found with framed IP address {framed_ip_address}")
        # Return the first active session
        for session_id in session_id_list:
            gx_session = self.get_session(session_id)
            if gx_session.active:
                return gx_session
    
    # def get_gx_session_by_msisdn(self, msisdn: str) -> GxSession:
    #     session_id_list = self.msisdn_to_session_id.get(msisdn)
    #     if session_id_list is None:
    #         raise ValueError(f"No GxSession found with MSISDN {msisdn}")
    #     # Return the first active session
    #     for session_id in session_id_list:
    #         gx_session = self.get_gx_session(session_id)
    #         if gx_session.active:
    #             return gx_session

    # def remove_gx_session(self, session_id: str):
    #     self.remove_session(session_id)

    def create_session(self, subscriber, session_id: str, framed_ip_address: str) -> GxSession:
        gx_session = GxSession(subscriber, session_id, framed_ip_address)
        self.add_gx_session(gx_session)
        return gx_session
    
    def add_message(self, session_id: str, message):
        self.get_session(session_id).add_message(message)


class RxSession(DiameterSession):
    subscriber: Subscriber
    session_id: str
    gx_session_id: str

    def __init__(self, subscriber, session_id, gx_session_id):
        super().__init__(subscriber, session_id)
        self.gx_session_id = gx_session_id

    def set_gx_session_id(self, gx_session_id: str):
        self.gx_session_id = gx_session_id

    # def __repr__(self):
    #     return (f"\nGxSession(Session ID: {self.session_id},\n"
    #             f"          IP Address: {self.framed_ip_address},\n"
    #             f"          MCC/MNC: {self.mcc_mnc},\n"
    #             f"          RAT Type: {self.rat_type},\n"
    #             f"          APN: {self.apn},\n"
    #             f"          QoS Info: {self.qos_information},\n"
    #             f"          PCC Rules: {self.pcc_rules})")


class RxSessions(DiameterSessions):
    def __init__(self):
        super().__init__()

    def add_rx_session(self, rx_session: RxSession):
        self.add_session(rx_session)

    def get_rx_session(self, session_id: str) -> RxSession:
        return self.get_session(session_id)
    
    def get(self, session_id: str) -> RxSession:
        return self.diameter_sessions.get(session_id, None)

    # def remove_rx_session(self, session_id: str):
    #     self.remove_session(session_id)

    def create_session(self, subscriber, session_id: str, gx_session_id: str) -> RxSession:
        rx_session = RxSession(subscriber, session_id, gx_session_id)
        self.add_rx_session(rx_session)
        return rx_session



class SySession(DiameterSession):
    session_id: str
    gx_session_id: str

    def __init__(self, subscriber, session_id: str):
        super().__init__(subscriber, session_id)
        self.gx_session_id = None

    def set_gx_session_id(self, gx_session_id: str):
        self.gx_session_id = gx_session_id

class SySessions(DiameterSessions):
    def __init__(self):
        super().__init__()

    # def add_sy_session(self, sy_session: SySession):
    #     self.add_session(sy_session)

    # def get_sy_session(self, session_id: str) -> SySession:
    #     return self.get_session(session_id)
    
    def get(self, session_id: str) -> SySession:
        return self.diameter_sessions.get(session_id, None)

    # def remove_sy_session(self, session_id: str):
    #     self.remove_session(session_id)

    def create_sy_session(self, subscriber, session_id: str) -> SySession:
        sy_session = SySession(subscriber, session_id)
        self.add_session(sy_session)
        return sy_session
    
