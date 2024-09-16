from ..helpers import is_valid_msisdn, is_valid_imsi
from typing import List, Dict

import logging
logger = logging.getLogger(__name__)
    
class Subscriber:
    id: str
    msisdn: str
    imsi: str
    carrier_id: int
    """
    Represents a telecommunications subscriber with an MSISDN and an IMSI.
    """
    def __init__(self,
                 id: str,
                 msisdn: str,
                 imsi: str,
                 carrier_id: int = None):
        logger.debug("Inicializando Subscriber com MSISDN: %s e IMSI: %s", msisdn, imsi)
        # Convert
        id = str(id)
        msisdn = str(msisdn)
        imsi = str(imsi)
        if not is_valid_msisdn(msisdn):
            raise ValueError(f"Invalid MSISDN: {msisdn}")
        if not is_valid_imsi(imsi):
            raise ValueError(f"Invalid IMSI: {imsi}")
        #
        self.id = id
        self.msisdn = msisdn
        self.imsi = imsi
        self.carrier_id = carrier_id
        self.use_case = None
        # self.messages = DiameterMessages()

class Subscribers(dict):
    """
    Represents a collection of subscribers.
    """
    def create_subscriber(self, id: str, msisdn: str, imsi: str):
        if id in self:
            raise ValueError("Subscriber ID already exists")
        subscriber = Subscriber(id, msisdn, imsi)
        self[id] = subscriber
        return subscriber
    
    def get_subscriber_by_msisdn(self, msisdn: str) -> Subscriber:
        for subscriber in self.values():
            if subscriber.msisdn == msisdn:
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
        return next(iter(self.values()))
    
    def get_subscriber_by_msisdn_imsi(self, msisdn: str, imsi: str) -> Subscriber:
        for subscriber in self.values():
            if subscriber.msisdn == msisdn and subscriber.imsi == imsi:
                return subscriber
        return None