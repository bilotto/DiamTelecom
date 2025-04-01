from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
from .apps import CustomSimpleThreadingApplication, GxApplication, RxApplication
from .session import *
from .message import DiameterMessage
from diameter.message import dump

def handle_request_gx(app: GxApplication, message: Message):
    answer = None
    if isinstance(message, ReAuthRequest):
        answer = handle_rar(app, message)
    elif isinstance(message, AbortSessionRequest):
        answer = handle_asr(app, message)
    # app.stats.increment_based_on_answer(answer)
    return answer

def handle_request_rx(app: RxApplication, message: Message):
    answer = None
    rx_session = app.get_session_by_id(message.session_id)
    if isinstance(message, ReAuthRequest):
        answer = handle_rar(app, message)
    elif isinstance(message, AbortSessionRequest):
        answer = handle_asr(app, message)
        # Need to send STR
        str_message = rx_session.create_str()
        str_message.termination_cause = E_TERMINATION_CAUSE_DIAMETER_LOGOUT
        str_message.origin_host = message.destination_host
        str_message.origin_realm = message.destination_realm
        str_message.destination_host = message.origin_host
        str_message.destination_realm = message.origin_realm
        str_answer = app.send_request_custom(str_message)
        rx_session.add_message(str_message)
        rx_session.add_message(str_answer)
    # app.stats.increment_based_on_answer(answer)
    return answer

def handle_rar(app: CustomSimpleThreadingApplication, message: ReAuthRequest):
    answer = message.to_answer()
    if not isinstance(answer, ReAuthAnswer):
        raise ValueError("Answer is not ReAuthAnswer")
    answer.session_id = message.session_id
    answer.origin_host = message.destination_host
    answer.origin_realm = message.destination_realm
    answer.destination_host = message.origin_host
    answer.destination_realm = message.origin_realm
    #
    session_id = message.session_id
    session = app.get_session_by_id(session_id)
    if not session:
        answer.result_code = E_RESULT_CODE_DIAMETER_UNKNOWN_SESSION_ID
    else:
        req_diameter_message = DiameterMessage(message)
        session.add_message(req_diameter_message)
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
        session.add_message(answer)
    return answer

def handle_asr(app: CustomSimpleThreadingApplication, message: AbortSessionRequest):
    answer = message.to_answer()
    if not isinstance(answer, AbortSessionAnswer):
        raise ValueError("Answer is not AbortSessionAnswer")
    answer.session_id = message.session_id
    answer.origin_host = message.destination_host
    answer.origin_realm = message.destination_realm
    answer.destination_host = message.origin_host
    answer.destination_realm = message.origin_realm
    #
    session_id = message.session_id
    session = app.get_session_by_id(session_id)
    if not session:
        answer.result_code = E_RESULT_CODE_DIAMETER_UNKNOWN_SESSION_ID
    else:
        req_diameter_message = DiameterMessage(message)
        session.add_message(req_diameter_message)
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
        session.add_message(answer)
    return answer