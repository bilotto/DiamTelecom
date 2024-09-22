from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import RxSessions, RxSession

class RxApplication(CustomSimpleThreadingApplication):
    sessions: RxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler, dsc_app)
        self.sessions = RxSessions()
