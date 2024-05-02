from telecom.diameter_session import DiameterSession, DiameterSessions

class SySession(DiameterSession):
    session_id: str

    def __init__(self, subscriber, session_id: str):
        super().__init__(subscriber, session_id)

class SySessions(DiameterSessions):
    def __init__(self):
        super().__init__()

    def add_sy_session(self, sy_session: SySession):
        self.add_diameter_session(sy_session)

    def get_sy_session(self, session_id: str) -> SySession:
        return self.get_diameter_session(session_id)

    def remove_sy_session(self, session_id: str):
        self.remove_diameter_session(session_id)