
from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from ..diameter.app import SyApplication
from ..diameter.session import SySession
import time

class SyService:
    sy_app: SyApplication
    sy_config: dict

    def __init__(self, sy_app: SyApplication, sy_config: dict):
        self.sy_app = sy_app
        self.sy_config = sy_config
        self.logger = logging.getLogger(__name__)

    @property
    def sy_destination_host(self) -> str:
        if self.sy_config.get('destination_host'):
            return self.sy_config['destination_host']
        return None
    
    @property
    def sy_destination_realm(self) -> str:
        if self.sy_config.get('destination_realm'):
            return self.sy_config['destination_realm']
        return self.sy_app.node.realm_name
    
    def set_sy_hosts(self, message):
        origin_host = self.sy_app.node.origin_host
        origin_realm = self.sy_app.node.realm_name
        if self.sy_destination_host:
            destination_host = self.sy_destination_host
            message.destination_host = destination_host.encode()
        
        destination_realm = self.sy_destination_realm
        message.origin_host = origin_host.encode()
        message.origin_realm = origin_realm.encode()
        
        message.destination_realm = destination_realm.encode()
        # message.route_record = origin_host.encode()
        return message
    
    def send_sy_request(self, sy_session: SySession, message, timeout=5):
        sy_session.add_message(message)
        response = self.sy_app.send_request_custom(message, timeout)
        sy_session.add_message(response)
        return response

    def create_ssnr(self, sy_session: SySession, policy_counter_dict: dict = None) -> SpendingStatusNotificationRequest:
        message = sy_session.create_ssnr()
        message = self.set_sy_hosts(message)
        if policy_counter_dict:
            for pc_id, pc_status in policy_counter_dict.items():
                pcsr = PolicyCounterStatusReport()
                pcsr.policy_counter_identifier = pc_id
                pcsr.policy_counter_status = str(pc_status)
                message.policy_counter_status_report.append(pcsr)
        return message
    
    def wait_for_sy_session(self, subscriber_msisdn, timeout=3) -> SySession:
        self.logger.info(f"Waiting for Sy session for {subscriber_msisdn}")
        start_time = time.time()  # Get the current time
        while not self.sy_app.get_subscriber_active_session(subscriber_msisdn):
            time.sleep(0.1)
            self.logger.info(f"Waiting for Sy session for {subscriber_msisdn}")
            if time.time() - start_time > timeout:
                break

        if self.sy_app.get_subscriber_active_session(subscriber_msisdn):
            self.logger.info("Sy session found")
            return self.sy_app.get_subscriber_active_session(subscriber_msisdn)
        return None