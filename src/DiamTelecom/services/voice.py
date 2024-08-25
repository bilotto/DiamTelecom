from DiamTelecom.diameter import *
from .ip_queue import IpQueue, ip_to_bytes
from DiamTelecom.diameter import *
from carrier.subscriber import CustomSubscriber
from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import MediaSubComponent
from .services import Service, GxService, RxService

import time

class VoiceService(Service):
    def __init__(self, gx_config: dict, rx_config: dict, carrier_data: dict, gx_app: GxApplication, rx_app: RxAppication):
        super().__init__(gx_service=GxService(gx_app, gx_config), rx_service=RxService(rx_app, rx_config))

    # def send_rx_request(self, rx_session: RxSession, message, timeout=5):
    #     rx_session.add_message(message)
    #     response = self.rx_service.af.send_request(message, timeout)
    #     rx_session.add_message(response)

    @property
    def rx_destination_host(self):
        if self.rx_config.get('destination_host'):
            return self.rx_config['destination_host']
        return None
    
    @property
    def rx_destination_realm(self):
        if self.rx_config.get('destination_realm'):
            return self.rx_config['destination_realm']
        return None
    
    @property
    def all_peers_ports(self):
        ports = []
        for peer in self.gx_config['peers']:
            ports.append(peer['port'])
        for peer in self.rx_config['peers']:
            ports.append(peer['port'])
        return ports

    # def set_rx_hosts(self, rx_message):
    #     origin_host = self.af.node.origin_host
    #     origin_realm = self.af.node.realm_name
    #     destination_host = self.rx_destination_host
    #     destination_realm = self.rx_destination_realm
    #     rx_message.origin_host = origin_host.encode()
    #     rx_message.origin_realm = origin_realm.encode()
    #     rx_message.destination_host = destination_host.encode()
    #     rx_message.destination_realm = destination_realm.encode()
    #     return rx_message

    def create_aar(self) -> AaRequest:
        aar = AaRequest()
        aar = self.rx_service.set_rx_hosts(aar)
        aar.auth_application_id = APP_3GPP_RX
        return aar

    def create_str(self):
        str_ = SessionTerminationRequest()
        str_ = self.rx_service.set_rx_hosts(str_)
        str_.auth_application_id = APP_3GPP_RX
        return str_

    # def create_rx_session(self, subscriber: CustomSubscriber, gx_session: GxSession):
    #     rx_session_id = self.af.node.session_generator.next_id()
    #     rx_session = RxSession(subscriber, rx_session_id, gx_session)
    #     return rx_session
    
    def create_ccr_i(self, gx_session: GxSession) -> CreditControlRequest:
        ccr = self.gx_service.create_ccr()
        ccr.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
        ccr.cc_request_number = 0
        #
        ccr.session_id = gx_session.session_id
        ccr.framed_ip_address = ip_to_bytes(gx_session.framed_ip_address)
        ccr.sgsn_mcc_mnc = str(gx_session.mcc_mnc)
        #
        ccr.rat_type = E_RAT_TYPE_EUTRAN
        ccr.ip_can_type = E_IP_CAN_TYPE_3GPP_EPS

        ccr.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_E164, str(gx_session.msisdn))
        ccr.add_subscription_id(E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI, str(gx_session.imsi))

        ccr.supported_features.vendor_id = VENDOR_TGPP
        ccr.supported_features.feature_list = 1032
        ccr.supported_features.feature_list_id = 1

        ccr.qos_information.apn_aggregate_max_bitrate_ul = 384000
        ccr.qos_information.apn_aggregate_max_bitrate_dl = 384000

        ccr.default_eps_bearer_qos.qos_class_identifier = E_QOS_CLASS_IDENTIFIER_QCI_9
        ccr.default_eps_bearer_qos.allocation_retention_priority.priority_level = 8
        ccr.default_eps_bearer_qos.allocation_retention_priority.pre_emption_vulnerability = E_PRE_EMPTION_VULNERABILITY_PRE_EMPTION_VULNERABILITY_ENABLED
        ccr.default_eps_bearer_qos.allocation_retention_priority.pre_emption_capability = E_PRE_EMPTION_CAPABILITY_PRE_EMPTION_CAPABILITY_DISABLED

        # ccr.user_location_info = b"Tset"
        # ccr.ms_timezone = b"GMT+4"

        ccr.called_station_id = "ims"

        ccr.online = E_ONLINE_DISABLE_ONLINE
        ccr.offline = E_OFFLINE_ENABLE_OFFLINE

        ccr.network_request_support = E_NETWORK_REQUEST_SUPPORT_NETWORK_REQUEST_SUPPORTED
        ccr.origin_state_id = 1448374171

        ccr.bearer_usage = E_BEARER_USAGE_IMS_SIGNALLING

        return ccr
    
    def start_rx_session(self, rx_session: RxSession):
        logger.info(f"Starting RX session: {rx_session}")
        aar = self.create_aar_audio(rx_session)
        self.rx_service.send_rx_request(rx_session, aar, timeout=5)
        ts = time.time()
        rx_session.set_start_time(ts)
        logger.info("RX session started")
        return rx_session

    def start_gx_session(self, gx_session: GxSession):
        logger.info(f"Starting GX session: {gx_session}")
        ccr_i = self.create_ccr_i(gx_session)
        try:
            cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
        except:
            # First one failed. Try again
            logger.info("Sending CCR-I request again")
            cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
        ts = time.time()
        gx_session.set_start_time(ts)
        # gx_session.active = True
        logger.info("GX session started")
        #
        return gx_session

    def stop_gx_session(self, gx_session: GxSession):
        logger.info(f"Stopping GX session: {gx_session}")
        ccr_t = self.create_ccr_t(gx_session)
        cca_t = self.gx_service.send_gx_request(gx_session, ccr_t, timeout=5)
        if not isinstance(cca_t, CreditControlAnswer):
            raise Exception("CCA is not received")
        if cca_t.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            self.gx_service.ip_queue.put_ip(gx_session.framed_ip_address)
            ts = time.time()
            gx_session.set_end_time(ts)
        logger.info("GX session stopped")
        return gx_session

    def create_ccr_t(self, gx_session: GxSession) -> CreditControlRequest:
        ccr = self.gx_service.create_ccr()
        ccr.session_id = gx_session.session_id
        ccr.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST
        ccr.cc_request_number = gx_session.cc_request_number + 1
        #
        ccr.framed_ip_address = ip_to_bytes(gx_session.framed_ip_address)

        ccr.supported_features.vendor_id = VENDOR_TGPP
        ccr.supported_features.feature_list = 1032
        ccr.supported_features.feature_list_id = 1

        ccr.qos_information = None

        ccr.origin_state_id = 1448374171

        return ccr

    def create_aar_audio(self, rx_session: RxSession) -> AaRequest:
        aar = self.create_aar()
        aar.session_id = rx_session.session_id

        aar.specific_action.append(E_SPECIFIC_ACTION_INDICATION_OF_RELEASE_OF_BEARER)
        aar.specific_action.append(E_SPECIFIC_ACTION_ACCESS_NETWORK_INFO_REPORT)
        aar.specific_action.append(E_SPECIFIC_ACTION_INDICATION_OF_FAILED_RESOURCES_ALLOCATION)
        #
        aar.supported_features.vendor_id = VENDOR_TGPP
        aar.supported_features.feature_list = 35
        aar.supported_features.feature_list_id = 1

        # Get gx_session from rx_session.gx_session_id
        gx_session = self.gx_service.gx_app.sessions.get(rx_session.gx_session_id)
        print(gx_session)
        #
        aar.framed_ip_address = ip_to_bytes(gx_session.framed_ip_address)
        aar.origin_state_id = 1268028842

        aar.header.hop_by_hop_identifier = 4
        aar.header.end_to_end_identifier = 4
        aar.header.is_proxyable = True
        #
        mdc = aar.media_component_description
        mdc.media_component_number = 0
        # mdc.af_application_identifier = "urn:3gpp:service.ims.icsi.mmtel".encode()
        mdc.af_application_identifier = "urn:urn-7:3gpp-service.ims.icsi.mmtel-4G".encode()
        mdc.media_type = E_MEDIA_TYPE_AUDIO
        mdc.max_requested_bandwidth_ul = 41000
        mdc.max_requested_bandwidth_dl = 41000
        # 
        media_sub_component = MediaSubComponent()
        media_sub_component.flow_description.append("permit out 17 from 10.130.18.118 32380 to 10.4.25.194 1234".encode())
        media_sub_component.flow_description.append("permit in 17 from 10.4.25.194 to 10.130.18.118 32380".encode())
        #
        media_sub_component.flow_usage = E_FLOW_USAGE_NO_INFORMATION
        media_sub_component.flow_status = E_FLOW_STATUS_ENABLED
        media_sub_component.flow_number = 1
        #
        mdc.media_sub_component.append(media_sub_component)
        #
        media_sub_component = MediaSubComponent()
        media_sub_component.flow_description.append("flow3".encode())
        media_sub_component.flow_description.append("flow4".encode())
        #
        media_sub_component.flow_usage = E_FLOW_USAGE_RTCP
        media_sub_component.flow_status = E_FLOW_STATUS_ENABLED
        media_sub_component.flow_number = 2
        #
        mdc.media_sub_component.append(media_sub_component)

        return aar
