from .session import GxSessions, GxSession
from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from .app import GxApplication, SyApplication


def handle_request_pcef(app: GxApplication, message: ReAuthRequest):
    if not isinstance(app, GxApplication):
        raise TypeError("app must be an instance of GxApplication")
    if not isinstance(message, ReAuthRequest):
        raise TypeError("message must be an instance of ReAuthRequest")
    #
    answer = message.to_answer()
    if not isinstance(answer, ReAuthAnswer):
        raise TypeError("answer must be an instance of ReAuthAnswer")
    # For RAR, check if the session exists
    session_id = message.session_id
    session = app.sessions.get_session(session_id)
    if not session:
        answer.result_code = E_RESULT_CODE_DIAMETER_UNKNOWN_SESSION_ID
        return answer
    # Add the message to the session
    session.add_message(message)
    # Prepare the answer
    answer.session_id = message.session_id
    answer.origin_host = app.node.origin_host.encode()
    answer.origin_realm = app.node.realm_name.encode()
    answer.destination_host = message.origin_host
    answer.destination_realm = message.origin_realm
    answer.auth_application_id = message.auth_application_id
    answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
    # Add the answer to the session
    session.add_message(answer)
    return answer


    
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
    # print(session)
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
    # print(session)
    if isinstance(answer, SessionTerminationAnswer):
        answer.session_id = message.session_id
        answer.origin_host = message.destination_host
        answer.origin_realm = message.destination_realm
        answer.destination_host = message.origin_host
        answer.destination_realm = message.origin_realm
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
    session.add_message(answer)
    return answer


def handle_request_ocs(app: SyApplication, message: Message):
    if isinstance(message, SpendingLimitRequest):
        return handle_slr(app, message)
    elif isinstance(message, SessionTerminationRequest):
        return handle_str(app, message)
    else:
        raise ValueError(f"Message type {type(message)} not supported")
