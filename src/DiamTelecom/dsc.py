from diameter.message.constants import *
from .diameter.app import CustomSimpleThreadingApplication, Node, DiameterApplications
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
    #
    answer = app.send_request(message)
    if answer:
        # answer.route_record.append(app.node.origin_host)
        app.send_answer(answer)
    return True

class DSC:
    node: Node
    apps: DiameterApplications

    def __init__(self, node: Node, apps: DiameterApplications = None):
        self.node = node
        if apps and isinstance(apps, DiameterApplications):
            self.apps = apps
        else:
            self.apps = DiameterApplications()

    def start(self):
        self.node.start()

    def wait_for_ready(self, timeout=30):
        self.apps.wait_for_ready(timeout)

    def stop(self):
        self.node.stop()