from .diameter_session import DiameterSession, DiameterSessions

class RxSession(DiameterSession):
    session_id: str

    def __init__(self, subscriber, session_id):
        super().__init__(subscriber, session_id)


class RxSessions(DiameterSessions):
    def __init__(self):
        super().__init__()

    def add_rx_session(self, rx_session: RxSession):
        self.add_diameter_session(rx_session)

    def get_rx_session(self, session_id: str) -> RxSession:
        return self.get_diameter_session(session_id)

    def remove_rx_session(self, session_id: str):
        self.remove_diameter_session(session_id)
