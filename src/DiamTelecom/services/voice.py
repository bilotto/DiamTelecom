from ..diameter import *
from .ip_queue import IpQueue, ip_to_bytes
from ..telecom.subscriber import Subscriber
from diameter.message.constants import *
from diameter.message.commands import *
from .gx import GxService
from .rx import RxService
from diameter.message.avp.grouped import *
import time
import logging
logger = logging.getLogger(__name__)
from typing import List, Tuple

class VoiceService():
    gx_service: GxService
    rx_service: RxService

    def __init__(self,
                 gx_service: GxService,
                 rx_service: RxService = None,
                 ):
        if not isinstance(gx_service, GxService):
            raise Exception("DataService: gx_service must be an instance of GxService")
        if rx_service and not isinstance(rx_service, RxService):
            raise Exception("DataService: rx_service must be an instance of RxService")
        self.gx_service = gx_service
        self.rx_service = rx_service
        self.logger = logging.getLogger("DiamTelecom.services")

    @property
    def gx(self):
        return self.gx_service
    
    @property
    def rx(self):
        return self.rx_service

    @property
    def gx_sessions(self):
        return self.gx_service.sessions
    
    @property
    def rx_sessions(self):
        if self.rx_service:
            return self.rx_service.sessions
        return []

    def start_gx_session(self, gx_session: GxSession) -> GxSession:
        ccr_i = self.gx_service.create_ccr_i(gx_session)
        # Add specific voice parameters
        ccr_i.bearer_usage = E_BEARER_USAGE_IMS_SIGNALLING
        cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
        if not isinstance(cca_i, CreditControlAnswer):
            raise Exception("CCA is not received")
        if cca_i.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            gx_session.start()
        return gx_session
    
    def create_rx_session(self, subscriber: Subscriber) -> RxSession:
        gx_session = self.gx_service.gx_app.get_subscriber_active_session(subscriber.msisdn)
        if not gx_session:
            return None
        rx_session_id = self.rx_service.rx_app.node.session_generator.next_id()
        rx_session = self.rx_service.rx_app.sessions.create_session(subscriber, rx_session_id, gx_session.session_id)
        rx_session.framed_ip_address = gx_session.framed_ip_address
        return rx_session

    def start_rx_session(self, rx_session: RxSession) -> RxSession:
        aar = self.rx_service.create_aar(rx_session)
        aaa = self.rx_service.send_rx_request(rx_session, aar, timeout=5)
        if not isinstance(aaa, AaAnswer):
            raise Exception("AAA is not received")
        if aaa.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            rx_session.start()
        return rx_session
    
    def stop_rx_session(self, rx_session: RxSession) -> RxSession:
        if not rx_session.active:
            return
        str_ = self.rx_service.create_str(rx_session)
        sta = self.rx_service.send_rx_request(rx_session, str_, timeout=5)
        if not isinstance(sta, SessionTerminationAnswer):
            raise Exception("STA is not received")
        if sta.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            rx_session.end()
        return rx_session
    
    def start_voice_session(self, subscriber: Subscriber) -> Tuple[GxSession, RxSession]:
        gx_session = self.gx_service.gx_app.get_subscriber_active_session(subscriber.msisdn)
        if not gx_session:
            gx_session = self.start_gx_session(self.gx_service.create_gx_session(subscriber))
        if not gx_session:
            raise Exception("GX session is not created")
        if not gx_session.active:
            self.logger.error(f"Cannot start voice session. GX session is not active: {gx_session}")
            return None, None
        # rx_session = self.create_rx_session(subscriber)
        # rx_session = self.start_rx_session(rx_session)
        # self.gx_service.wait_for_gx_raa(gx_session, timeout=5)
        # gx_session.add_rx_session(rx_session)
        return gx_session
    
    def stop_voice_session(self, gx_session: GxSession) -> Tuple[GxSession, RxSession]:
        rx_session = self.rx_service.rx_app.sessions.get(gx_session.rx_session_id)
        if not rx_session:
            raise Exception("RX session is not found")
        if not rx_session.active:
            return gx_session, rx_session
        self.stop_rx_session(rx_session)
        self.gx_service.wait_for_gx_raa(gx_session, timeout=5)
        return gx_session, rx_session

    # def create_aar_audio(self, rx_session: RxSession) -> AaRequest:
    #     # aar = self.create_aar()
    #     aar = AaRequest()
    #     aar.auth_application_id = APP_3GPP_RX

    #     origin_host = self.rx_service.af.node.origin_host
    #     origin_realm = self.rx_service.af.node.realm_name
    #     # destination_host = self.rx_destination_host
    #     destination_realm = self.rx_service.af.node.realm_name
    #     aar.origin_host = origin_host.encode()
    #     aar.origin_realm = origin_realm.encode()
    #     aar.destination_realm = destination_realm.encode() if destination_realm else None

    #     aar.session_id = rx_session.session_id

    #     aar.specific_action.append(E_SPECIFIC_ACTION_INDICATION_OF_RELEASE_OF_BEARER)
    #     aar.specific_action.append(E_SPECIFIC_ACTION_ACCESS_NETWORK_INFO_REPORT)
    #     aar.specific_action.append(E_SPECIFIC_ACTION_INDICATION_OF_FAILED_RESOURCES_ALLOCATION)
    #     #
    #     aar.supported_features = SupportedFeatures()
    #     aar.supported_features.vendor_id = VENDOR_TGPP
    #     aar.supported_features.feature_list = 35
    #     aar.supported_features.feature_list_id = 1

    #     # Get gx_session from rx_session.gx_session_id
    #     gx_session = self.gx_service.gx_app.sessions.get(rx_session.gx_session_id)
    #     #
    #     aar.framed_ip_address = ip_to_bytes(gx_session.framed_ip_address)
    #     aar.origin_state_id = 1268028842

    #     aar.header.hop_by_hop_identifier = 4
    #     aar.header.end_to_end_identifier = 4
    #     aar.header.is_proxyable = True
    #     #
    #     aar.media_component_description = MediaComponentDescription()
    #     mdc = aar.media_component_description
    #     mdc.media_component_number = 0
    #     # mdc.af_application_identifier = "urn:3gpp:service.ims.icsi.mmtel".encode()
    #     mdc.af_application_identifier = "urn:urn-7:3gpp-service.ims.icsi.mmtel-4G".encode()
    #     mdc.media_type = E_MEDIA_TYPE_AUDIO
    #     mdc.max_requested_bandwidth_ul = 41000
    #     mdc.max_requested_bandwidth_dl = 41000
    #     # 
    #     media_sub_component = MediaSubComponent()
    #     media_sub_component.flow_description.append("permit out 17 from 10.130.18.118 32380 to 10.4.25.194 1234".encode())
    #     media_sub_component.flow_description.append("permit in 17 from 10.4.25.194 to 10.130.18.118 32380".encode())
    #     #
    #     media_sub_component.flow_usage = E_FLOW_USAGE_NO_INFORMATION
    #     media_sub_component.flow_status = E_FLOW_STATUS_ENABLED
    #     media_sub_component.flow_number = 1
    #     #
    #     mdc.media_sub_component.append(media_sub_component)
    #     #
    #     media_sub_component = MediaSubComponent()
    #     media_sub_component.flow_description.append("flow3".encode())
    #     media_sub_component.flow_description.append("flow4".encode())
    #     #
    #     media_sub_component.flow_usage = E_FLOW_USAGE_RTCP
    #     media_sub_component.flow_status = E_FLOW_STATUS_ENABLED
    #     media_sub_component.flow_number = 2
    #     #
    #     mdc.media_sub_component.append(media_sub_component)

    #     return aar

