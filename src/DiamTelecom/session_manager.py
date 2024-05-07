from .subscriber import Subscribers
from .diameter import *


class SessionManager:
    subscribers: Subscribers
    gx_sessions: GxSessions
    rx_sessions: RxSessions
    sy_sessions: SySessions
    """
    Manages the sessions of subscribers.
    """

    def __init__(self):
        self.subscribers = Subscribers()
        self.gx_sessions = GxSessions()
        self.rx_sessions = RxSessions()
        self.sy_sessions = SySessions()

