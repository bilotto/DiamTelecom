from .diameter_session import DiameterSession, DiameterSessions, Subscriber, DiameterMessage

class SySession(DiameterSession):
    session_id: str
    gx_session_id: str

    def __init__(self, subscriber, session_id: str):
        super().__init__(subscriber, session_id)
        self.gx_session_id = None

    def set_gx_session_id(self, gx_session_id: str):
        self.gx_session_id = gx_session_id

    def __repr__(self):
        return f"SySession(n_messages={self.n_messages}, last_message={self.last_message})"

class SySessions(DiameterSessions):
    def __init__(self):
        super().__init__()
    
    def get(self, session_id: str) -> SySession:
        return self.diameter_sessions.get(session_id, None)

    def create_sy_session(self, subscriber, session_id: str) -> SySession:
        sy_session = SySession(subscriber, session_id)
        self.add_session(sy_session)
        return sy_session