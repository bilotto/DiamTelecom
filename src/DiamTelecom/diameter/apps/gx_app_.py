from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import GxSessions, GxSession
from diameter.message.constants import APP_3GPP_GX
# from diameter.message.commands import *
# from ..handle_request import handle_request_gx

class GxApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id=APP_3GPP_GX, is_acct_application=False, is_auth_application=True, max_threads=1, request_handler=None):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GxSessions()
        self.sy_app = None


    def __repr__(self):
        return f"GxApplication({self.application_id})"
    
    def get_session_by_id(self, session_id: str) -> GxSession:
        return self.sessions.get_session(session_id)