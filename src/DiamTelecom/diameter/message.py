from .constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from typing import List
import logging
logger = logging.getLogger(__name__)
from ..helpers import convert_timestamp
from DiamTelecom.services.ip_queue import bytes_to_ip
from DiamTelecom.telecom import Subscriber

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

# def parse_charging_rules(message: Message):
#     output_dict = {}
#     output_dict['charging_rule_install'] = []
#     output_dict['charging_rule_remove'] = []
#     if hasattr(message, 'charging_rule_install'):
#         avp_charging_rule_install = message.charging_rule_install
#         for i in avp_charging_rule_install:
#             # print(i)
#             if i.charging_rule_name:
#                 for j in i.charging_rule_name:
#                     output_dict['charging_rule_install'].append(j)
#             if i.charging_rule_base_name:
#                 for j in i.charging_rule_base_name:
#                     output_dict['charging_rule_install'].append(j)
#             if i.charging_rule_definition:
#                 # print(i)
#                 for j in i.charging_rule_definition:
#                     for k in j:
#                         print(k)
#     # if hasattr(message, 'charging_rule_remove'):
#     #     avp_charging_rule_remove = message.charging_rule_remove
#     #     if hasattr(avp_charging_rule_remove, 'charging_rule_name'):
#     #         output_dict['charging_rule_remove'].append(avp_charging_rule_remove.charging_rule_name)
#     #     if hasattr(avp_charging_rule_remove, 'charging_rule_base_name'):
#     #         output_dict['charging_rule_remove'].append(avp_charging_rule_remove.charging_rule_base_name)
#     #     if hasattr(avp_charging_rule_remove, 'charging_rule_definition'):
#     #         output_dict['charging_rule_remove'].append(avp_charging_rule_remove.charging_rule_definition.charging_rule_name)
#     print(output_dict)
#     return output_dict



class DiameterMessage:
    hex_string: str
    message: Message
    
    def __init__(self, hex_string: str = None, message: Message = None):
        if not hex_string and not message:
            raise ValueError("hex_string or Message must be provided")
        if hex_string and message:
            raise ValueError("Only one of hex_string or Message must be provided")
        if message:
            if not isinstance(message, Message):
                raise TypeError("Message must be of type Message")
            self.message = message
        if hex_string:
            self.message = Message.from_bytes(hex_string)
        #
        self.timestamp = None
        self.subscriber = None

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def set_subscriber(self, subscriber: Subscriber):
        if not isinstance(subscriber, Subscriber):
            raise ValueError("Subscriber must be an instance of Subscriber")
        self.subscriber = subscriber

    @property
    def name(self):
        return name_diameter_message(self)
    
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

    def __repr__(self):
        return f"DiameterMessage({self.name}, {self.time})"
    
    def charging_rules(self):
        return parse_charging_rules(self.message)
    

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
