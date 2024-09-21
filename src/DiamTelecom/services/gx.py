from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from ..diameter.app import GxApplication
from ..diameter.session import GxSession
import time

class GxService:
    gx_app: GxApplication
    gx_config: dict
    def __init__(self,
                 gx_app: GxApplication,
                 gx_config: dict
                 ):
        self.gx_app = gx_app
        self.gx_config = gx_config
        self.request_count = dict()
        self.request_count['success'] = 0
        self.request_count['failure'] = 0
        self.logger = logging.getLogger(__name__)

    # def start(self):
    #     self.gx_app.custom_start()

    # def stop(self):
    #     self.gx_app.custom_stop()


    def set_gx_config(self, gx_config: dict):
        self.gx_config = gx_config

    @property
    def destination_realm(self):
        if self.gx_config.get('destination_realm'):
            return self.gx_config['destination_realm']
        return self.gx_app.node.realm_name
    
    def send_gx_request(self, gx_session: GxSession, request: Message, timeout=5):
        try:
            answer = self.gx_app.send_request(request, timeout)
            gx_session.add_message(request)
            gx_session.add_message(answer)
            self.request_count['success'] += 1
            return answer
        except Exception as e:
            self.request_count['failure'] += 1
            logger.error(f"Error sending request: {e}")
            raise e

    def create_ccr_i(self,
                     gx_session: GxSession,
                     mcc_mnc='999',
                     apn='internet') -> CreditControlRequest:
        ccr_i = gx_session.create_ccr_i()
        ccr_i.auth_application_id = APP_3GPP_GX
        #
        origin_host = self.gx_app.node.origin_host
        origin_realm = self.gx_app.node.realm_name
        destination_realm = self.destination_realm
        ccr_i.origin_host = origin_host.encode()
        ccr_i.origin_realm = origin_realm.encode()
        ccr_i.destination_realm = destination_realm.encode()
        #
        ccr_i.header.hop_by_hop_identifier = 2
        ccr_i.header.end_to_end_identifier = 2
        ccr_i.header.is_proxyable = True
        ccr_i.header.application_id = APP_3GPP_GX
        #
        ccr_i.rat_type = E_RAT_TYPE_EUTRAN
        ccr_i.ip_can_type = E_IP_CAN_TYPE_3GPP_EPS
        #
        ccr_i.sgsn_mcc_mnc = mcc_mnc
        ccr_i.called_station_id = apn
        #
        ccr_i.supported_features = SupportedFeatures()
        ccr_i.supported_features.vendor_id = VENDOR_TGPP
        ccr_i.supported_features.feature_list = 1032
        ccr_i.supported_features.feature_list_id = 1
        #
        ccr_i.qos_information = QosInformation()
        ccr_i.qos_information.apn_aggregate_max_bitrate_ul = 300000000
        ccr_i.qos_information.apn_aggregate_max_bitrate_dl = 150000000
        #
        ccr_i.default_eps_bearer_qos = DefaultEpsBearerQos()
        ccr_i.default_eps_bearer_qos.qos_class_identifier = E_QOS_CLASS_IDENTIFIER_QCI_9
        ccr_i.default_eps_bearer_qos.allocation_retention_priority.priority_level = 8
        ccr_i.default_eps_bearer_qos.allocation_retention_priority.pre_emption_capability = E_PRE_EMPTION_CAPABILITY_PRE_EMPTION_CAPABILITY_DISABLED
        ccr_i.default_eps_bearer_qos.allocation_retention_priority.pre_emption_vulnerability = E_PRE_EMPTION_VULNERABILITY_PRE_EMPTION_VULNERABILITY_ENABLED
        #
        ccr_i.bearer_usage = E_BEARER_USAGE_GENERAL
        ccr_i.network_request_support = E_NETWORK_REQUEST_SUPPORT_NETWORK_REQUEST_SUPPORTED
        ccr_i.origin_state_id = 1448374171
        #
        return ccr_i
    
    def create_ccr_t(self, gx_session: GxSession) -> CreditControlRequest:
        ccr_t = gx_session.create_ccr_t()
        ccr_t.auth_application_id = APP_3GPP_GX
        ccr_t.origin_host = self.gx_app.node.origin_host.encode()
        ccr_t.origin_realm = self.gx_app.node.realm_name.encode()
        ccr_t.destination_realm = self.destination_realm.encode()
        ccr_t.header.hop_by_hop_identifier = 2
        ccr_t.header.end_to_end_identifier = 2
        ccr_t.header.is_proxyable = True
        ccr_t.header.application_id = APP_3GPP_GX
        return ccr_t

    def wait_for_gx_raa(self, gx_session: GxSession, current_message_count=None, timeout=3):
        self.logger.info("Waiting for Gx RAR/RAA")
        if not current_message_count:
            current_message_count = len(gx_session.messages)
        start_time = time.time()
        self.logger.info(f"Waiting for Gx RAR/RAA for {gx_session.session_id}")
        # while not isinstance(gx_session.last_message, ReAuthAnswer) and len(gx_session.messages) <= current_message_count + 2:
        while not isinstance(gx_session.last_message, ReAuthAnswer) and len(gx_session.messages) <= current_message_count:
            time.sleep(0.1)
            self.logger.debug(f"Waiting for Gx RAR/RAA for {gx_session.session_id}")
            if time.time() - start_time > timeout:
                self.logger.warn("Timeout")
                return False
        return True
