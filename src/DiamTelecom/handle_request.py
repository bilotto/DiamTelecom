from diameter.message.constants import *
from .diameter.app import CustomSimpleThreadingApplication, GxApplication, RxApplication, SyApplication
from diameter.message.commands import *
from diameter.message.avp.grouped import PolicyCounterStatusReport
import logging
from .diameter.session import *
logger = logging.getLogger(__name__)

def handle_request(app: CustomSimpleThreadingApplication, message: Message):
    logger.info(f"Received message {message}")
    if isinstance(message, ReAuthRequest):
        return handle_rar(app, message)
    elif isinstance(message, SpendingLimitRequest):
        return handle_slr(app, message)
    elif isinstance(message, SessionTerminationRequest):
        return handle_str(app, message)
    elif isinstance(message, CreditControlRequest):
        return handle_ccr(app, message)
    return None

def handle_request_dsc(app: CustomSimpleThreadingApplication, message: Message):
    origin_host = message.origin_host
    origin_realm = message.origin_realm
    destination_host = message.destination_host
    destination_realm = message.destination_realm
    #
    logger.info(f"Received message {message} from {origin_realm} to {destination_realm}")
    message.route_record.append(origin_host)
    if isinstance(message, CreditControlRequest):
        pass
    elif isinstance(message, SpendingLimitRequest):
        pass
        # if message.destination_realm.decode() == "sy.guyana.com":
        #     logger.info(f"Will replace realm {message.destination_realm} with dmg.guyana.com")
        #     message.destination_realm = "dmg.guyana.com".encode()
    #
    answer = app.send_request(message)
    if answer:
        # answer.route_record.append(app.node.origin_host)
        app.send_answer(answer)
    return True

def handle_rar(app: CustomSimpleThreadingApplication, message: ReAuthRequest):
    answer = message.to_answer()
    session_id = message.session_id
    session = app.get_session_by_id(session_id)
    if not session:
        logging.error(f"Session with id {session_id} not found. Found: {app.sessions}")
        return None
    session.add_message(message)
    if isinstance(answer, ReAuthAnswer):
        answer.session_id = message.session_id
        answer.origin_host = message.destination_host
        answer.origin_realm = message.destination_realm
        answer.destination_host = message.origin_host
        answer.destination_realm = message.origin_realm 
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
    session.add_message(answer)
    return answer

def handle_slr(app: SyApplication, message: SpendingLimitRequest):
    logger.info("Need to handle SLR")
    if message.auth_application_id == APP_3GPP_SY:
        session_id = message.session_id
        subscription_id = message.subscription_id
        for i in subscription_id:
            if i.subscription_id_type == 0:
                subscriber_msisdn = i.subscription_id_data
            elif i.subscription_id_type == 1:
                subscriber_imsi = i.subscription_id_data
    if app.subscribers:
        print(app.subscribers)
        # Get carrier_id
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
        if subscriber.use_case:
            print(subscriber.use_case)
            if subscriber.use_case.sla_policy_counter_dict:
                answer.policy_counter_status_report = []
                for k, v in subscriber.use_case.sla_policy_counter_dict.items():
                    pcsr = PolicyCounterStatusReport()
                    pcsr.policy_counter_identifier = k
                    pcsr.policy_counter_status = v
                    answer.policy_counter_status_report.append(pcsr)
        elif carrier_id == 1:
            answer.policy_counter_status_report = []
            pcsr = PolicyCounterStatusReport()
            pcsr.policy_counter_identifier = "RG31"
            pcsr.policy_counter_status = "full"
            answer.policy_counter_status_report.append(pcsr)
            # pcsr = PolicyCounterStatusReport()
            # pcsr.policy_counter_identifier = "RG34"
            # pcsr.policy_counter_status = "full"
            # answer.policy_counter_status_report.append(pcsr)
        elif carrier_id == 3:
            answer.policy_counter_status_report = []
            pcsr = PolicyCounterStatusReport()
            pcsr.policy_counter_identifier = "RG31"
            pcsr.policy_counter_status = "disable"
            answer.policy_counter_status_report.append(pcsr)
    session.add_message(answer)
    if answer.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
        session.active = True
    return answer

def handle_str(app: CustomSimpleThreadingApplication, message: SessionTerminationRequest):
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

def handle_ccr(app: CustomSimpleThreadingApplication, message: CreditControlRequest):
    answer = message.to_answer()
    if not isinstance(answer, CreditControlAnswer):
        raise Exception("Not a Credit-Control-Answer message")
    session_id = message.session_id
    print(f"Received message {message} with session_id {session_id}")
    answer.session_id = message.session_id
    answer.origin_host = app.node.origin_host.encode()
    answer.origin_realm = app.node.realm_name.encode()
    answer.destination_realm = message.origin_realm
    answer.cc_request_type = message.cc_request_type
    answer.cc_request_number = message.cc_request_number
    answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
    answer.auth_application_id = message.auth_application_id
    return answer

