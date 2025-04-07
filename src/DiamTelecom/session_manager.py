from .telecom.subscriber import Subscribers
from .diameter import *
from typing import List
import logging
logger = logging.getLogger(__name__)
import csv
from diameter.message.constants import *
import threading

lock = threading.Lock()

class SessionManager:
    subscribers: Subscribers
    gx_sessions: GxSessions
    rx_sessions: RxSessions
    sy_sessions: SySessions

    def __init__(self, subscribers=None, gx_sessions=None, rx_sessions=None, sy_sessions=None):
        if subscribers:
            self.subscribers = subscribers
        else:
            self.subscribers = Subscribers()
        if gx_sessions:
            self.gx_sessions = gx_sessions
        else:
            self.gx_sessions = GxSessions()
        if rx_sessions:
            self.rx_sessions = rx_sessions
        else:
            self.rx_sessions = RxSessions()
        if sy_sessions:
            self.sy_sessions = sy_sessions
        else:
            self.sy_sessions = SySessions()
        # self.subscribers = Subscribers()
        # self.gx_sessions = GxSessions()
        # self.rx_sessions = RxSessions()
        # self.sy_sessions = SySessions()
        # self.all_messages = DiameterMessages()
        self.orphan_messages = []

    def add_orphan_message(self, message):
        with lock:
            session_id = message.session_id
            if self.gx_sessions.get_session_by_id(session_id):
                print(f"GX session found for session_id: {session_id}, message: {message}")
            self.orphan_messages.append(message)
            # print(len(f"Orphan messages: {self.orphan_messages}"))

    def add_gx_session(self, gx_session):
        with lock:
            self.gx_sessions.add_gx_session(gx_session)

    def get_gx_session(self, session_id):
        with lock:
            return self.gx_sessions.get_session_by_id(session_id)
        
    def get_subscriber_by_msisdn(self, msisdn):
        with lock:
            return self.subscribers.get_subscriber_by_msisdn(msisdn)
        
    def add_subscriber(self, subscriber):
        with lock:
            self.subscribers.add_subscriber(subscriber)

    # def get_gx_session(self, session_id):
    #     return self.gx_sessions.get(session_id)
    # def parse_sessions(self):
    #     for subscriber in self.subscribers.get_subscribers():
    #         for gx_session in self.gx_sessions.get_msisdn_sessions(subscriber.msisdn):
    #             for message in gx_session.messages.get_messages():
    #                 self.all_messages.add_message(message)
    #         for sy_session in self.sy_sessions.get_msisdn_sessions(subscriber.msisdn):
    #             for message in sy_session.messages.get_messages():
    #                 self.all_messages.add_message(message)
    #         for rx_session in self.rx_sessions.get_msisdn_sessions(subscriber.msisdn):
    #             for message in rx_session.messages.get_messages():
    #                 self.all_messages.add_message(message)

    # def dump_csv(self, csv_output_file: str):
    #     self.parse_sessions()
    #     with open(csv_output_file, mode='w') as csv_file:
    #         fieldnames = [
    #                     'date',
    #                     'message_name',
    #                     'msisdn',
    #                     'imsi',
    #                     'mcc_mnc',
    #                     'framed_ip_address',
    #                     'apn',
    #                     'session_id',
    #                       ]
    #         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    #         writer.writeheader()
    #         for message in self.all_messages.get_messages():
    #             if message.app_id == APP_3GPP_GX:
    #                 gx_session = self.gx_sessions.get(message.session_id)
    #             elif message.app_id == APP_3GPP_RX:
    #                 rx_session = self.rx_sessions.get(message.session_id)
    #                 gx_session = self.gx_sessions.get(rx_session.gx_session_id)

    #             writer.writerow({
    #                 'date': message.time,
    #                 'message_name': message.name,
    #                 'msisdn': message.subscriber.msisdn,
    #                 'imsi': message.subscriber.imsi,
    #                 'mcc_mnc': gx_session.mcc_mnc,
    #                 'framed_ip_address': gx_session.framed_ip_address,
    #                 'apn': gx_session.apn,
    #                 'session_id': message.session_id,
    #             })


    # def dump_hex_string(self, output_directory):
    #     print("Dumping hex strings")
    #     self.parse_sessions()
    #     for idx, message in enumerate(self.all_messages.get_messages()):
    #         filename = f"{message.name}_{idx}.txt"
    #         with open(f"{output_directory}/{filename}", "w") as f:
    #             f.write(message.hex_string)
            