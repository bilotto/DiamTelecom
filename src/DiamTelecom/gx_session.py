from .diameter_session import DiameterSession, DiameterSessions
from .rx_session import RxSessions
from .sy_session import SySessions

class GxSession(DiameterSession):
    session_id: str
    framed_ip_address: str
    rx_sessions: RxSessions
    sy_sessions: SySessions

    def __init__(self, subscriber, session_id: str, framed_ip_address: str):
        super().__init__(subscriber, session_id)
        self.framed_ip_address = framed_ip_address
        self.rx_sessions: RxSessions = RxSessions()
        self.sy_sessions: SySessions = SySessions()
        self.cc_request_number = 0
        self.mcc_mnc = None
        self.rat_type = None
        self.apn = None


class GxSessions(DiameterSessions):
    def __init__(self):
        super().__init__()

    def add_gx_session(self, gx_session: GxSession):
        self.add_diameter_session(gx_session)

    def get_gx_session(self, session_id: str) -> GxSession:
        return self.get_diameter_session(session_id)

    def remove_gx_session(self, session_id: str):
        self.remove_diameter_session(session_id)

    def create_gx_session(self, subscriber, session_id: str, framed_ip_address: str) -> GxSession:
        gx_session = GxSession(subscriber, session_id, framed_ip_address)
        self.add_gx_session(gx_session)
        return gx_session
    
