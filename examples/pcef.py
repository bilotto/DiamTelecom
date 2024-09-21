from diameter.message.constants import *
from DiamTelecom.diameter.app import *
from typing import List, Dict
import logging
# this shows a human-readable message dump in the logs
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)

# this shows a human-readable message dump in the logs
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

from DiamTelecom.diameter.create_nodes import *
from DiamTelecom.handle_request import handle_request
from DiamTelecom.services import *
from DiamTelecom import GxService, DataService, Subscriber

if __name__ == "__main__":
    pcef_node = create_node("pcef", "example.com", ["localhost"], 3869)

    pcef_peers_list = [
        {
            "host": "pcrf",
            "port": 3868,
            "realm": "example.com",
            "ip_addresses": ["127.0.0.1"],
            "is_persistent": True,
            "is_default": False
        }
    ]
    pcef_peers = add_peers(pcef_node, pcef_peers_list)
    pcef = create_gx_app(10, handle_request)
    pcef_node.add_application(pcef, pcef_peers)
    pcef.node.vendor_id = VENDOR_TGPP
    pcef.node.product_name = "PCEF"
    pcef.node.start()
    pcef.wait_for_ready()

    gx_config = dict()
    gx_service = GxService(pcef, gx_config)
    data_service = DataService(gx_service)
    data_service._mcc_mnc = "999"
    data_service._apn = "internet"
    data_service._realm = "example.com"

    subscriber = Subscriber(id="5920000075", msisdn="5920000075", imsi="738002000000075")
    gx_session_ = data_service.create_gx_session(subscriber)
    data_service.start_gx_session(gx_session_)