from .diameter_session import DiameterSession, DiameterSessions, Subscriber, DiameterMessage
from diameter.message.commands import SpendingStatusNotificationRequest
from diameter.message.constants import *
from diameter.message.avp.grouped import PolicyCounterStatusReport

class SySession(DiameterSession):
    session_id: str
    gx_session_id: str

    def __init__(self, subscriber, session_id: str):
        super().__init__(subscriber, session_id)
        self.gx_session_id = None

    def set_gx_session_id(self, gx_session_id: str):
        self.gx_session_id = gx_session_id

    def create_ssnr(self) -> SpendingStatusNotificationRequest:
        message = SpendingStatusNotificationRequest()
        message.session_id = self.session_id
        message.auth_application_id = APP_3GPP_SY
        message.policy_counter_status_report = []
        return message

    def __repr__(self):
        return f"SySession(active={self.active}, gx_session_id={self.gx_session_id}, n_messages={self.n_messages}, last_message={self.last_message})"

class SySessions(DiameterSessions):
    def __init__(self):
        super().__init__()
    
    def get(self, session_id: str) -> SySession:
        return self.diameter_sessions.get(session_id, None)

    def create_sy_session(self, subscriber, session_id: str) -> SySession:
        sy_session = SySession(subscriber, session_id)
        self.add_session(sy_session)
        return sy_session