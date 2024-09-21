from diameter.node.application import SimpleThreadingApplication, Node
from .session import *
import logging

class CustomSimpleThreadingApplication(SimpleThreadingApplication):
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = DiameterSessions()
        # self.started = False
        # self.init_connection = False

    def get_session_by_id(self, session_id: str) -> DiameterSession:
        return self.sessions.get_session(session_id)
    
    def get_subscriber_sessions_by_msisdn(self, msisdn: int):
        return self.sessions.get_msisdn_sessions(msisdn)
    
    def get_subscriber_active_session(self, msisdn: int):
        if self.sessions.get_msisdn_sessions(msisdn):
            for session in self.sessions.get_msisdn_sessions(msisdn):
                if session.active:
                    return session
                

    def send_request_custom(self, request, timeout=5):
        # logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
        try:
            answer = self.send_request(request, timeout)
            # logging.getLogger("diameter.peer.msg").setLevel(logging.ERROR)
            return answer
        except Exception as e:
            raise e
        
class GxApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GxSessions()

class GyApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GySessions()

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

    def set_subscribers(self, subscribers):
        self.subscribers = subscribers

from typing import List

class DiameterApplications:
    def __init__(self):
        self.apps_per_id = {}
        self.apps_per_node = {}

    def add_application(self, app: CustomSimpleThreadingApplication):
        self.apps_per_id[app.application_id] = app
        node = app.node
        if self.apps_per_node.get(node) is None:
            self.apps_per_node[node] = []
        self.apps_per_node[node].append(app)

    @property
    def nodes(self) -> List[Node]:
        return list(self.apps_per_node.keys())
    
    @property
    def apps(self) -> List[CustomSimpleThreadingApplication]:
        return list(self.apps_per_id.values())
    
    def start(self):
        for node in self.nodes:
            node.start()
            print(f"Node {node} started")

    def wait_for_ready(self, timeout=30):
        for app in self.apps:
            app.wait_for_ready(timeout)
            print(f"App {app} ready")

    def stop(self):
        for node in self.nodes:
            node.stop()
            print(f"Node {node} stopped")