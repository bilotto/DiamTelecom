from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import PolicyCounterStatusReport
from ..app import SyApplication
from ..sessions import SySession
import logging
logger = logging.getLogger(__name__)

# OCS here is represented as SyApplication that will handle the SLR as request
# It sends back the SLA policy counter status report

def handle_request_sy(app: SyApplication, message: Message):
    answer = None
    if isinstance(message, SpendingLimitRequest):
        return handle_slr(app, message)
    elif isinstance(message, SessionTerminationRequest):
        return handle_str(app, message)
    else:
        raise ValueError(f"Message type {type(message)} not supported")

def handle_slr(app: SyApplication, message: SpendingLimitRequest):
    logger.info("Need to handle SLR")
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
        pcsr.policy_counter_identifier = "mobileInternet"
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


