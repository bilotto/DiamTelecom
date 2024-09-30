from diameter.node.application import SimpleThreadingApplication, Node
from ..sessions import DiameterSessions, DiameterSession
from DiamTelecom.telecom.subscriber import Subscribers
from .stats import DiameterStatistics

class CustomSimpleThreadingApplication(SimpleThreadingApplication):
    def __init__(self, application_id,
                 is_acct_application,
                 is_auth_application,
                 max_threads,
                 request_handler,
                 ):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = DiameterSessions()
        self.stats = DiameterStatistics()
        self.subscribers = None

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{self.node.origin_host}: <{self.name} ({self.application_id})>"

    def send_request_custom(self, request, timeout=5):
        session_id = request.session_id
        session = self.get_session_by_id(session_id)
        if not session:
            raise Exception(f"Session {session_id} not found")
        session.add_message(request)
        try:
            answer = self.send_request(request, timeout)
        except Exception as e:
            self.stats.increment_request_count(success=False)
            raise e
        #
        session.add_message(answer)
        result_code = answer.result_code
        self.stats.increment_rc_count(result_code)
        self.stats.increment_request_count(success=True)
        return answer

        
    def set_subscribers(self, subscribers: Subscribers):
        self.subscribers = subscribers

    def get_session_by_id(self, session_id: str) -> DiameterSession:
        return self.sessions.get_session(session_id)
    
    def get_subscriber_sessions_by_msisdn(self, msisdn: int):
        return self.sessions.get_msisdn_sessions(msisdn)
    
    def get_subscriber_active_session(self, msisdn: int):
        if self.sessions.get_msisdn_sessions(msisdn):
            for session in self.sessions.get_msisdn_sessions(msisdn):
                if session.active:
                    return session
