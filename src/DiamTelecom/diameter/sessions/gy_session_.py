
from .diameter_session import DiameterSession, DiameterSessions, Subscriber, DiameterMessage
from diameter.message.commands import CreditControlRequest
from diameter.message.avp.grouped import *
from .rx_session_ import RxSession
from typing import List, Dict
from ..constants import *
from DiamTelecom.helpers import ip_to_bytes

class GySession(DiameterSession):
    session_id: str
    framed_ip_address: str
    rx_sessions: List[RxSession]

    def __init__(self,
                 subscriber,
                 session_id: str,
                 framed_ip_address: str):
        super().__init__(subscriber, session_id)
        self.framed_ip_address = framed_ip_address
        self.cc_request_number = 0

    def __repr__(self):
        return f"GySession(n_messages={self.n_messages}, last_message={self.last_message})"

    def add_message(self, message):
        message = super().add_message(message)
        if self.start_time and self.messages.n_messages == 1:
            logger.info(f"{message.time},{message.pkt_number},{message.name},{self.subscriber.msisdn} started Gy session,{self.framed_ip_address}")
        
        elif self.end_time:
            if message.name == CCR_T:
                logger.info(f"{message.time},{message.pkt_number},{message.name},{self.subscriber.msisdn} ended Gy session,{self.framed_ip_address}")

    
    def create_ccr_i(self):
        ccr_i = CreditControlRequest()
        ccr_i.session_id = self.session_id
        ccr_i.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
        ccr_i.cc_request_number = 0
        ccr_i.framed_ip_address = ip_to_bytes(self.framed_ip_address)
        ccr_i.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(self.msisdn))
        ccr_i.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(self.imsi))
        return ccr_i
    
    def create_ccr_t(self):
        ccr_t = CreditControlRequest()
        ccr_t.session_id = self.session_id
        ccr_t.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST
        ccr_t.cc_request_number = self.cc_request_number + 1
        ccr_t.framed_ip_address = ip_to_bytes(self.framed_ip_address)
        ccr_t.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(self.msisdn))
        ccr_t.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(self.imsi))
        return ccr_t


class GySessions(DiameterSessions):
    framed_ip_address_to_session_id: Dict[str, List[str]]
    # msisdn_to_session_id: Dict[str, List[str]]

    def __init__(self):
        super().__init__()
        self.framed_ip_address_to_session_id = {}
        # self.msisdn_to_session_id = {}

    def add_gy_session(self, gy_session: GySession):
        self.add_session(gy_session)
        if self.framed_ip_address_to_session_id.get(gy_session.framed_ip_address) is None:
            self.framed_ip_address_to_session_id[gy_session.framed_ip_address] = []
        self.framed_ip_address_to_session_id[gy_session.framed_ip_address].append(gy_session.session_id)

    def get(self, session_id: str) -> GySession:
        return self.diameter_sessions.get(session_id, None)
    
    def get_gy_session_by_framed_ip_address(self, framed_ip_address: str) -> GySession:
        session_id_list = self.framed_ip_address_to_session_id.get(framed_ip_address)
        if session_id_list is None:
            raise ValueError(f"No GySession found with framed IP address {framed_ip_address}")
        # Return the first active session
        for session_id in session_id_list:
            gy_session = self.get_session(session_id)
            # need to return the session even though its not active
            # it was causing a bug when Rx messages continue to be sent after the session is closed
            # if gy_session.active:
            #     return gy_session
            return gy_session

    def create_session(self, subscriber, session_id: str, framed_ip_address: str) -> GySession:
        gy_session = GySession(subscriber, session_id, framed_ip_address)
        self.add_gy_session(gy_session)
        return gy_session
    
    def add_message(self, session_id: str, message):
        self.get_session(session_id).add_message(message)


    def get_msisdn_sessions(self, msisdn: str) -> List[GySession]:
        # Retorna uma lista de sessões associadas a um MSISDN específico
        if msisdn in self.msisdn_to_session_id:
            return [self.diameter_sessions[session_id] for session_id in self.msisdn_to_session_id[msisdn]]