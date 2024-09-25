
from .diameter_session import DiameterSession, DiameterSessions, Subscriber, DiameterMessage
from diameter.message.constants import *
from diameter.message.commands import AaRequest, SessionTerminationRequest
from diameter.message.avp.grouped import *
from ..constants import *
from DiamTelecom.helpers import ip_to_bytes


class RxSession(DiameterSession):
    subscriber: Subscriber
    session_id: str
    gx_session_id: str

    def __init__(self, subscriber, session_id, gx_session_id):
        super().__init__(subscriber, session_id)
        self.gx_session_id = gx_session_id
        self.framed_ip_address = None

    def set_gx_session_id(self, gx_session_id: str):
        self.gx_session_id = gx_session_id

    def __repr__(self):
        return f"""RxSession(msisdn={self.msisdn}
          session_id={self.session_id}
          gx_session_id={self.gx_session_id}
          active={self.active}
          n_messages={self.n_messages}
          last_message={self.last_message})"""

    @property
    def tshark_filter(self):
        return f"diameter.Framed-IP-Address.IPv4 == {self.framed_ip_address} || diameter.Session-Id == \"{self.gx_session_id}\" || diameter.Session-Id == \"{self.session_id}\""

    @property
    def is_voice_call(self):
        message = self.messages.get_messages()[0]
        if message.avps.get('Media-Type') == 'AUDIO':
            return True
        return False
    
    def add_message(self, message: DiameterMessage):
        message = super().add_message(message)
        #
        if self.start_time and self.messages.n_messages == 1:
            if self.is_voice_call:
                logger.info(f"{message.time},{message.pkt_number},{message.name},{self.subscriber.msisdn} started voice call,{self.framed_ip_address}")
        
        elif self.end_time:
            if message.name == STA and self.is_voice_call:
                logger.info(f"{message.time},{message.pkt_number},{message.name},{self.subscriber.msisdn} ended voice call. Duration: {self.duration} seconds,{self.framed_ip_address}")


    def create_aar(self):
        aar = AaRequest()
        aar.auth_application_id = APP_3GPP_RX
        aar.session_id = self.session_id
        if self.framed_ip_address:
            aar.framed_ip_address = ip_to_bytes(self.framed_ip_address)
        return aar

    def create_str(self):
        str_ = SessionTerminationRequest()
        str_.auth_application_id = APP_3GPP_RX
        str_.session_id = self.session_id
        return str_

class RxSessions(DiameterSessions):
    def __init__(self):
        super().__init__()

    def add_rx_session(self, rx_session: RxSession):
        self.add_session(rx_session)

    def get_rx_session(self, session_id: str) -> RxSession:
        return self.get_session(session_id)
    
    def get(self, session_id: str) -> RxSession:
        return self.diameter_sessions.get(session_id, None)

    def create_session(self, subscriber, session_id: str, gx_session_id: str) -> RxSession:
        rx_session = RxSession(subscriber, session_id, gx_session_id)
        self.add_rx_session(rx_session)
        return rx_session

