from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import GySessions, GySession

class GyApplication(CustomSimpleThreadingApplication):
    sessions: GySessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GySessions()