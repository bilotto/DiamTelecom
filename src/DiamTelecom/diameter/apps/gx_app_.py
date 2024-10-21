from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import GxSessions, GxSession
from .sy_app_ import SyApplication

class GxApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GxSessions()
        self.sy_app = None

    def set_sy_app(self, sy_app: SyApplication):
        self.sy_app = sy_app

    # def get_subscriber_active_session(self, msisdn: int) -> GxSession:
    #     if self.sessions.get_msisdn_sessions(msisdn):
    #         for session in self.sessions.get_msisdn_sessions(msisdn):
    #             if session.active:
    #                 return session

  
class PCEF:
    app: GxApplication
    app_config: dict
    def __init__(self, app, app_config):
        self.app = app
        self.app_config = app_config



class PCRF:
    app: GxApplication
    app_config: dict
    def __init__(self, app, app_config):
        self.app = app
        self.app_config = app_config
