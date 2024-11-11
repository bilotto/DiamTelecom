from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import SySession, SySessions
from diameter.message.constants import *
from diameter.message.avp.grouped import *
from diameter.message.commands import *

class SyApplication(CustomSimpleThreadingApplication):
    sessions: SySessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = SySessions()

    def create_slr(self, sy_session: SySession) -> SpendingLimitRequest:
        message = sy_session.create_slr()
        origin_host = self.node.origin_host
        origin_realm = self.node.realm_name
        destination_realm = sy_session.destination_realm
        #
        message.origin_host = origin_host.encode()
        message.origin_realm = origin_realm.encode()
        if destination_realm:
            message.destination_realm = destination_realm.encode()
        #
        subscription_id_imsi = SubscriptionId()
        subscription_id_imsi.subscription_id_type = E_SUBSCRIPTION_ID_TYPE_END_USER_IMSI
        subscription_id_imsi.subscription_id_data = sy_session.subscriber.imsi
        message.subscription_id.append(subscription_id_imsi)
        subscription_id_msisdn = SubscriptionId()
        subscription_id_msisdn.subscription_id_type = E_SUBSCRIPTION_ID_TYPE_END_USER_E164
        subscription_id_msisdn.subscription_id_data = sy_session.subscriber.msisdn
        message.subscription_id.append(subscription_id_msisdn)
        return message
    
