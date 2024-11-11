from diameter.node import Node
from .app import GxApplication, SyApplication, DiameterApplications
from .create_nodes import *
from .handle_request import *



# class PCEF:
#     def __init__(self, origin_host, origin_realm, ip_addresses, tcp_port, peers_gx, max_threads=10):
#         self.node = Node(origin_host, origin_realm, ip_addresses=ip_addresses, tcp_port=tcp_port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
#         self.apps = DiameterApplications()
#         gx_app = GxApplication(APP_3GPP_GX,
#                          is_acct_application=False,
#                          is_auth_application=True,
#                          max_threads=max_threads,
#                          request_handler=handle_request_pcef,
#                          )
#         peers = add_peers(self.node, peers_gx)
#         self.node.add_application(self.app, peers)

#     def start(self):
#         self.node.start()
#         self.app.wait_for_ready()

class OCS:
    def __init__(self, origin_host, origin_realm, ip_addresses, tcp_port):
        self.node = Node(origin_host, origin_realm, ip_addresses=ip_addresses, tcp_port=tcp_port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
        self.apps = DiameterApplications()

    def add_sy_app(self, peers_sy, realms=[], max_threads=10, handle_request=None):
        if not handle_request:
            app = SyApplication(APP_3GPP_SY, False, True, max_threads, handle_request_ocs)
        else:
            app = SyApplication(APP_3GPP_SY, False, True, max_threads, handle_request)
        peers = add_peers(self.node, peers_sy)
        self.node.add_application(app, peers, realms)
        self.apps.add_application(app)

    def start(self):
        self.node.start()



# class PCRF:
#     def __init__(self, origin_host, origin_realm, ip_addresses, tcp_port, peers_gx: list, max_threads=10):
#         self.node = Node(origin_host, origin_realm, ip_addresses=ip_addresses, tcp_port=tcp_port, vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
#         # self.app = create_gx_app(max_threads, handle_request_pcef_gx)
        
#         peers = add_peers(self.node, peers_gx)
#         self.node.add_application(self.app, peers)

#     def start(self):
#         self.node.start()
#         self.app.wait_for_ready()

