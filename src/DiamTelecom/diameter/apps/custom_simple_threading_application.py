from diameter.node.application import SimpleThreadingApplication, Node
from ..sessions import DiameterSessions, DiameterSession

class CustomSimpleThreadingApplication(SimpleThreadingApplication):
    def __init__(self, application_id,
                 is_acct_application,
                 is_auth_application,
                 max_threads,
                 request_handler,
                 ):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = DiameterSessions()

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
