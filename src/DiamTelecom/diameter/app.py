from diameter.node.application import SimpleThreadingApplication, Node
from DiamTelecom.telecom import Subscribers
from .session import *
import logging

class CustomSimpleThreadingApplication(SimpleThreadingApplication):
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = DiameterSessions()
        self.dsc_app = dsc_app
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
        try:
            answer = self.send_request(request, timeout)
            return answer
        except Exception as e:
            raise e
        
class GxApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app)
        self.sessions = GxSessions()

    def get_subscriber_active_session(self, msisdn: int) -> GxSession:
        if self.sessions.get_msisdn_sessions(msisdn):
            for session in self.sessions.get_msisdn_sessions(msisdn):
                if session.active:
                    return session

class GyApplication(CustomSimpleThreadingApplication):
    sessions: GySessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app)
        self.sessions = GySessions()

class RxApplication(CustomSimpleThreadingApplication):
    sessions: RxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app)
        self.sessions = RxSessions()

class SyApplication(CustomSimpleThreadingApplication):
    sessions: SySessions
    subscribers: Subscribers
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app)
        self.sessions = SySessions()
        self.subscribers = None 

    def set_subscribers(self, subscribers: Subscribers):
        self.subscribers = subscribers

from typing import List, Dict

class DiameterApplications:
    apps_per_id: Dict[int, List[CustomSimpleThreadingApplication]]
    apps_per_node: Dict[Node, List[CustomSimpleThreadingApplication]]
    def __init__(self):
        self.apps_per_id = {}
        self.apps_per_node = {}

    def add_application(self, app: CustomSimpleThreadingApplication):
        if not isinstance(app, CustomSimpleThreadingApplication):
            raise Exception("Application is not CustomSimpleThreadingApplication")
        if not self.apps_per_id.get(app.application_id):
            self.apps_per_id[app.application_id] = []
        self.apps_per_id[app.application_id].append(app)
        #
        node = app.node
        if self.apps_per_node.get(node) is None:
            self.apps_per_node[node] = []
        self.apps_per_node[node].append(app)

    @property
    def nodes(self) -> List[Node]:
        return list(self.apps_per_node.keys())
    
    @property
    def apps(self) -> List[CustomSimpleThreadingApplication]:
        apps = []
        for app_list in self.apps_per_id.values():
            apps.extend(app_list)
        return apps
    
    @property
    def ports(self) -> List[int]:
        ports = set()
        for node in self.nodes:
            ports.add(node.tcp_port)
            for peer in node.peers.values():
                ports.add(peer.port)
        return list(ports)
    
    def start(self):
        import threading
        threads = []
        for node in self.nodes:
            t = threading.Thread(target=node.start)
            threads.append(t)
            t.start()
            print(f"Node {node} started")
        for t in threads:
            t.join()                                                                                                                        
        print("Nodes started")

    def wait_for_ready(self, timeout=30):
        for app in self.apps:
            app.wait_for_ready(timeout)
            print(f"App {app} ready")

    def stop(self):
        import threading
        threads = []
        for node in self.nodes:
            t = threading.Thread(target=node.stop)
            threads.append(t)
            t.start()
            print(f"Node {node} stopping")
        for t in threads:
            t.join()
        print("Nodes stopped")