from .diameter.subscriber import Subscribers
from .diameter import *
import os
import csv
from typing import List
from .pcap import Pcap
import logging
logger = logging.getLogger(__name__)

# class SubscriberMessages:
#     messages: list
#     subscriber: Subscriber

#     def __init__(self, subscriber):
#         self.subscriber = subscriber
#         self.messages = []

#     def append(self, message):
#         self.messages.append(message)

#     def get_messages(self) -> List[DiameterMessage]:
#         messages_sorted = sorted(self.messages, key=lambda x: x.timestamp)
#         return messages_sorted

#     def __repr__(self):
#         return f"SubscriberMessages({self.subscriber.msisdn},n_messages={len(self.messages)})"
    
#     def to_csv(self, output_dir="."):
#         csv_filepath = os.path.join(output_dir, "{}_{}.csv".format(self.subscriber.msisdn, self.subscriber.imsi))
#         with open(csv_filepath, 'w', newline='') as csvfile:
#             csvwriter = csv.writer(csvfile)
#             for diameter_message in self.get_messages():
#                 row = []
#                 time = diameter_message.time
#                 name = diameter_message.name
#                 msisdn = self.subscriber.msisdn
#                 framed_ip_address = diameter_message.framed_ip_address
#                 session_id = diameter_message.session_id
#                 avps_string = diameter_message.avps.get_fields_string()
#                 origin_host = diameter_message.get_from_pkt("Origin-Host")
#                 row.append(time)
#                 row.append(msisdn)
#                 row.append(name)
#                 row.append(origin_host)
#                 row.append(framed_ip_address)
#                 row.append(avps_string)
#                 row.append(session_id)
#                 # row = diameter_message.to_csv()
#                 csvwriter.writerow(row)

class SessionManager:
    subscribers: Subscribers
    pcap: Pcap
    gx_sessions: GxSessions
    rx_sessions: RxSessions
    sy_sessions: SySessions
    """
    Manages the sessions of subscribers.
    """

    def __init__(self, pcap, subscribers=None):
        if subscribers:
            self.subscribers = subscribers
            self.create_subscribers = False
        else:
            self.subscribers = Subscribers()
            self.create_subscribers = True
        self.gx_sessions = GxSessions()
        self.rx_sessions = RxSessions()
        self.sy_sessions = SySessions()
        self.pcap = pcap
        self.pcap_filename = pcap.filename
        self.all_messages = DiameterMessages()
        self.subscriber_messages = dict()
        self.voice_call_rx_sessions = dict()

    def parse_sessions(self):
        for subscriber in self.subscribers.get_subscribers():
            # subscriber_messages = SubscriberMessages(subscriber)
            for gx_session in self.gx_sessions.get_msisdn_sessions(subscriber.msisdn):
                # if not gx_session.rx_sessions:
                #     continue
                for message in gx_session.messages.get_messages():
                    self.all_messages.add_message(message)
            for sy_session in self.sy_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in sy_session.messages.get_messages():
                    self.all_messages.add_message(message)
            for rx_session in self.rx_sessions.get_msisdn_sessions(subscriber.msisdn):
                for message in rx_session.messages.get_messages():
                    self.all_messages.add_message(message)
        self.all_messages.to_csv(f"output/{self.pcap_filename}.csv")


    def parse_voice_sessions(self):
        logging.info("Tshark filters for voice calls")
        for subscriber in self.subscribers.get_subscribers():
            for i, gx_session in enumerate(self.gx_sessions.get_msisdn_sessions(subscriber.msisdn)):
                if not gx_session.rx_sessions:
                    continue
                diameter_messages = DiameterMessages()
                for rx_session in gx_session.rx_sessions:
                    if not rx_session.is_voice_call:
                        continue
                    for diameter_message in rx_session.messages.get_messages():
                        diameter_messages.add_message(diameter_message)
                for gx_message in gx_session.messages.get_messages():
                    diameter_messages.add_message(gx_message)
                filename = f"output/{subscriber.msisdn}_{i}.csv"
                # diameter_messages.to_csv(filename)
                # self.pcap.dump_packets(gx_session.tshark_filter, f"{filename}.pcap")
                logger.info(gx_session.tshark_filter)
                logger.info("")