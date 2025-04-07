from .constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from typing import List
import logging
logger = logging.getLogger(__name__)
from ..helpers import convert_timestamp
from DiamTelecom.services.ip_queue import bytes_to_ip
from DiamTelecom.telecom import Subscriber
import ipaddress


def decode_framed_ipv6(raw_bytes):
    try:
        reserved_byte = raw_bytes[0]
        prefix_length = raw_bytes[1]
        ipv6_prefix_bytes = raw_bytes[2:]
        ipv6_prefix_bytes_padded = ipv6_prefix_bytes.ljust(16, b'\x00')
        ipv6_address = ipaddress.IPv6Address(ipv6_prefix_bytes_padded)
        return f"{ipv6_address}/{prefix_length}"
    except:
        return None


def parse_subscription_id(subscription_id: List[SubscriptionId]):
    msisdn = None
    imsi = None
    sip_uri = None
    for i in subscription_id:
        if i.subscription_id_type == E_SUBSCRIPTION_ID_TYPE_END_USER_E164:
            msisdn = i.subscription_id_data
        elif i.subscription_id_type == E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI:
            imsi = i.subscription_id_data
        elif i.subscription_id_type == E_SUBSCRIPTION_ID_TYPE_END_USER_SIP_URI:
            sip_uri = i.subscription_id_data
    return (msisdn, imsi, sip_uri)

import logging
from diameter.message import Message

logger = logging.getLogger(__name__)

class DiameterMessage:
    def __init__(self, obj):
        if isinstance(obj, Message):
            self.message = obj
        elif isinstance(obj, str):
            try:
                hex_string = obj.strip().replace(':', '')
                message_bytes = bytes.fromhex(hex_string)
                self.message = Message.from_bytes(message_bytes)
            except ValueError:
                raise ValueError("Invalid hex string provided.")
        else:
            raise TypeError(f"Parameter must be a hex string or a Message instance. Provided: {obj},{type(obj)}")
        
        self.timestamp = None
        self.subscriber = None
        self.pkt_number = None
        logger.debug(f"Created DiameterMessage: {self.message.__class__.__name__}")
    
    def __getattr__(self, attr):
        """
        Delegate attribute access to the inner Message object
        """
        return getattr(self.message, attr)

    def __str__(self):
        return str(self.message)

    def __repr__(self):
        return repr(self.message)

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def set_subscriber(self, subscriber: Subscriber):
        if not isinstance(subscriber, Subscriber):
            raise ValueError("Subscriber must be an instance of Subscriber")
        self.subscriber = subscriber

    @property
    def name(self):
        return name_diameter_message_new(self)
    
    @property
    def app_id(self):
        return self.message.header.application_id
    
    @property
    def subscription_id(self):
        if self.message.subscription_id:
            return parse_subscription_id(self.message.subscription_id)
        return None
    
    @property
    def framed_ip_address(self):
        if self.message.framed_ip_address:
            return bytes_to_ip(self.message.framed_ip_address)
        return None
    
    @property
    def framed_ipv6_prefix(self):
        if self.message.framed_ipv6_prefix:
            framed_ipv6_prefix = self.message.framed_ipv6_prefix
            if isinstance(framed_ipv6_prefix, list):
                framed_ipv6_prefix = framed_ipv6_prefix[0]
            return decode_framed_ipv6(framed_ipv6_prefix)
        return None
    
    @property
    def apn(self):
        if self.message.called_station_id:
            return self.message.called_station_id
        return None
    
    @property
    def session_id(self):
        return self.message.session_id
    
    @property
    def is_request(self):
        return self.message.header.is_request

    
    @property
    def time(self):
        if self.timestamp:
            return convert_timestamp(self.timestamp)
        return None
    
    @property
    def hex_string(self):
        return self.message.as_bytes().hex()
    
    @property
    def result_code(self):
        if not self.is_request:
            if hasattr(self.message, "result_code") and self.message.result_code:
                return self.message.result_code
        return None

    def __repr__(self):
        return f"DiameterMessage({self.name}, {self.time})"
    
    def dump_hex_string(self, file_full_path):
        print(file_full_path)
        with open(file_full_path, 'w') as f:
            f.write(self.hex_string)
        logger.info(f"Hex string written to {file_full_path}")


def check_charging_rule_remove(diameter_message: DiameterMessage):
    message = diameter_message.message
    pcc_rules = set()
    try:
        if hasattr(message, "charging_rule_remove") and message.charging_rule_remove:
            for i in message.charging_rule_remove:
                if i.charging_rule_base_name:
                    for j in i.charging_rule_base_name:
                        pcc_rules.add(j)
                if i.charging_rule_name:
                    for j in i.charging_rule_name:
                        pcc_rules.add(j)
                if i.charging_rule_definition:
                    for j in i.charging_rule_definition:
                        charging_rule_name = j.charging_rule_name
                        pcc_rules.add(charging_rule_name)
            return pcc_rules
    except Exception as e:
        logger.error(f"Error then trying to remove pcc_rules from GxSession: {e}. This error is not relevant to the flow")

def check_charging_rule_install(diameter_message: DiameterMessage):
    message = diameter_message.message
    pcc_rules = set()
    try:
        if hasattr(message, "charging_rule_install") and message.charging_rule_install:
            for i in message.charging_rule_install:
                if i.charging_rule_base_name:
                    for j in i.charging_rule_base_name:
                        pcc_rules.add(j)
                if i.charging_rule_name:
                    for j in i.charging_rule_name:
                        pcc_rules.add(j)
                if i.charging_rule_definition:
                    for j in i.charging_rule_definition:
                        charging_rule_name = j.charging_rule_name
                        pcc_rules.add(charging_rule_name)
            return pcc_rules
    except Exception as e:
        logger.error(f"Error then trying to add pcc_rules from GxSession: {e}. This error is not relevant to the flow")


def check_qos(diameter_message: DiameterMessage):
    message = diameter_message.message
    try:
        if hasattr(message, "default_eps_bearer_qos") and message.default_eps_bearer_qos:
                default_eps_bearer_qos = message.default_eps_bearer_qos
                qos_class_identifier = default_eps_bearer_qos.qos_class_identifier
                arp = default_eps_bearer_qos.allocation_retention_priority
                priority_level = arp.priority_level
                return qos_class_identifier, priority_level
        # if hasattr(message, "qos_information") and message.qos_information:
        #     qos_information = message.qos_information
    except:
        logger.error(f"Error then trying to set QoS attributes from GxSession")
        pass

def check_event_trigger(diameter_message: DiameterMessage):
    message = diameter_message.message
    event_trigger = []
    try:
        if hasattr(message, "event_trigger") and message.event_trigger:
            for i in message.event_trigger:
                event_trigger.append(i)
            return event_trigger
    except:
        logger.error(f"Error then trying to set Event Trigger from GxSession")
        pass

def check_rat_type(diameter_message: DiameterMessage):
    message = diameter_message.message
    try:
        if hasattr(message, "rat_type") and message.rat_type:
            return message.rat_type
    except:
        logger.error(f"Error then trying to set RAT Type from GxSession")
        pass




        

class DiameterMessages:
    messages: List[DiameterMessage]

    def __init__(self):
        self.messages = []
        self.logger = logging.getLogger(__name__)

    def add_message(self, message: DiameterMessage):
        self.messages.append(message)
        return message

    def get_messages(self) -> List[DiameterMessage]:
        return sorted(self.messages, key=lambda x: x.timestamp)

    @property
    def last_message(self) -> DiameterMessage:
        if self.n_messages == 0:
            return None
        return self.messages[-1]
    
    @property
    def n_messages(self):
        return len(self.messages)
    
    def __repr__(self):
        return f"DiameterMessages({self.n_messages}, {self.last_message})"
    
    def __len__(self):
        return len(self.messages)

def name_diameter_message(diameter_message: DiameterMessage):
    message_name = None
    cmd_code = diameter_message.message.header.command_code
    request_flag = diameter_message.message.header.is_request
    cc_request_type = None

    if cmd_code == CMD_CREDIT_CONTROL:
        cc_request_type = diameter_message.message.cc_request_type
        if cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
            message_name = CCR_I if request_flag else CCA_I
        elif cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
            message_name = CCR_U if request_flag else CCA_U
        elif cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
            message_name = CCR_T if request_flag else CCA_T

    elif cmd_code == CMD_RE_AUTH:
        message_name = RAR if request_flag else RAA

    elif cmd_code == CMD_AA:
        message_name = AAR if request_flag else AAA

    elif cmd_code == CMD_SESSION_TERMINATION:
        message_name = STR if request_flag else STA

    elif cmd_code == CMD_ABORT_SESSION:
        message_name = ASR if request_flag else ASA

    elif cmd_code == CMD_SPENDING_LIMIT:
        message_name = SLR if request_flag else SLA

    elif cmd_code == CMD_SPENDING_STATUS_NOTIFICATION:
        message_name = SSNR if request_flag else SSNA

    elif cmd_code == CMD_DEVICE_WATCHDOG:
        message_name = DWR if request_flag else DWA

    elif cmd_code == CMD_CAPABILITIES_EXCHANGE:
        message_name = CER if request_flag else CEA

    return message_name


def name_diameter_message_new(diameter_message: DiameterMessage):
    message = diameter_message.message
    if isinstance(message, CreditControl):
        if isinstance(message, CreditControlRequest):
            cc_request_type = message.cc_request_type
            if cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
                return CCR_I
            elif cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
                return CCR_U
            elif cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
                return CCR_T
        elif isinstance(message, CreditControlAnswer):
            cc_request_type = message.cc_request_type
            if cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
                return CCA_I
            elif cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
                return CCA_U
            elif cc_request_type and cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
                return CCA_T
    elif isinstance(message, ReAuth):
        return RAR if message.header.is_request else RAA
    elif isinstance(message, AbortSession):
        return ASR if message.header.is_request else ASA
    elif isinstance(message, SpendingLimit):
        return SLR if message.header.is_request else SLA
    elif isinstance(message, SpendingStatusNotification):
        return SSNR if message.header.is_request else SSNA
    elif isinstance(message, DeviceWatchdog):
        return DWR if message.header.is_request else DWA
    elif isinstance(message, CapabilitiesExchange):
        return CER if message.header.is_request else CEA
    elif isinstance(message, SessionTermination):
        return STR if message.header.is_request else STA
    elif isinstance(message, Aa):
        return AAR if message.header.is_request else AAA
    
    return None

