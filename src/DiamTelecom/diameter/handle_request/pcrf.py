from diameter.message.constants import *
from diameter.message.commands import CreditControlRequest, CreditControlAnswer
from ..apps import GxApplication
from ..sessions import GxSession, SySession
import logging
logger = logging.getLogger(__name__)

# PCEF is a GxApplication that only handles RAR as request
# PCRF is a GxApplication that handles CCR as request

def handle_request_pcrf(app: GxApplication, message: CreditControlRequest):
    if not isinstance(app, GxApplication):
        raise TypeError("app must be an instance of GxApplication")
    if not isinstance(message, CreditControlRequest):
        raise TypeError("message must be an instance of CreditControlRequest")
    #
    answer = message.to_answer()
    logger.debug(f"Received CCR message: {message}")
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
        print(subscriber)
        if not subscriber:
            raise ValueError(f"Subscriber {msisdn} not found")
            # subscriber = app.subscribers.create_subscriber(id=msisdn, msisdn=msisdn, imsi=imsi)
        if app.sy_app:
            sy_app = app.sy_app
            # Need to create Sy session
            sy_session_id = sy_app.node.session_generator.next_id()
            sy_session = SySession(subscriber, sy_session_id)
            sy_session.set_gx_session_id(message.session_id)
            sy_session.destination_realm = "sy.gy.c1.atni.local"
            sy_app.sessions.add_session(sy_session)
            # Need to send SLR
            slr = sy_app.create_slr(sy_session)
            try:
                sla = sy_app.send_request_custom(slr)
            except Exception as e:
                logger.error(f"SLR failed: {e}")
                raise ValueError("SLR failed")
            # Need to wait for SLA
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