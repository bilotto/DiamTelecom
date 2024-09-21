
from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from ..diameter.app import SyApplication
from ..diameter.session import SySession

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
        return self.ocs.node.realm_name
    
    # def start(self):
    #     self.ocs.custom_start()

    # def stop(self):
    #     self.ocs.custom_stop()
    
    def set_sy_hosts(self, message):
        origin_host = self.ocs.node.origin_host
        origin_realm = self.ocs.node.realm_name
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
        response = self.ocs.send_request(message, timeout)
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
        
        # message = SpendingStatusNotificationRequest()
        # message = self.set_sy_hosts(message)
        # message.session_id = sy_session.session_id
        # message.auth_application_id = APP_3GPP_SY
        # message.policy_counter_status_report = []
        # if policy_counter_dict:
        #     for pc_id, pc_status in policy_counter_dict.items():
        #         pcsr = PolicyCounterStatusReport()
        #         pcsr.policy_counter_identifier = pc_id
        #         pcsr.policy_counter_status = str(pc_status)
        #         message.policy_counter_status_report.append(pcsr)
        # return message

    # def wait_for_sy_session(self, subscriber_msisdn, timeout=3):
    #     start_time = time.time()  # Get the current time
    #     while not self.ocs.get_subscriber_active_session(subscriber_msisdn):
    #         time.sleep(0.1)
    #         logger.info(f"Waiting for Sy session for {subscriber_msisdn}")
    #         if time.time() - start_time > timeout:
    #             break

    #     if self.ocs.get_subscriber_active_session(subscriber_msisdn):
    #         logger.info("Sy session found")
    #         return self.ocs.get_subscriber_active_session(subscriber_msisdn)
    #     return None
