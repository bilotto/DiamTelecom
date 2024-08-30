from .subscriber import Subscribers
from ..services import VoiceService, DataService
import logging
logger = logging.getLogger(__name__)
from .helpers import generate_subscribers

class Carrier:
    name: str
    carrier_id: int
    mcc_mnc: int
    country_code: int
    voice_service: VoiceService
    data_service: DataService
    subscribers: Subscribers
    

    def __init__(self,
                 name,
                 carrier_id,
                 mcc_mnc: int,
                 country_code: int,
                 subscribers: Subscribers = None
                 ):
        self.name = name
        self.carrier_id = carrier_id
        self.mcc_mnc = mcc_mnc
        self.country_code = country_code
        self.data_service = None
        self.msisdn_template = f"{str(country_code)}0000000"
        self.imsi_template = f"{str(mcc_mnc)}000000000"[:15]

        if subscribers:
            self.subscribers = subscribers
        else:
            self.subscribers = Subscribers()
            # self.subscribers = generate_subscribers(self.subscribers, self.mcc_mnc, self.country_code, 1000)
            self.subscribers = generate_subscribers(self.subscribers, self.msisdn_template, self.imsi_template, self.carrier_id, 1000)
        #
        self.voice_service = None



    def set_voice_service(self, voice_service: VoiceService):
        self.voice_service = voice_service

    def set_data_service(self, data_service: DataService):
        self.data_service = data_service

    def start_voice_service(self):
        if self.voice_service:
            self.voice_service.start()

    def stop_voice_service(self):
        if self.voice_service:
            self.voice_service.stop()

    def start_data_service(self):
        if self.data_service:
            self.data_service.start()

    def stop_data_service(self):
        if self.data_service:
            self.data_service.stop()