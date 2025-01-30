from diameter.node import Node
from diameter.message.constants import *
from diameter.node.node import Peer
from .app import *
from typing import List, Dict
from diameter.message.commands import *
from diameter.message.avp.grouped import *

def create_node(origin_host, realm, ip_addresses, port, sctp=False) -> Node:
    if not sctp:
        node = Node(origin_host, realm, ip_addresses=ip_addresses, tcp_port=port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
    else:
        node = Node(origin_host, realm, ip_addresses=ip_addresses, sctp_port=port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
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
    return GxApplication(APP_3GPP_GX,
                         is_acct_application=False,
                         is_auth_application=True,
                         max_threads=max_threads,
                         request_handler=request_handler,
                         )

def create_gy_app(max_threads, request_handler) -> GyApplication:
    return GyApplication(APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
                         is_acct_application=False,
                         is_auth_application=True,
                         max_threads=max_threads,
                         request_handler=request_handler,
                         )

def create_rx_app(max_threads, request_handler) -> RxApplication:
    return RxApplication(APP_3GPP_RX,
                         is_acct_application=False,
                         is_auth_application=True,
                         max_threads=max_threads,
                         request_handler=request_handler,
                         )

def create_sy_app(max_threads, request_handler) -> SyApplication:
    return SyApplication(APP_3GPP_SY,
                         is_acct_application=False,
                         is_auth_application=True,
                         max_threads=max_threads,
                         request_handler=request_handler,
                         )


