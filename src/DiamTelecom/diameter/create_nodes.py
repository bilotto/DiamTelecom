from diameter.node import Node
from diameter.message.constants import *
from diameter.node.node import Peer
from DiamTelecom.diameter.app import *
from typing import List, Dict
from diameter.message.commands import *
from diameter.message.avp.grouped import *

# def handle_request(app: CustomSimpleThreadingApplication, message):
#     answer = message.to_answer()
#     session_id = message.session_id
#     print(f"Received message {message} with session_id {session_id}")
#     try:
#         answer.session_id = message.session_id
#         answer.origin_host = app.node.origin_host.encode()
#         answer.origin_realm = app.node.realm_name.encode()
#         answer.destination_realm = message.origin_realm
#         answer.cc_request_type = E_CC_REQUEST_TYPE_EVENT_REQUEST
#         answer.cc_request_number = message.cc_request_number
#         answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
#         if isinstance(answer, CreditControlAnswer):
#             answer.cost_information = CostInformation()
#             answer.cost_information.unit_value = UnitValue()
#             answer.cost_information.unit_value.value_digits = 100
#             answer.cost_information.unit_value.exponent = 6
#             answer.cost_information.currency_code = 986

#     except Exception as e:
#         print(f"Error processing message: {e}")
#         answer.result_code = E_RESULT_CODE_DIAMETER_UNABLE_TO_DELIVER
#     return answer

def create_node(origin_host, realm, ip_addresses, tcp_port) -> Node:
    node = Node(origin_host, realm, ip_addresses=ip_addresses, tcp_port=tcp_port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
    node.idle_timeout = 20
    return node

def add_peers(node: Node, peers_list: List[Dict]) -> List[Peer]:
    return [node.add_peer(f"aaa://{peer['host']}:{peer['port']};transport=tcp",
                          peer['realm'],
                          ip_addresses=peer.get('ip_addresses'),
                          is_persistent=peer['is_persistent'],
                          is_default=peer.get('is_default', False))
            for peer in peers_list]


def create_gx_app(max_threads, request_handler) -> GxApplication:
    return GxApplication(APP_3GPP_GX, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=request_handler)

def create_gy_app(max_threads, request_handler) -> GyApplication:
    return GyApplication(APP_DIAMETER_CREDIT_CONTROL_APPLICATION, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=request_handler)

def create_rx_app(max_threads, request_handler) -> RxAppication:
    return RxAppication(APP_3GPP_RX, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=request_handler)

def create_sy_app(max_threads, request_handler) -> SyApplication:
    return SyApplication(APP_3GPP_SY, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=request_handler)


