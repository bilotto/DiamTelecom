from diameter.node import Node
from diameter.constants import *
from diameter.node.node import Peer
from DiamTelecom.diameter.app import *
from typing import List, Dict

def handle_request(app: CustomSimpleThreadingApplication, message):
    pass

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


def create_gx_app(max_threads) -> GxApplication:
    return GxApplication(APP_3GPP_GX, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=handle_request)

def create_rx_app(max_threads) -> RxAppication:
    return RxAppication(APP_3GPP_RX, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=handle_request)

def create_sy_app(max_threads) -> SyApplication:
    return SyApplication(APP_3GPP_SY, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=handle_request)


