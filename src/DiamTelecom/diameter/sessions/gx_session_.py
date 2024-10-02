
from .diameter_session import DiameterSession, DiameterSessions, Subscriber, DiameterMessage
from diameter.message.commands import CreditControlRequest
from diameter.message.avp.grouped import *
from .rx_session_ import RxSession
from typing import List, Dict
from ..constants import *
from DiamTelecom.helpers import ip_to_bytes

class GxSession(DiameterSession):
    session_id: str
    framed_ip_address: str
    apn: str
    rx_sessions: List[RxSession]

    def __init__(self,
                 subscriber,
                 session_id: str,
                 framed_ip_address: str,
                 apn: str = None,):
        super().__init__(subscriber, session_id)
        self.framed_ip_address = framed_ip_address
        self.apn = apn
        #
        self.cc_request_number = 0
        # self.mcc_mnc = None
        # self.rat_type = None
        # self.ip_can_type = None
        # self.destination_realm = None
        # self.qos_information = None
        # self.pcc_rules = []
        self.rx_sessions = []
        
    def __repr__(self):
        return f"""GxSession(msisdn={self.msisdn}
          session_id={self.session_id}
          active={self.active}
          n_messages={self.n_messages}
          last_message={self.last_message})

"""

    def incr_cc_request_number(self):
        self.cc_request_number += 1

    # def set_mcc_mnc(self, mcc_mnc: str):
    #     self.mcc_mnc = mcc_mnc

    # def set_apn(self, apn: str):
    #     if not isinstance(apn, str):
    #         raise ValueError("APN must be a string")
    #     self.apn = apn

    # def add_message(self, message):
    #     message = super().add_message(message)
    #     if message.name == CCR_I:
    #         self.set_apn(message._message.called_station_id)
    #     if self.start_time and self.messages.n_messages == 1:
    #         logger.info(f"{message.time},{message.pkt_number},{message.name},{self.subscriber.msisdn} started Gx session,{self.framed_ip_address}")
        
    #     elif self.end_time:
    #         if message.name == CCR_T:
    #             logger.info(f"{message.time},{message.pkt_number},{message.name},{self.subscriber.msisdn} ended Gx session,{self.framed_ip_address}")


    def add_rx_session(self, rx_session):
        self.rx_sessions.append(rx_session)

    @property
    def tshark_filter(self):
        filter = f"diameter.Framed-IP-Address.IPv4 == {self.framed_ip_address} || diameter.Session-Id == \"{self.session_id}\""
        for rx_session in self.rx_sessions:
            filter += f" || diameter.Session-Id == \"{rx_session.session_id}\""
        return filter
    
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
    
    def create_ccr_u(self):
        ccr_u = CreditControlRequest()
        ccr_u.session_id = self.session_id
        ccr_u.cc_request_type = E_CC_REQUEST_TYPE_UPDATE_REQUEST
        ccr_u.cc_request_number = self.cc_request_number + 1
        ccr_u.framed_ip_address = ip_to_bytes(self.framed_ip_address)
        ccr_u.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(self.msisdn))
        ccr_u.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(self.imsi))
        return ccr_u


class GxSessions(DiameterSessions):
    framed_ip_address_to_session_id: Dict[str, List[str]]
    apn_to_session_id: Dict[str, List[str]]

    def __init__(self):
        super().__init__()
        self.framed_ip_address_to_session_id = {}
        self.apn_to_session_id = {}

    def add_gx_session(self, gx_session: GxSession):
        self.add_session(gx_session)
        #
        # Here we want to fill two maps based on the session attributes framed_ip_address and apn
        framed_ip_address = gx_session.framed_ip_address
        apn = gx_session.apn
        if not framed_ip_address:
            raise ValueError("Framed IP Address is required")
        if not apn:
            raise ValueError("APN is required")
        #
        if self.framed_ip_address_to_session_id.get(gx_session.framed_ip_address) is None:
            self.framed_ip_address_to_session_id[gx_session.framed_ip_address] = []
        if self.apn_to_session_id.get(gx_session.apn) is None:
            self.apn_to_session_id[gx_session.apn] = []
        self.framed_ip_address_to_session_id[gx_session.framed_ip_address].append(gx_session.session_id)
        self.apn_to_session_id[gx_session.apn].append(gx_session.session_id)

    def get(self, session_id: str) -> GxSession:
        return self.diameter_sessions.get(session_id, None)
    
    def get_gx_session_by_framed_ip_address(self, framed_ip_address: str) -> GxSession:
        session_id_list = self.framed_ip_address_to_session_id.get(framed_ip_address)
        if session_id_list is None:
            raise ValueError(f"No GxSession found with framed IP address {framed_ip_address}")
        # Return the first active session
        for session_id in session_id_list:
            gx_session = self.get_session(session_id)
            # need to return the session even though its not active
            # it was causing a bug when Rx messages continue to be sent after the session is closed
            # if gx_session.active:
            #     return gx_session
            return gx_session

    def create_session(self, subscriber, session_id: str, framed_ip_address: str, apn: str) -> GxSession:
        gx_session = GxSession(subscriber, session_id, framed_ip_address, apn)
        self.add_gx_session(gx_session)
        return gx_session
    
    def add_message(self, session_id: str, message):
        self.get_session(session_id).add_message(message)

    def get_sessions_by_apn(self, apn: str) -> List[GxSession]:
        return [self.diameter_sessions[session_id] for session_id in self.apn_to_session_id.get(apn, [])]

    # def get_msisdn_sessions(self, msisdn: str) -> List[GxSession]:
    #     # Retorna uma lista de sessões associadas a um MSISDN específico
    #     if msisdn in self.msisdn_to_session_id:
    #         return [self.diameter_sessions[session_id] for session_id in self.msisdn_to_session_id[msisdn]]