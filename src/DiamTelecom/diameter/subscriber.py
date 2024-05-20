from ..helpers import is_valid_msisdn, is_valid_imsi
from typing import List, Dict
from .session import GxSessions, RxSessions, SySessions

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
            raise ValueError(f"Invalid MSISDN: {msisdn}")
        if not is_valid_imsi(imsi):
            raise ValueError(f"Invalid IMSI: {imsi}")
        #
        self.id = id
        self.msisdn = msisdn
        self.imsi = imsi
        # self.messages = DiameterMessages()
        self.gx_sessions = GxSessions()
        self.rx_sessions = RxSessions()
        self.sy_sessions = SySessions()

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
    
    def get_subscriber(self, id: str) -> Subscriber:
        logger.debug("Buscando subscriber com ID: %s", id)
        return self.subscribers.get(id)
    
    def get_subscribers(self) -> List[Subscriber]:
        return list(self.subscribers.values())