from .helpers import is_valid_msisdn, is_valid_imsi
from typing import List, Dict

import logging
logger = logging.getLogger(__name__)
    
class Subscriber:
    id: str
    msisdn: str
    imsi: str
    """
    Represents a telecommunications subscriber with an MSISDN and an IMSI.
    """
    def __init__(self, id: str, msisdn: str, imsi: str):
        logger.debug("Inicializando Subscriber com MSISDN: %s e IMSI: %s", msisdn, imsi)
        # Convert
        id = str(id)
        msisdn = str(msisdn)
        imsi = str(imsi)
        if not is_valid_msisdn(msisdn):
            raise ValueError("Invalid MSISDN")
        if not is_valid_imsi(imsi):
            raise ValueError("Invalid IMSI")
        #
        self.id = id
        self.msisdn = msisdn
        self.imsi = imsi

class Subscribers:
    subscribers: Dict[str, Subscriber]
    """
    Represents a collection of subscribers.
    """
    def __init__(self):
        self.subscribers = {}

    def create_subscriber(self, id: str, msisdn: str, imsi: str):
        if id in self.subscribers:
            raise ValueError("Subscriber ID already exists")
        subscriber = Subscriber(id, msisdn, imsi)
        self.subscribers[subscriber.id] = subscriber
        return subscriber
    
    def get_subscriber_by_msisdn(self, msisdn: str) -> Subscriber:
        for subscriber in self.subscribers.values():
            if subscriber.msisdn == msisdn:
                return subscriber
        return None