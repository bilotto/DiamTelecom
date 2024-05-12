from .diameter.subscriber import Subscribers
from .diameter import *
import os
import csv

class SubscriberMessages:
    messages: list
    subscriber: Subscriber

    def __init__(self, subscriber):
        self.subscriber = subscriber
        self.messages = []

    def append(self, message):
        self.messages.append(message)

    def get_messages(self):
        print(self.messages)
        messages_sorted = sorted(self.messages, key=lambda x: x.timestamp)
        print(messages_sorted)
        return messages_sorted
    
    def __repr__(self):
        return f"SubscriberMessages({self.subscriber.msisdn},n_messages={len(self.messages)})"
    
    def to_csv(self, output_dir="."):
        csv_filepath = os.path.join(output_dir, "{}_{}.csv".format(self.subscriber.msisdn, self.subscriber.imsi))
        with open(csv_filepath, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for diameter_message in self.get_messages():
                csvwriter.writerow(diameter_message.to_csv())

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
            subscriber_messages = SubscriberMessages(subscriber)
            for gx_session in self.gx_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in gx_session.messages.get_messages():
                    subscriber_messages.append(message)
            for sy_session in self.sy_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in sy_session.messages.get_messages():
                    subscriber_messages.append(message)
            for rx_session in self.rx_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in rx_session.messages.get_messages():
                    subscriber_messages.append(message)
            subscriber_messages.to_csv()