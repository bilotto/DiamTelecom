import re
from itertools import product
from .subscriber import Subscribers, Subscriber
from ..services import VoiceService, DataService, APN
from typing import Dict
import logging
from ..helpers import UUIDGenerator

uuid = UUIDGenerator()

logger = logging.getLogger(__name__)

def generate_subscribers(subscribers: Subscribers,
                         msisdn_template,
                         imsi_template,
                         carrier_id,
                         n_subscribers):
    msisdn_min = int(msisdn_template)
    imsi_min = int(imsi_template)
    imsi = imsi_min
    msisdn_max = msisdn_min + n_subscribers
    imsi_max = imsi_min + n_subscribers
    for msisdn in range(msisdn_min, msisdn_max):
        # Check if MSISDN is even or odd, if even make it prepaid and odd make it postpaid
        if msisdn % 2 == 0:
            subscriber = Subscriber(id=uuid.next_id(), msisdn=str(msisdn), imsi=str(imsi), carrier_id=carrier_id, type="prepaid")
        else:
            subscriber = Subscriber(id=uuid.next_id(), msisdn=str(msisdn), imsi=str(imsi), carrier_id=carrier_id, type="postpaid")
        subscribers.add_subscriber(subscriber)
        imsi += 1
        if imsi > imsi_max:
            imsi = imsi_min
    return subscribers

class Carrier:
    name: str
    carrier_id: int
    mcc_mnc: int
    country_code: int
    voice_service: VoiceService
    data_service: DataService
    subscribers: Subscribers
    apns: Dict[str, APN]

    def __init__(self, name,
                 carrier_id,
                 mcc_mnc: str,
                 country_code: str,
                 n_subscribers: int,
                 generate_subscribers: bool = True,
                 subscribers: Subscribers = None
                 ):
        self.name = name
        self.carrier_id = str(carrier_id)
        self.mcc_mnc = str(mcc_mnc)
        self.country_code = str(country_code)
        if subscribers:
            self.subscribers = subscribers
        else:
            self.subscribers = Subscribers()
        if generate_subscribers and n_subscribers:
            self.generate_subscribers(int(n_subscribers))
        self.data_service = None
        self.voice_service = None
        self.data_realm = None
        self.voice_realm = None
        self.gx_data_realm = None
        self.sy_data_realm = None
        self.gx_voice_realm = None
        self.rx_voice_realm = None
        self.realms = {}
        self.apns = {}

    def set_voice_service(self, voice_service: VoiceService):
        self.voice_service = voice_service

    def set_data_service(self, data_service: DataService):
        for i in self.subscribers.values():
            data_service.gx_service.app.subscribers.add_subscriber(i)
            data_service.sy_service.app.subscribers.add_subscriber(i)
        self.data_service = data_service

    def generate_subscribers(self, count: int):
        msisdn_template = f"{str(self.country_code)}0000000"
        imsi_template = f"{str(self.mcc_mnc)}000000000"[:15]

        self.subscribers = generate_subscribers(self.subscribers,
                                                msisdn_template,
                                                imsi_template,
                                                self.carrier_id,
                                                count)
        return self.subscribers
    
    def create_subscriber(self, msisdn, imsi, type=None):
        subscriber = Subscriber(id=uuid.next_id(), msisdn=msisdn, imsi=imsi, carrier_id=self.carrier_id, type=type)
        self.subscribers.add_subscriber(subscriber)
        return subscriber
            

    def add_apn(self, apn_name, ip_pool_cidr, mcc_mnc):
        apn = APN(apn_name, ip_pool_cidr, mcc_mnc)
        self.apns[apn_name] = apn
        return apn


    def data_flow(self):
        pass

    def voice_flow(self):
        pass