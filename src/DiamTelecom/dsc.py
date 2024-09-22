from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import PolicyCounterStatusReport
from diameter.node import Node
#
from .diameter.apps import CustomSimpleThreadingApplication, DiameterApplications
from .diameter.session import *
#
import logging
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
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.logger.info(f"Starting DSC node: {self.node}")
        self.node.start()

    def wait_for_ready(self, timeout=30):
        self.logger.info("Waiting for DSC applications to be ready")
        self.apps.wait_for_ready(timeout)

    def stop(self):
        self.node.stop()