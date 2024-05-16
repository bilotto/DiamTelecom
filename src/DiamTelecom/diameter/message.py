from .constants import *
from diameter.message.commands import *
from typing import List
from typing import NamedTuple
import logging
logger = logging.getLogger(__name__)
from ..helpers import convert_timestamp

class AVPs():

    FIELDS_SEPARATOR = "\|"
    
    def __init__(self):
        self.avps = {}

    def add_avp(self, key, value):
        self.avps[key] = value

    def set_avps(self, avps):
        self.avps = avps

    def get(self, key):
        return self.avps.get(key, None)

    def get_fields_string(self):
        message_fields = ""
        for key, value in self.avps.items():
            print(key, value)
            message_fields += f"{value}"
            if key != list(self.avps.keys())[-1]:
                message_fields += self.FIELDS_SEPARATOR
        return message_fields

class DiameterMessage:
    name: str
    message: Message
    timestamp: float
    session_id: str
    framed_ip_address: str
    
    def __init__(self, name, message):
        self.name = name
        self._message = message
        self.avps = AVPs()
        # Attributes to be set later
        self.timestamp = None
        self.session_id = None
        self.framed_ip_address = None
        self.parse_message()

    def __repr__(self) -> str:
        return f"DiameterMessage({self.name})"

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def set_session_id(self, session_id):
        self.session_id = session_id

    def set_framed_ip_address(self, framed_ip_address):
        self.framed_ip_address = framed_ip_address

    @property
    def time(self):
        if self.timestamp:
            return convert_timestamp(self.timestamp)
        return None

    def to_csv(self):
        return [
                self.time,
                self.name,
                self.framed_ip_address,
                self.avps.get_fields_string(),
                self.session_id,
                ]
    
    def get_message_attribute(self, attr_name):
        try:
            return getattr(self._message, attr_name)
        except AttributeError:
            # logger.error(f"Attribute {attr_name} not found in {self.name}")
            return None
        
    def parse_message(self):
        if self.get_message_attribute('qos_information'):
            self.avps.add_avp("qos_information", self.get_message_attribute('qos_information'))
        if self.get_message_attribute('charging_rule_install'):
            self.avps.add_avp("charging_rule_install", self.get_message_attribute('charging_rule_install'))
        if self.get_message_attribute('charging_rule_remove'):
            self.avps.add_avp("charging_rule_remove", self.get_message_attribute('charging_rule_remove'))
    
class DiameterMessages:
    messages: List[Message]

    def __init__(self):
        self.messages = []

    def add_message(self, message: DiameterMessage):
        if not isinstance(message, DiameterMessage):
            raise TypeError("Message must be of type DiameterMessage")
        if self.last_message and self.last_message.name == message.name:
            # print("Won't add message with same name")
            logging.error(f"Message with same name {message.name} already exists. Won't add to Session. Last message: {self.last_message.name}")
            return
        self.messages.append(message)
        return message

    def get_messages(self):
        return self.messages

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

def create_diameter_message(cmd_code, request_flag, cc_request_type=None) -> DiameterMessage:
    # Convert to right type
    cmd_code = int(cmd_code)
    request_flag = int(request_flag)
    if cc_request_type:
        cc_request_type = int(cc_request_type)

    # Initialize the variables
    message_name = "Unknown"
    message_object = None

    if cmd_code == CMD_CREDIT_CONTROL:
        if cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
            message_name = CCR_I if request_flag else CCA_I
            message_object = CreditControlRequest() if request_flag else CreditControlAnswer()
            message_object.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
        elif cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
            message_name = CCR_U if request_flag else CCA_U
            message_object = CreditControlRequest() if request_flag else CreditControlAnswer()
            message_object.cc_request_type = E_CC_REQUEST_TYPE_UPDATE_REQUEST
        elif cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
            message_name = CCR_T if request_flag else CCA_T
            message_object = CreditControlRequest() if request_flag else CreditControlAnswer()
            message_object.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST

    elif cmd_code == CMD_RE_AUTH:
        message_name = RAR if request_flag else RAA
        message_object = ReAuthRequest() if request_flag else ReAuthAnswer()

    elif cmd_code == CMD_AA:
        message_name = AAR if request_flag else AAA
        message_object = AaRequest() if request_flag else AaAnswer()

    elif cmd_code == CMD_SESSION_TERMINATION:
        message_name = STR if request_flag else STA
        message_object = SessionTerminationRequest() if request_flag else SessionTerminationAnswer()

    elif cmd_code == CMD_ABORT_SESSION:
        message_name = ASR if request_flag else ASA
        message_object = AbortSessionRequest() if request_flag else AbortSessionAnswer()

    elif cmd_code == CMD_SPENDING_LIMIT:
        message_name = SLR if request_flag else SLA
        message_object = SpendingLimitRequest() if request_flag else SpendingLimitAnswer()

    elif cmd_code == CMD_SPENDING_STATUS_NOTIFICATION:
        message_name = SSNR if request_flag else SSNA
        message_object = SpendingStatusNotificationRequest() if request_flag else SpendingStatusNotificationAnswer()

    elif cmd_code == CMD_DEVICE_WATCHDOG:
        message_name = DWR if request_flag else DWA
        message_object = DeviceWatchdogRequest() if request_flag else DeviceWatchdogAnswer()

    elif cmd_code == CMD_CAPABILITIES_EXCHANGE:
        message_name = CER if request_flag else CEA
        message_object = CapabilitiesExchangeRequest() if request_flag else CapabilitiesExchangeAnswer()
    return DiameterMessage(message_name, message_object)

def create_diameter_message_from_message(message: Message):
    cmd_code = int(message.header.command_code)
    request_flag = message.header.is_request
    # Initialize the variables
    message_name = "Unknown"
    message_object = message
    if cmd_code == CMD_CREDIT_CONTROL:
        cc_request_type = message.cc_request_type
        if cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
            message_name = CCR_I if request_flag else CCA_I
        elif cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
            message_name = CCR_U if request_flag else CCA_U
        elif cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
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

    return DiameterMessage(message_name, message_object)

def name_diameter_message(cmd_code, request_flag, cc_request_type=None):
    cmd_code = int(cmd_code)
    request_flag = int(request_flag)
    if cmd_code == CMD_CREDIT_CONTROL:
        cc_request_type = int(cc_request_type)
        if cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
            message_name = CCR_I if request_flag else CCA_I
        elif cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
            message_name = CCR_U if request_flag else CCA_U
        elif cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
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

# class DiameterMessage:
#     def __init__(self,
#                  request_flag,
#                  app_id,
#                  cmd_code,
#                  pkt=None):
#         self.request_flag = int(request_flag)
#         self.app_id = app_id
#         self.cmd_code = cmd_code
#         self.session_id = None
#         self.framed_ip_address = None
#         self.cc_request_type = None
#         self.cc_request_number = None
#         #
#         if pkt:
#             self.parse_pkt(pkt)


#     @property
#     def next_message(self) -> NamedTuple:
#         if self.request_flag:
#             return next_message(0, self.cmd_code)
#         else:
#             return next_message(1, None)

#     @property
#     def interface(self):
#         if self.app_id == APP_3GPP_GX:
#             return "Gx"
#         elif self.app_id == APP_3GPP_RX:
#             return "Rx"
#         elif self.app_id == APP_3GPP_SY:
#             return "Sy"
#         else:
#             return "Unknown" 

#     def parse_pkt(self, pkt):
#         self.session_id = pkt.diameter.session_id
#         self.framed_ip_address = pkt.diameter.get_field_value("framed_ip_address_ipv4")
#         self.cc_request_type = pkt.diameter.get_field_value("CC-Request-Type")
#         self.cc_request_number = pkt.diameter.get_field_value("CC-Request-Number")

#     def __repr__(self):
#         return f"{self.interface},{self.name}"



# expected_message = {
#     "CCR-I": "CCA-I",
#     "CCR-U": "CCA-U",
#     "CCR-T": "CCA-T",
#     "RAR": "RAA",
#     "AAR": "AAA",
#     "STR": "STA",
#     "ASR": "ASA",
#     "SLR": "SLA",
#     "SSNR": "SSNA",
#     "DWR": "DWA",
#     "CER": "CEA"
#     }