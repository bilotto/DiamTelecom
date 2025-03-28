from ..helpers import is_valid_msisdn, is_valid_imsi
from typing import List, Dict
import logging
logger = logging.getLogger(__name__)

class Subscriber:
    id: str
    msisdn: str
    imsi: str
    carrier_id: int
    apn: str
    """
    Represents a telecommunications subscriber with an MSISDN and an IMSI.
    """
    def __init__(self,
                 id: str,
                 msisdn: str,
                 imsi: str,
                 carrier_id: int = None,
                 type: str = None,):
        self.id = id
        if not id:
            raise ValueError("Subscriber ID is required")
        if not msisdn:
            raise ValueError("MSISDN is required")
        if not imsi:
            logger.error("Subscriber created without IMSI")
        msisdn = str(msisdn)
        imsi = str(imsi)
        self.msisdn = msisdn
        self.imsi = imsi
        self.carrier_id = carrier_id
        if not type:
            type = "prepaid"
        self.type = type
        self.apn = None

    @property
    def subscriber_type(self):
        return self.type

    def set_type(self, type: str):
        self.type = type

    # Method to represent then the subscriber manually sets the APN in the phone
    def set_apn(self, apn: str):
        self.apn = apn

    def __str__(self):
        return f"Subscriber({self.msisdn},{self.imsi})"
    
    def __repr__(self):
        return self.__str__()

import random

class Subscribers(dict):
    """
    Represents a collection of subscribers.
    """
    def __str__(self):
        return f"Subscribers({len(self)})"
    
    def __repr__(self):
        return self.__str__()

    def create_subscriber(self, id: str, msisdn: str, imsi: str):
        if id in self:
            raise ValueError("Subscriber ID already exists")
        subscriber = Subscriber(id, msisdn, imsi)
        self[id] = subscriber
        return subscriber
    
    def get_subscriber_by_subscription_id(self, parsed_subscription_id: tuple) -> Subscriber:
            msisdn = parsed_subscription_id[0]
            imsi = parsed_subscription_id[1]
            sip_uri = parsed_subscription_id[2]
            if msisdn:
                return self.get_subscriber_by_msisdn(msisdn)
            elif imsi:
                return self.get_subscriber_by_imsi(imsi)
            elif sip_uri:
                return self.get_subscriber_by_sip_uri(sip_uri)
            return None

    
    def get_subscriber_by_msisdn(self, msisdn: str) -> Subscriber:
        for subscriber in self.values():
            if subscriber.msisdn == msisdn:
                return subscriber
        return None
    
    def get_subscriber_by_imsi(self, imsi: str) -> Subscriber:
        for subscriber in self.values():
            if subscriber.imsi == imsi:
                return subscriber
        return None
    
    def get_subscriber_by_sip_uri(self, sip_uri: str) -> Subscriber:
        for subscriber in self.get_subscribers():
            if subscriber.msisdn in sip_uri or subscriber.imsi in sip_uri:
                return subscriber
        return None
    
    def get_subscriber(self, id: str) -> Subscriber:
        return self.get(id)
    
    def get_subscribers(self) -> List[Subscriber]:
        return list(self.values())

    def add_subscriber(self, subscriber: Subscriber) -> Subscriber:
        if subscriber.id in self:
            raise ValueError("Subscriber ID already exists")
        self[subscriber.id] = subscriber
        return subscriber
    
    def get_random_subscriber(self) -> Subscriber:
        return random.choice(list(self.values()))
        
    def get_subscriber_by_msisdn_imsi(self, msisdn: str, imsi: str) -> Subscriber:
        for subscriber in self.values():
            if subscriber.msisdn == msisdn and subscriber.imsi == imsi:
                return subscriber
        return None
    
