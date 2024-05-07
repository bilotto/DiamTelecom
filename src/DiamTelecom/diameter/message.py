
from diameter.message.constants import *
from diameter.message.commands import *
from typing import List
from typing import NamedTuple

next_message = NamedTuple("next_message", [("request_flag", int), ("cmd_code", int)])

request_message_name = {
    CMD_CREDIT_CONTROL: CreditControlRequest,
    CMD_RE_AUTH: ReAuthRequest,
    CMD_AA: AaRequest,
    CMD_SESSION_TERMINATION: SessionTerminationRequest,
    CMD_ABORT_SESSION: AbortSessionRequest,
    CMD_SPENDING_LIMIT: SpendingLimitRequest,
    CMD_SPENDING_STATUS_NOTIFICATION: SpendingStatusNotificationRequest,
    CMD_DEVICE_WATCHDOG: DeviceWatchdogRequest,
    CMD_CAPABILITIES_EXCHANGE: CapabilitiesExchangeRequest
    }

answer_message_name = {
    CMD_CREDIT_CONTROL: CreditControlAnswer,
    CMD_RE_AUTH: ReAuthAnswer,
    CMD_AA: AaAnswer,
    CMD_SESSION_TERMINATION: SessionTerminationAnswer,
    CMD_ABORT_SESSION: AbortSessionAnswer,
    CMD_SPENDING_LIMIT: SpendingLimitAnswer,
    CMD_SPENDING_STATUS_NOTIFICATION: SpendingStatusNotificationAnswer,
    CMD_DEVICE_WATCHDOG: DeviceWatchdogAnswer,
    CMD_CAPABILITIES_EXCHANGE: CapabilitiesExchangeAnswer
    }



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


class DiameterMessage:
    def __init__(self,
                 request_flag,
                 app_id,
                 cmd_code,
                 pkt=None):
        self.request_flag = int(request_flag)
        self.app_id = app_id
        self.cmd_code = cmd_code
        self.session_id = None
        self.framed_ip_address = None
        self.cc_request_type = None
        self.cc_request_number = None
        #
        if pkt:
            self.parse_pkt(pkt)

        self.name = name_diameter_message(self.cmd_code, self.request_flag, self.cc_request_type)

    @property
    def next_message(self) -> NamedTuple:
        if self.request_flag:
            return next_message(0, self.cmd_code)
        else:
            return next_message(1, None)

    @property
    def interface(self):
        if self.app_id == APP_3GPP_GX:
            return "Gx"
        elif self.app_id == APP_3GPP_RX:
            return "Rx"
        elif self.app_id == APP_3GPP_SY:
            return "Sy"
        else:
            return "Unknown"

    def parse_pkt(self, pkt):
        self.session_id = pkt.diameter.session_id
        self.framed_ip_address = pkt.diameter.get_field_value("framed_ip_address_ipv4")
        self.cc_request_type = pkt.diameter.get_field_value("CC-Request-Type")
        self.cc_request_number = pkt.diameter.get_field_value("CC-Request-Number")

    def __repr__(self):
        return f"{self.interface},{self.name}"
    

class DiameterMessages:
    messages: List[DiameterMessage]

    def __init__(self):
        self.messages = []


    def add_message(self, message: DiameterMessage):
        if self.n_messages != 0:
            expected_message = self.last_message.next_message
            if expected_message.request_flag != message.request_flag:
                print(f"Expected request_flag {expected_message.request_flag} but got {message.request_flag}")
                return
        self.messages.append(message)
        print(f"Next message: {message.next_message}")

    @property
    def last_message(self):
        return self.messages[-1]
    
    @property
    def n_messages(self):
        return len(self.messages)
    
    def __repr__(self):
        return f"DiameterMessages({self.messages})"




def name_diameter_message(cmd_code, request_flag, cc_request_type=None):
    # convert to right type
    cmd_code = int(cmd_code)
    request_flag = int(request_flag)
    if cc_request_type:
        cc_request_type = int(cc_request_type)
    if cmd_code == CMD_CREDIT_CONTROL:
        if request_flag:
            if cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
                message = "CCR-I"
                 
            elif cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
                message = "CCR-U"
            elif cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
                message = "CCR-T"
        else:
            if cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
                message = "CCA-I"
            elif cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
                message = "CCA-U"
            elif cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
                message = "CCA-T"
    elif cmd_code == CMD_RE_AUTH:
        if request_flag:
            message = "RAR"
        else:
            message = "RAA"
    elif cmd_code == CMD_AA:
        if request_flag:
            message = "AAR"
        else:
            message = "AAA"
    elif cmd_code == CMD_SESSION_TERMINATION:
        if request_flag:
            message = "STR"
        else:
            message = "STA"
    elif cmd_code == CMD_ABORT_SESSION:
        if request_flag:
            message = "ASR"
        else:
            message = "ASA"
    elif cmd_code == CMD_SPENDING_LIMIT:
        if request_flag:
            message = "SLR"
        else:
            message = "SLA"
    elif cmd_code == CMD_SPENDING_STATUS_NOTIFICATION:
        if request_flag:
            message = "SSNR"
        else:
            message = "SSNA"
    elif cmd_code == CMD_DEVICE_WATCHDOG:
        if request_flag:
            message = "DWR"
        else:
            message = "DWA"
    elif cmd_code == CMD_CAPABILITIES_EXCHANGE:
        if request_flag:
            message = "CER"
        else:
            message = "CEA"
    else:
        message = "Unknown"
    return message


def create_diameter_message(cmd_code, request_flag, cc_request_type=None):
    # convert to right type
    cmd_code = int(cmd_code)
    request_flag = int(request_flag)
    if cc_request_type:
        cc_request_type = int(cc_request_type)
    if cmd_code == CMD_CREDIT_CONTROL:
        if request_flag:
            if cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
                message = CreditControlRequest()
                message.
                message.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
                message.cc_request_number = 0
            elif cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
                message = CreditControlRequest()
                message.cc_request_type = E_CC_REQUEST_TYPE_UPDATE_REQUEST
                
            elif cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
                message = CreditControlRequest()
                message.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST
        else:
            if cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
                message = CreditControlAnswer()
                message.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
                message.cc_request_number = 0
            elif cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
                message = CreditControlAnswer()
                message.cc_request_type = E_CC_REQUEST_TYPE_UPDATE_REQUEST
            elif cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
                message = CreditControlAnswer()
                message.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST

    elif cmd_code == CMD_RE_AUTH:
        if request_flag:
            message = ReAuthRequest()
        else:
            message = ReAuthAnswer()
    elif cmd_code == CMD_AA:
        if request_flag:
            message = AaRequest()
        else:
            message = AaAnswer()
    elif cmd_code == CMD_SESSION_TERMINATION:
        if request_flag:
            message = SessionTerminationRequest()
        else:
            message = SessionTerminationAnswer()
    elif cmd_code == CMD_ABORT_SESSION:
        if request_flag:
            message = AbortSessionRequest()
        else:
            message = AbortSessionAnswer()
    elif cmd_code == CMD_SPENDING_LIMIT:
        if request_flag:
            message = SpendingLimitRequest()
        else:
            message = SpendingLimitAnswer()
    elif cmd_code == CMD_SPENDING_STATUS_NOTIFICATION:
        if request_flag:
            message = SpendingStatusNotificationRequest()
        else:
            message = SpendingStatusNotificationAnswer()
    return message