from .diameter_session import DiameterSession, DiameterSessions
from diameter.message.commands import *
from diameter.message.constants import *
from diameter.message.avp.grouped import PolicyCounterStatusReport
from diameter.message import Message

class SySession(DiameterSession):
    session_id: str
    gx_session_id: str

    def __init__(self, subscriber, session_id: str):
        super().__init__(subscriber, session_id)
        self.gx_session_id = None
        self.policy_counter_status_report = dict()

    @property
    def pc_string(self):
        pc_str = ""
        for pc_id, pc_status in self.policy_counter_status_report.items():
            pc_str += f"{pc_id}={pc_status},"
        return pc_str

    def set_gx_session_id(self, gx_session_id: str):
        self.gx_session_id = gx_session_id

    def create_ssnr(self) -> SpendingStatusNotificationRequest:
        message = SpendingStatusNotificationRequest()
        message.session_id = self.session_id
        message.auth_application_id = APP_3GPP_SY
        message.policy_counter_status_report = []
        return message
    
    def create_slr(self) -> SpendingLimitRequest:
        message = SpendingLimitRequest()
        message.session_id = self.session_id
        message.auth_application_id = APP_3GPP_SY
        return message
        
    def add_message(self, message: Message):
        super().add_message(message)
        if isinstance(message, SpendingLimitAnswer):
            for i in message.policy_counter_status_report:
                pc_id = i.policy_counter_identifier
                pc_status = i.policy_counter_status
                self.policy_counter_status_report[pc_id] = pc_status

        # if isinstance(message, SessionTerminationAnswer):
        #     self.end()

    def __repr__(self):
        return f"""SySession(msisdn={self.msisdn},
          session_id={self.session_id}
          gx_session_id={self.gx_session_id}
          active={self.active}
          n_messages={self.n_messages}
          last_message={self.last_message})
          """

class SySessions(DiameterSessions):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"SySessions({len(self.diameter_sessions)},{self.n_active_sessions})"
    
    def get(self, session_id: str) -> SySession:
        return self.diameter_sessions.get(session_id, None)

    def create_sy_session(self, subscriber, session_id: str) -> SySession:
        sy_session = SySession(subscriber, session_id)
        self.add_session(sy_session)
        return sy_session