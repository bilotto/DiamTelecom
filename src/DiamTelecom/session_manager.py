from .diameter.subscriber import Subscribers
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

    def parse_sessions(self):
        for subscriber in self.subscribers.get_subscribers():
            subscriber_messages = []
            for gx_session in self.gx_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in gx_session.messages.get_messages():
                    subscriber_messages.append(message)
            for sy_session in self.sy_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in sy_session.messages.get_messages():
                    subscriber_messages.append(message)
            for rx_session in self.rx_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in rx_session.messages.get_messages():
                    subscriber_messages.append(message)
            # Sort messages by timestamp
            subscriber_messages.sort(key=lambda x: x.timestamp)
            print(subscriber_messages)