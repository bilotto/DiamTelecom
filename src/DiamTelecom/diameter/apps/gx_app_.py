from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import GxSessions, GxSession
from diameter.message.constants import *
from diameter.message.commands import *

class GxApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GxSessions()
        self.sy_app = None
