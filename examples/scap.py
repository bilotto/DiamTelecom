from diameter.node import Node
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

def handle_request(app: CustomSimpleThreadingApplication, message: Message):
    pass

if __name__ == "__main__":
    import os
    ORIGIN_HOST = os.getenv("ORIGIN_HOST") or "pcef"
    ORIGIN_REALM = os.getenv("ORIGIN_REALM") or "example.com"
    DESTINATION_HOST = os.getenv("DESTINATION_HOST") or "pcrf"
    DESTINATION_REALM = os.getenv("DESTINATION_REALM") or "example.com"
    DESTINATION_IP = os.getenv("DESTINATION_IP") or "127.0.0.1"
    DESTINATION_PORT = os.getenv("DESTINATION_PORT") or 3868

    pcef_node = create_node(ORIGIN_HOST, ORIGIN_REALM, ["localhost"], 3869)

    pcef_peers_list = [
        {
            "host": DESTINATION_HOST,
            "port": DESTINATION_PORT,
            "realm": DESTINATION_REALM,
            "ip_addresses": [DESTINATION_IP],
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
