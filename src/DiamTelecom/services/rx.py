from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from ..diameter.app import RxApplication
from ..diameter.session import RxSession

class RxService:
    rx_app: RxApplication
    rx_config: dict

    def __init__(self, rx_app: RxApplication, rx_config: dict):
        self.rx_app = rx_app
        self.rx_config = rx_config
        self.logger = logging.getLogger("DiamTelecom.services")

    @property
    def destination_realm(self) -> str:
        if self.rx_config.get('destination_realm'):
            return self.rx_config['destination_realm']
        return self.rx_app.node.realm_name

    def send_rx_request(self, rx_session: RxSession, message, timeout=5):
        rx_session.add_message(message)
        try:
            response = self.rx_app.send_request_custom(message, timeout)
            rx_session.add_message(response)
            return response
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def create_aar(self, rx_session: RxSession) -> AaRequest:
        aar = rx_session.create_aar()
        #
        aar.header.hop_by_hop_identifier = 4
        aar.header.end_to_end_identifier = 4
        aar.header.is_proxyable = True
        #
        origin_host = self.rx_app.node.origin_host
        origin_realm = self.rx_app.node.realm_name
        destination_realm = self.destination_realm
        aar.origin_host = origin_host.encode()
        aar.origin_realm = origin_realm.encode()
        aar.destination_realm = destination_realm.encode()

        aar.specific_action.append(E_SPECIFIC_ACTION_INDICATION_OF_RELEASE_OF_BEARER)
        aar.specific_action.append(E_SPECIFIC_ACTION_ACCESS_NETWORK_INFO_REPORT)
        aar.specific_action.append(E_SPECIFIC_ACTION_INDICATION_OF_FAILED_RESOURCES_ALLOCATION)
        #
        aar.supported_features = SupportedFeatures()
        aar.supported_features.vendor_id = VENDOR_TGPP
        aar.supported_features.feature_list = 35
        aar.supported_features.feature_list_id = 1

        aar.origin_state_id = 1268028842

        aar.media_component_description = MediaComponentDescription()
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
    
    def create_str(self, rx_session: RxSession) -> SessionTerminationRequest:
        str_ = rx_session.create_str()
        #
        str_.header.hop_by_hop_identifier = 4
        str_.header.end_to_end_identifier = 4
        str_.header.is_proxyable = True
        #
        origin_host = self.rx_app.node.origin_host
        origin_realm = self.rx_app.node.realm_name
        destination_realm = self.destination_realm
        str_.origin_host = origin_host.encode()
        str_.origin_realm = origin_realm.encode()
        str_.destination_realm = destination_realm.encode()
        #
        str_.origin_state_id = 1268028842
        str_.termination_cause = E_TERMINATION_CAUSE_DIAMETER_LOGOUT
        return str_