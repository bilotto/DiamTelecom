from diameter.message.constants import *
from diameter.message.commands import ReAuthRequest, ReAuthAnswer
from ..apps import GxApplication
import logging
logger = logging.getLogger(__name__)

# PCEF is a GxApplication that only handles RAR as request
# PCRF is a GxApplication that handles CCR as request

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

# def handle_rar(app: CustomSimpleThreadingApplication, message: ReAuthRequest):
#     answer = message.to_answer()
#     if isinstance(answer, ReAuthAnswer):
#         answer.session_id = message.session_id
#         answer.origin_host = message.destination_host
#         answer.origin_realm = message.destination_realm
#         answer.destination_host = message.origin_host
#         answer.destination_realm = message.origin_realm
#     session_id = message.session_id
#     session = app.get_session_by_id(session_id)
#     if session:
#         session.add_message(message)
#         answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
#         session.add_message(answer)
#     else:
#         logger.error(f"Session with id {session_id} not found. App is: {app}, Sessions are: {app.sessions.get_all()}")
#         answer.result_code = E_RESULT_CODE_DIAMETER_UNKNOWN_SESSION_ID
