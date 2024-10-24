from .custom_simple_threading_application import CustomSimpleThreadingApplication
from diameter.message.constants import *
from diameter.message.avp.grouped import *
from diameter.message.commands import *
from ..sessions import RxSessions, RxSession


class RxApplication(CustomSimpleThreadingApplication):
    sessions: RxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = RxSessions()
