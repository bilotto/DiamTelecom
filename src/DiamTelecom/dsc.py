from diameter.message.constants import *
from .diameter.app import CustomSimpleThreadingApplication, GxApplication, RxApplication, SyApplication
from diameter.message.commands import *
from diameter.message.avp.grouped import PolicyCounterStatusReport
import logging
from .diameter.session import *
logger = logging.getLogger(__name__)



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