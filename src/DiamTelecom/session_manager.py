from .telecom.subscriber import Subscribers
from .diameter import *
from typing import List
import logging
logger = logging.getLogger(__name__)
import csv
from diameter.message.constants import *

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
        self.all_messages = DiameterMessages()

    def parse_sessions(self):
        for subscriber in self.subscribers.get_subscribers():
            for gx_session in self.gx_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in gx_session.messages.get_messages():
                    self.all_messages.add_message(message)
            for sy_session in self.sy_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in sy_session.messages.get_messages():
                    self.all_messages.add_message(message)
            for rx_session in self.rx_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in rx_session.messages.get_messages():
                    self.all_messages.add_message(message)

    def dump_csv(self, csv_output_file: str):
        self.parse_sessions()
        with open(csv_output_file, mode='w') as csv_file:
            fieldnames = [
                        'date',
                        'message_name',
                        'msisdn',
                        'imsi',
                        'mcc_mnc',
                        'framed_ip_address',
                        'apn',
                        'session_id',
                          ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for message in self.all_messages.get_messages():
                if message.app_id == APP_3GPP_GX:
                    gx_session = self.gx_sessions.get(message.session_id)
                elif message.app_id == APP_3GPP_RX:
                    rx_session = self.rx_sessions.get(message.session_id)
                    gx_session = self.gx_sessions.get(rx_session.gx_session_id)

                writer.writerow({
                    'date': message.time,
                    'message_name': message.name,
                    'msisdn': message.subscriber.msisdn,
                    'imsi': message.subscriber.imsi,
                    'mcc_mnc': gx_session.mcc_mnc,
                    'framed_ip_address': gx_session.framed_ip_address,
                    'apn': gx_session.apn,
                    'session_id': message.session_id,
                })