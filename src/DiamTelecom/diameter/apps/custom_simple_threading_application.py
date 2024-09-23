from diameter.node.application import SimpleThreadingApplication, Node
from ..sessions import DiameterSessions, DiameterSession

class DiameterStatistics:
    def __init__(self):
        self.request_count = dict()
        self.request_count['success'] = 0
        self.request_count['failure'] = 0
        self.rc_count = dict()

    def increment_request_count(self, success: bool):
        if success:
            self.request_count['success'] += 1
        else:
            self.request_count['failure'] += 1

    def increment_rc_count(self, rc):
        if rc not in self.rc_count:
            self.rc_count[rc] = 1
        else:
            self.rc_count[rc] += 1


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
            result_code = answer.result_code
            self.stats.increment_rc_count(result_code)
            self.stats.increment_request_count(success=True)
            return answer
        except Exception as e:
            self.stats.increment_request_count(success=False)
            raise e