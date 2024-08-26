from .ip_queue import IpQueue, ip_to_bytes
from DiamTelecom.diameter import *
from DiamTelecom.telecom.subscriber import Subscriber
from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
import time
import logging
logger = logging.getLogger(__name__)

class RxService:
    rx_app: RxApplication
    rx_config: dict

    def __init__(self, rx_app: RxApplication, rx_config: dict):
        self.rx_app = rx_app
        self.rx_config = rx_config

    @property
    def af(self):
        return self.rx_app

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
    
    def start(self):
        self.af.custom_start()

    def stop(self):
        self.af.custom_stop()

    def send_rx_request(self, rx_session: RxSession, message, timeout=5):
        rx_session.add_message(message)
        response = self.af.send_request(message, timeout)
        rx_session.add_message(response)

    def set_rx_hosts(self, rx_message):
        origin_host = self.af.node.origin_host
        origin_realm = self.af.node.realm_name
        destination_host = self.rx_destination_host
        destination_realm = self.rx_destination_realm
        rx_message.origin_host = origin_host.encode()
        rx_message.origin_realm = origin_realm.encode()
        rx_message.destination_host = destination_host.encode()
        rx_message.destination_realm = destination_realm.encode()
        return rx_message

    def create_aar(self) -> AaRequest:
        aar = AaRequest()
        aar = self.set_rx_hosts(aar)
        aar.auth_application_id = APP_3GPP_RX
        return aar

    def create_str(self):
        str_ = SessionTerminationRequest()
        str_ = self.set_rx_hosts(str_)
        str_.auth_application_id = APP_3GPP_RX
        return str_

    def create_rx_session(self, subscriber: Subscriber, gx_session: GxSession):
        rx_session_id = self.af.node.session_generator.next_id()
        # rx_session = RxSession(subscriber, rx_session_id, gx_session)
        rx_session = RxSession(subscriber, rx_session_id, gx_session.session_id)
        return rx_session

class SyService:
    sy_app: SyApplication
    sy_config: dict

    def __init__(self, sy_app: SyApplication, sy_config: dict):
        self.sy_app = sy_app
        self.sy_config = sy_config

    @property
    def ocs(self):
        return self.sy_app
    
    @property
    def sy_destination_host(self) -> str:
        if self.sy_config.get('destination_host'):
            return self.sy_config['destination_host']
        return None
    
    @property
    def sy_destination_realm(self) -> str:
        if self.sy_config.get('destination_realm'):
            return self.sy_config['destination_realm']
        return None
    
    def start(self):
        self.ocs.custom_start()

    def stop(self):
        self.ocs.custom_stop()
    
    def set_sy_hosts(self, message):
        origin_host = self.ocs.node.origin_host
        origin_realm = self.ocs.node.realm_name
        destination_host = self.sy_destination_host
        destination_realm = self.sy_destination_realm
        message.origin_host = origin_host.encode()
        message.origin_realm = origin_realm.encode()
        message.destination_host = destination_host.encode()
        message.destination_realm = destination_realm.encode()
        # message.route_record = origin_host.encode()
        return message
    
    def send_sy_request(self, sy_session: SySession, message, timeout=5):
        sy_session.add_message(message)
        response = self.ocs.send_request(message, timeout)
        sy_session.add_message(response)
        return response

    def create_ssnr(self,
                    sy_session: SySession,
                    policy_counter_dict: dict = None) -> SpendingStatusNotificationRequest:
        message = SpendingStatusNotificationRequest()
        message = self.set_sy_hosts(message)
        message.session_id = sy_session.session_id
        message.auth_application_id = APP_3GPP_SY
        message.policy_counter_status_report = []
        if policy_counter_dict:
            for pc_id, pc_status in policy_counter_dict.items():
                pcsr = PolicyCounterStatusReport()
                pcsr.policy_counter_identifier = pc_id
                pcsr.policy_counter_status = str(pc_status)
                message.policy_counter_status_report.append(pcsr)
        return message

    def wait_for_sy_session(self, subscriber_msisdn, timeout=3):
        start_time = time.time()  # Get the current time
        while not self.ocs.get_subscriber_active_session(subscriber_msisdn):
            time.sleep(0.1)
            logger.info(f"Waiting for Sy session for {subscriber_msisdn}")
            if time.time() - start_time > timeout:
                break

        if self.ocs.get_subscriber_active_session(subscriber_msisdn):
            logger.info("Sy session found")
            return self.ocs.get_subscriber_active_session(subscriber_msisdn)
        return None

class GxService:
    gx_app: GxApplication
    gx_config: dict
    def __init__(self,
                 gx_app: GxApplication,
                 gx_config: dict
                 ):
        self.gx_app = gx_app
        self.gx_config = gx_config
        self.ip_queue = IpQueue(gx_config['ip_start'], gx_config['ip_end'])

    @property
    def pcef(self):
        return self.gx_app

    @property
    def gx_destination_host(self):
        return self.gx_config.get('destination_host')

    @property
    def gx_destination_realm(self):
        return self.gx_config.get('destination_realm')

    def start(self):
        self.pcef.custom_start()

    def stop(self):
        self.pcef.custom_stop()

    def send_gx_request(self, gx_session: GxSession, ccr: CreditControlRequest, timeout=5):
        gx_session.add_message(ccr)
        cca = self.pcef.send_request(ccr, timeout)
        gx_session.add_message(cca)
        return cca

    def set_gx_hosts(self, message):
        origin_host = self.pcef.node.origin_host
        origin_realm = self.pcef.node.realm_name
        destination_host = self.gx_destination_host
        destination_realm = self.gx_destination_realm
        message.origin_host = origin_host.encode()
        message.origin_realm = origin_realm.encode()
        # message.destination_host = destination_host.encode() if destination_host else None
        message.destination_realm = destination_realm.encode() if destination_realm else None
        return message
   
    def create_ccr(self) -> CreditControlRequest:
        ccr = CreditControlRequest()
        ccr = self.set_gx_hosts(ccr)
        ccr.auth_application_id = APP_3GPP_GX
        ccr.header.hop_by_hop_identifier = 2
        ccr.header.end_to_end_identifier = 2
        ccr.header.is_proxyable = True
        return ccr
    
    def create_gx_session(self, subscriber: Subscriber):
        gx_session_id = self.pcef.node.session_generator.next_id()
        framed_ip_address = self.ip_queue.get_ip()
        gx_session = self.pcef.sessions.create_session(subscriber, gx_session_id, framed_ip_address)
        return gx_session

    def wait_for_gx_raa(self, gx_session: GxSession, current_message_count=None, timeout=3):
        logger.info("Waiting for Gx RAR/RAA")
        if not current_message_count:
            current_message_count = len(gx_session.messages)
        start_time = time.time()
        logger.info(f"Waiting for Gx RAR/RAA for {gx_session.session_id}")
        # while not isinstance(gx_session.last_message, ReAuthAnswer) and len(gx_session.messages) <= current_message_count + 2:
        while not isinstance(gx_session.last_message, ReAuthAnswer) and len(gx_session.messages) <= current_message_count:
            time.sleep(0.1)
            logger.debug(f"Waiting for Gx RAR/RAA for {gx_session.session_id}")
            if time.time() - start_time > timeout:
                logger.warn("Timeout")
                return False
        return True

class Service:
    gx_service: GxService
    rx_service: RxService
    sy_service: SyService

    def __init__(self,
                 gx_service: GxService,
                 rx_service: RxService = None,
                 sy_service: SyService = None,
                 ):
        self.gx_service = gx_service
        self.rx_service = rx_service
        self.sy_service = sy_service

    @property
    def all_peers_ports(self):
        ports = []
        for peer in self.gx_service.gx_config['peers']:
            ports.append(peer['port'])
        if self.rx_service:
            for peer in self.rx_service.rx_config['peers']:
                ports.append(peer['port'])
        if self.sy_service:
            for peer in self.sy_service.sy_config['peers']:
                ports.append(peer['port'])
        return ports

    def start(self):
        logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
        self.gx_service.start()
        time.sleep(1)
        if self.sy_service:
            self.sy_service.start()
        if self.rx_service:
            self.rx_service.start()
        time.sleep(1)
        logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

    def stop(self):
        logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
        self.gx_service.stop()
        if self.rx_service:
            self.rx_service.stop()
        if self.sy_service:
            self.sy_service.stop()