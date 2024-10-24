from .custom_simple_threading_application import CustomSimpleThreadingApplication
from ..sessions import GxSessions, GxSession
from diameter.message.constants import *
from diameter.message.commands import *

class GxApplication(CustomSimpleThreadingApplication):
    sessions: GxSessions
    def __init__(self, application_id, is_acct_application, is_auth_application, max_threads, request_handler):
        super().__init__(application_id, is_acct_application, is_auth_application, max_threads, request_handler)
        self.sessions = GxSessions()
        self.sy_app = None

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

def handle_request_pcrf(app: GxApplication, message: CreditControlRequest):
    if not isinstance(app, GxApplication):
        raise TypeError("app must be an instance of GxApplication")
    if not isinstance(message, CreditControlRequest):
        raise TypeError("message must be an instance of CreditControlRequest")
    #
    answer = message.to_answer()
    if not isinstance(answer, CreditControlAnswer):
        raise TypeError("answer must be an instance of CreditControlAnswer")
    if message.cc_request_type == E_CC_REQUEST_TYPE_INITIAL_REQUEST:
        # Create a new session.
        # For that, first identify the subscriber
        for i in message.subscription_id:
            if i.subscription_id_type == 0:
                msisdn = i.subscription_id_data
            elif i.subscription_id_type == 1:
                imsi = i.subscription_id_data
        subscriber = app.subscribers.get_subscriber_by_msisdn(msisdn)
        if not subscriber:
            raise ValueError(f"Subscriber {msisdn} not found")
            # subscriber = app.subscribers.create_subscriber(id=msisdn, msisdn=msisdn, imsi=imsi)
        # For now create the session manually
        # todo: create session through the app object
        framed_ip_address = message.framed_ip_address
        apn = message.called_station_id
        gx_session = GxSession(subscriber, message.session_id, framed_ip_address, apn)
        app.sessions.add_session(gx_session)
        answer.session_id = message.session_id
        answer.origin_host = app.node.origin_host.encode()
        answer.origin_realm = app.node.realm_name.encode()
        # answer.destination_realm = message.origin_realm
        answer.auth_application_id = message.auth_application_id
        #
        answer.cc_request_type = message.cc_request_type
        answer.cc_request_number = message.cc_request_number
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
        gx_session.start()
    elif message.cc_request_type == E_CC_REQUEST_TYPE_UPDATE_REQUEST:
        # Find the session
        gx_session = app.sessions.get_session(message.session_id)
        if not gx_session:
            raise ValueError(f"Session {message.session_id} not found")
        answer.session_id = message.session_id
        answer.origin_host = app.node.origin_host.encode()
        answer.origin_realm = app.node.realm_name.encode()
        # answer.destination_realm = message.origin_realm
        answer.auth_application_id = message.auth_application_id
        #
        answer.cc_request_type = message.cc_request_type
        answer.cc_request_number = message.cc_request_number
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
    elif message.cc_request_type == E_CC_REQUEST_TYPE_TERMINATION_REQUEST:
        # Find the session
        gx_session = app.sessions.get_session(message.session_id)
        if not gx_session:
            raise ValueError(f"Session {message.session_id} not found")
        answer.session_id = message.session_id
        answer.origin_host = app.node.origin_host.encode()
        answer.origin_realm = app.node.realm_name.encode()
        # answer.destination_realm = message.origin_realm
        answer.auth_application_id = message.auth_application_id
        #
        answer.cc_request_type = message.cc_request_type
        answer.cc_request_number = message.cc_request_number
        answer.result_code = E_RESULT_CODE_DIAMETER_SUCCESS
        gx_session.end()
    else:
        raise ValueError(f"Unknown cc_request_type {message.cc_request_type}")
    return answer


# class PCEF(GxApplication):
#     def __init__(self, max_threads: int):
#         super().__init__(application_id=APP_3GPP_GX, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=handle_request_pcef)

# class PCRF(GxApplication):
#     def __init__(self, max_threads: int):
#         super().__init__(application_id=APP_3GPP_GX, is_acct_application=False, is_auth_application=True, max_threads=max_threads, request_handler=handle_request_pcrf)