from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import SySessions
from DiamTelecom.telecom.subscriber import Subscribers

class SyApplication(CustomSimpleThreadingApplication):
    sessions: SySessions
    subscribers: Subscribers
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = SySessions()
        self.subscribers = None 

    def set_subscribers(self, subscribers: Subscribers):
        self.subscribers = subscribers
