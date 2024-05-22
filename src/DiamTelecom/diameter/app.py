from diameter.node import Node
from diameter.node.node import Peer
from diameter.node.application import SimpleThreadingApplication
from .session import *
from typing import List, Dict

class CustomSimpleThreadingApplication(SimpleThreadingApplication):
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = DiameterSessions()
        self.started = False

    def get_session_by_id(self, session_id: str) -> DiameterSession:
        return self.sessions.get_diameter_session(session_id)
    
    def get_subscriber_sessions_by_msisdn(self, msisdn: int):
        return self.sessions.get_msisdn_sessions(msisdn)
    
    def get_subscriber_active_session(self, msisdn: int):
        if self.sessions.get_msisdn_sessions(msisdn):
            for session in self.sessions.get_msisdn_sessions(msisdn):
                if session.active:
                    return session
        
    def custom_start(self):
        if not self.started:
            self.node.start()
            self.wait_for_ready()
            self.started = True

    def custom_stop(self):
        if self.started:
            self.node.stop()
            self.started = False

class GxApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GxSessions()

class RxApplication(CustomSimpleThreadingApplication):
    sessions: RxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = RxSessions()

class SyApplication(CustomSimpleThreadingApplication):
    sessions: SySessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = SySessions()
        self.subscribers = None


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

def create_rx_app(max_threads, request_handler) -> RxApplication:
    return RxApplication(APP_3GPP_RX, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=request_handler)

def create_sy_app(max_threads, request_handler) -> SyApplication:
    return SyApplication(APP_3GPP_SY, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=request_handler)
