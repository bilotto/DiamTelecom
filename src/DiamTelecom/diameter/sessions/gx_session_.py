
from .diameter_session import DiameterSession, DiameterSessions, Subscriber, DiameterMessage
from diameter.message.commands import *
from diameter.message.avp import *
from diameter.message.avp.grouped import *
from diameter.message.constants import *
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
        self.mcc_mnc = None
        self.rx_sessions = []
        self.pcc_rules = set()
        self.qos_class_identifier = None
        self.priority_level = None
        self.event_trigger = []
        self.framed_ipv6_prefix = None
        self.rat_type = None
        
    def __repr__(self):
        return f"""GxSession(msisdn={self.msisdn}
          framed_ip_address={self.framed_ip_address}
          session_id={self.session_id}
          active={self.active}
          n_messages={self.n_messages}
          last_message={self.last_message})

"""
    def __setattr__(self, name, value):
        if value is not None:
            if name == 'rat_type':
                if value == E_RAT_TYPE_UTRAN:
                    logger.info(f"Subscriber {self.subscriber.msisdn}, GxSession handover to 3G: {self.session_id}")
        return super().__setattr__(name, value)

    def incr_cc_request_number(self):
        self.cc_request_number += 1

    def set_mcc_mnc(self, mcc_mnc: str):
        self.mcc_mnc = mcc_mnc

    def add_rx_session(self, rx_session):
        self.rx_sessions.append(rx_session)

    @property
    def tshark_filter(self):
        filter = f"diameter.Framed-IP-Address.IPv4 == {self.framed_ip_address} || diameter.Session-Id == \"{self.session_id}\""
        for rx_session in self.rx_sessions:
            filter += f" || diameter.Session-Id == \"{rx_session.session_id}\""
        return filter
    
    def get_messages(self):
        messages = []
        for i in super().get_messages():
            messages.append(i)
        for rx_session in self.rx_sessions:
            for i in rx_session.get_messages():
                messages.append(i)
        return sorted(messages, key=lambda x: x.timestamp)
    
    def add_message(self, message: DiameterMessage):
        diameter_message = super().add_message(message)
        if diameter_message.name == CCA_I:
            if diameter_message.message.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
                self.start()
        elif diameter_message.name == CCA_T:
            if diameter_message.message.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
                self.end()
        try:
            check_charging_rules(self, diameter_message)
            check_qos(self, diameter_message)
            check_event_trigger(self, diameter_message)
            check_rat_type(self, diameter_message)
        except Exception as e:
            logger.error(f"Error when trying to set GxSession attributes Error: {e}")
        return diameter_message

    # todo: change to a functions file
    def create_ccr_i(self, ccr_i: CreditControlRequest = None):
        if not ccr_i:
            ccr_i = CreditControlRequest()
            ccr_i.session_id = self.session_id
            ccr_i.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
            ccr_i.cc_request_number = 0
            ccr_i.framed_ip_address = ip_to_bytes(self.framed_ip_address)
            ccr_i.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(self.msisdn))
            ccr_i.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(self.imsi))
        else:
            ccr_i.session_id = self.session_id
            ccr_i.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
            ccr_i.cc_request_number = 0
            ccr_i.subscription_id = []
            ccr_i.framed_ip_address = ip_to_bytes(self.framed_ip_address)
            ccr_i.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(self.msisdn))
            ccr_i.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(self.imsi))
        return ccr_i
    
    # todo: change to a functions file
    def create_ccr_t(self, ccr_t: CreditControlRequest = None):
        ccr_t = CreditControlRequest()
        ccr_t.session_id = self.session_id
        ccr_t.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST
        ccr_t.cc_request_number = self.cc_request_number + 1
        ccr_t.framed_ip_address = ip_to_bytes(self.framed_ip_address)
        ccr_t.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(self.msisdn))
        ccr_t.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(self.imsi))
        return ccr_t
    
    # todo: change to a functions file
    def create_ccr_u(self, ccr_u: CreditControlRequest = None):
        ccr_u = CreditControlRequest()
        ccr_u.session_id = self.session_id
        ccr_u.cc_request_type = E_CC_REQUEST_TYPE_UPDATE_REQUEST
        ccr_u.cc_request_number = self.cc_request_number + 1
        ccr_u.framed_ip_address = ip_to_bytes(self.framed_ip_address)
        ccr_u.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(self.msisdn))
        ccr_u.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(self.imsi))
        return ccr_u


def check_charging_rules(gx_session: GxSession, diameter_message: DiameterMessage):
    message = diameter_message.message
    try:
        if isinstance(message, CreditControlAnswer) or isinstance(message, ReAuthRequest):
            if message.charging_rule_install:
                for i in message.charging_rule_install:
                    if i.charging_rule_base_name:
                        for j in i.charging_rule_base_name:
                            gx_session.pcc_rules.add(j)
                    if i.charging_rule_name:
                        for j in i.charging_rule_name:
                            gx_session.pcc_rules.add(j)
                    if i.charging_rule_definition:
                        for j in i.charging_rule_definition:
                            charging_rule_name = j.charging_rule_name
                            gx_session.pcc_rules.add(charging_rule_name)
        if isinstance(message, ReAuthRequest):
            if message.charging_rule_remove:
                for i in message.charging_rule_remove:
                    if i.charging_rule_base_name:
                        for j in i.charging_rule_base_name:
                            gx_session.pcc_rules.remove(j)
                    if i.charging_rule_name:
                        for j in i.charging_rule_name:
                            gx_session.pcc_rules.remove(j)
                    if i.charging_rule_definition:
                        for j in i.charging_rule_definition:
                            charging_rule_name = j.charging_rule_name
                            gx_session.pcc_rules.remove(charging_rule_name)
        # logger.info(f"current pcc_rules: {gx_session.pcc_rules}")
    except Exception as e:
        logger.error(f"Error then trying to add/remove pcc_rules from GxSession: {e}. This error is not relevant to the flow")


def check_qos(gx_session: GxSession, diameter_message: DiameterMessage):
    message = diameter_message.message
    if hasattr(message, "default_eps_bearer_qos") and message.default_eps_bearer_qos:
            default_eps_bearer_qos = message.default_eps_bearer_qos
            qos_class_identifier = default_eps_bearer_qos.qos_class_identifier
            arp = default_eps_bearer_qos.allocation_retention_priority
            priority_level = arp.priority_level
            gx_session.qos_class_identifier = qos_class_identifier
            gx_session.priority_level = priority_level
    if hasattr(message, "qos_information") and message.qos_information:
        qos_information = message.qos_information

def check_event_trigger(gx_session: GxSession, diameter_message: DiameterMessage):
    message = diameter_message.message
    if hasattr(message, "event_trigger") and message.event_trigger:
        for i in message.event_trigger:
            gx_session.event_trigger.append(i)

def check_rat_type(gx_session: GxSession, diameter_message: DiameterMessage):
    message = diameter_message.message
    if hasattr(message, "rat_type") and message.rat_type:
        gx_session.rat_type = message.rat_type




class GxSessions(DiameterSessions):
    framed_ip_address_to_session_id: Dict[str, List[str]]
    apn_to_session_id: Dict[str, List[str]]

    def __init__(self):
        super().__init__()
        self.framed_ip_address_to_session_id = {}
        self.apn_to_session_id = {}
        self.framed_ipv6_prefix_to_session_id = {}

    def __repr__(self):
        return f"GxSessions({len(self.diameter_sessions)},{self.n_active_sessions})"

    def add_gx_session(self, gx_session: GxSession):
        if not isinstance(gx_session, GxSession):
            raise ValueError(f"Invalid GxSession: {gx_session}")
        self.add_session(gx_session)
        #
        # Here we want to fill two maps based on the session attributes framed_ip_address and apn
        framed_ip_address = gx_session.framed_ip_address
        apn = gx_session.apn
        # if not framed_ip_address:
        #     raise ValueError("Framed IP Address is required")
        # if not apn:
        #     raise ValueError("APN is required")
        #
        if gx_session.framed_ip_address:
            if self.framed_ip_address_to_session_id.get(gx_session.framed_ip_address) is None:
                self.framed_ip_address_to_session_id[gx_session.framed_ip_address] = []
            self.framed_ip_address_to_session_id[gx_session.framed_ip_address].append(gx_session.session_id)

        if gx_session.apn:
            if self.apn_to_session_id.get(gx_session.apn) is None:
                self.apn_to_session_id[gx_session.apn] = []
            self.apn_to_session_id[gx_session.apn].append(gx_session.session_id)
        
        if gx_session.framed_ipv6_prefix:
            if self.framed_ipv6_prefix_to_session_id.get(gx_session.framed_ipv6_prefix) is None:
                self.framed_ipv6_prefix_to_session_id[gx_session.framed_ipv6_prefix] = []
            self.framed_ipv6_prefix_to_session_id[gx_session.framed_ipv6_prefix].append(gx_session.session_id)

    def get(self, session_id: str) -> GxSession:
        return self.diameter_sessions.get(session_id, None)
    
    def get_session_by_id(self, session_id: str) -> GxSession:
        return self.get(session_id)
    
    def get_gx_session_by_framed_ip_address(self, framed_ip_address: str) -> GxSession:
        session_id_list = self.framed_ip_address_to_session_id.get(framed_ip_address)
        if session_id_list:
            for session_id in session_id_list:
                gx_session = self.get_session(session_id)
                return gx_session
        
    def gx_session_by_framed_ipv6_prefix(self, desired_framed_ipv6_prefix: str) -> GxSession:
        for framed_ipv6_prefix in self.framed_ipv6_prefix_to_session_id.keys():
            parsed_framed_ipv6_prefix = str(framed_ipv6_prefix.split("/")[0].replace("::", ""))
            if parsed_framed_ipv6_prefix in desired_framed_ipv6_prefix:
                session_id_list = self.framed_ipv6_prefix_to_session_id.get(framed_ipv6_prefix)
                for session_id in session_id_list:
                    gx_session = self.get_session(session_id)
                    return gx_session

        # else:
        #     for framed_ip_v6 in self.framed_ip_address_to_session_id.keys():
        #         if framed_ip_address in framed_ip_v6:
        #             session_id_list = self.framed_ip_address_to_session_id.get(framed_ip_v6)
        #             for session_id in session_id_list:
        #                 gx_session = self.get_session(session_id)
        #                 return gx_session

    def create_session(self, subscriber, session_id: str, framed_ip_address: str, apn: str) -> GxSession:
        gx_session = GxSession(subscriber, session_id, framed_ip_address, apn)
        self.add_gx_session(gx_session)
        return gx_session
    
    def add_message(self, session_id: str, message):
        self.get_session(session_id).add_message(message)

    def get_sessions_by_apn(self, apn: str) -> List[GxSession]:
        return [self.diameter_sessions[session_id] for session_id in self.apn_to_session_id.get(apn, [])]
    
    def remove_session(self, gx_session: GxSession):
        if not isinstance(gx_session, GxSession):
            raise ValueError(f"gx_session must be a GxSession object. Passed: {gx_session}")
        session_id = gx_session.session_id
        if session_id in self.diameter_sessions:
            del self.diameter_sessions[session_id]
        framed_ip_address = gx_session.framed_ip_address
        if self.framed_ip_address_to_session_id.get(framed_ip_address):
            session_list = self.framed_ip_address_to_session_id.get(framed_ip_address)
            if session_id in session_list:
                session_list.remove(session_id)
        if gx_session.apn:
            if self.apn_to_session_id.get(gx_session.apn):
                session_list = self.apn_to_session_id.get(gx_session.apn)
                if session_id in session_list:
                    session_list.remove(session_id)
        if gx_session.framed_ipv6_prefix:
            if self.framed_ipv6_prefix_to_session_id.get(gx_session.framed_ipv6_prefix):
                session_list = self.framed_ipv6_prefix_to_session_id.get(gx_session.framed_ipv6_prefix)
                if session_id in session_list:
                    session_list.remove(session_id)
        # raise ValueError("DiameterSession not found")

    # def get_msisdn_sessions(self, msisdn: str) -> List[GxSession]:
    #     # Retorna uma lista de sessões associadas a um MSISDN específico
    #     if msisdn in self.msisdn_to_session_id:
    #         return [self.diameter_sessions[session_id] for session_id in self.msisdn_to_session_id[msisdn]]
