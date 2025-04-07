from .custom_simple_threading_application import CustomSimpleThreadingApplication
from diameter.message.constants import *
from diameter.message.avp.grouped import *
from diameter.message.commands import *
from ..sessions import RxSessions, RxSession
# from ..handle_request import handle_request_rx


class RxApplication(CustomSimpleThreadingApplication):
    sessions: RxSessions
    def __init__(self, application_id=APP_3GPP_RX, is_acct_application=False, is_auth_application=True, max_threads=1, request_handler=None, name=None):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.name = name
        self.sessions = RxSessions()

    def get_session_by_id(self, session_id: str) -> RxSession:
        return self.sessions.get_session(session_id)