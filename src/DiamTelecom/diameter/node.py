from diameter.node import Node
from diameter.message.constants import *
from .app import GxApplication, handle_request_pcef, handle_request_pcrf
from .create_nodes import *


class PCRF:
    def __init__(self, origin_host, origin_realm, ip_addresses, tcp_port, peers_gx: list, max_threads=10):
        self.node = Node(origin_host, origin_realm, ip_addresses=ip_addresses, tcp_port=tcp_port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
        self.app = create_gx_app(max_threads, handle_request_pcrf)
        peers = add_peers(self.node, peers_gx)
        self.node.add_application(self.app, peers)

    def start(self):
        self.node.start()
        self.app.wait_for_ready()



class PCEF:
    def __init__(self, origin_host, origin_realm, ip_addresses, tcp_port, peers_gx, max_threads=10):
        self.node = Node(origin_host, origin_realm, ip_addresses=ip_addresses, tcp_port=tcp_port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
        self.app = create_gx_app(max_threads, handle_request_pcef)
        peers = add_peers(self.node, peers_gx)
        self.node.add_application(self.app, peers)

    def start(self):
        self.node.start()
        self.app.wait_for_ready()
