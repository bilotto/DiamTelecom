# from diameter.node import Node
from DiamTelecom.diameter.constants import *
from DiamTelecom.diameter.app import *
from DiamTelecom.handle_request import handle_request
from typing import List, Dict

import logging
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # this shows a human-readable message dump in the logs
    logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

    pcrf_node = create_node("pcrf", "example.com", ["127.0.0.1"], 3868)

    pcrf_external_peers_list = [
        {
            "host": "pcef",
            "port": 3869,
            "realm": "example.com",
            "ip_addresses": ["localhost"],
            "is_persistent": False,
            "is_default": False
        }
    ]
    pcrf_peers = add_peers(pcrf_node, pcrf_external_peers_list)
    pcrf = create_gx_app(10, handle_request)
    pcrf_node.add_application(pcrf, pcrf_peers)

    pcrf.node.vendor_id = VENDOR_TGPP
    pcrf.node.product_name = "PCRF"

    pcrf.node.start()
    pcrf.wait_for_ready()
