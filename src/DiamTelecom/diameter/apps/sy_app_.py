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
    
def handle_request_ocs(app: SyApplication, message: Message):
    if isinstance(message, SpendingLimitRequest):
        return handle_slr(app, message)
    elif isinstance(message, SessionTerminationRequest):
        return handle_str(app, message)
    else:
        raise ValueError(f"Message type {type(message)} not supported")
    
def handle_slr(app: SyApplication, message: SpendingLimitRequest):
    session_id = message.session_id
    subscription_id = message.subscription_id
    for i in subscription_id:
        if i.subscription_id_type == 0:
            subscriber_msisdn = i.subscription_id_data
        elif i.subscription_id_type == 1:
            subscriber_imsi = i.subscription_id_data
    # if app.subscribers:
    #     print(app.subscribers)
    #     # Get carrier_id
    subscriber = app.subscribers.get_subscriber_by_msisdn_imsi(subscriber_msisdn, subscriber_imsi)
    carrier_id = int(subscriber.carrier_id)
    session = app.sessions.create_sy_session(subscriber, session_id)
    session.add_message(message)
    print(session)
    answer = message.to_answer()
    if isinstance(answer, SpendingLimitAnswer):
        answer.session_id = message.session_id
        answer.origin_host = app.node.origin_host.encode()
        answer.origin_realm = app.node.realm_name.encode()
        answer.auth_application_id = message.auth_application_id
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
        #
        answer.policy_counter_status_report = []
        pcsr = PolicyCounterStatusReport()
        pcsr.policy_counter_identifier = "yourPolicyCounterIdentifier"
        pcsr.policy_counter_status = "ON"
        answer.policy_counter_status_report.append(pcsr)
    session.add_message(answer)
    if answer.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
        session.active = True
    return answer


def handle_str(app: SyApplication, message: SessionTerminationRequest):
    answer = message.to_answer()
    session_id = message.session_id
    session = app.get_session_by_id(session_id)
    session.add_message(message)
    print(session)
    if isinstance(answer, SessionTerminationAnswer):
        answer.session_id = message.session_id
        answer.origin_host = message.destination_host
        answer.origin_realm = message.destination_realm
        answer.destination_host = message.origin_host
        answer.destination_realm = message.origin_realm
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
    session.add_message(answer)
    return answer



class Ocs(SyApplication):
    def __init__(self, max_threads: int):
        super().__init__(application_id=APP_3GPP_SY, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=handle_request_ocs)
