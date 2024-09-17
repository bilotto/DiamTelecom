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
from DiamTelecom.handle_request import handle_request
from constant import *
import time

if __name__ == "__main__":
    pcrf_node = create_node(PCRF_HOST, PCRF_REALM, ["127.0.0.1"], PCRF_PORT)
    pcrf_node.vendor_id = VENDOR_TGPP
    pcrf_node.product_name = "PCRF"

    pcrf_peers_list = [
        {
            "host": DSC_HOST,
            "port": DSC_PORT,
            "realm": DSC_REALM,
            "ip_addresses": ["127.0.0.1"],
            "is_persistent": False,
            "is_default": False
        }
    ]
    pcrf_peers = add_peers(pcrf_node, pcrf_peers_list)
    pcrf = create_gx_app(10, handle_request)
    pcrf_node.add_application(pcrf, pcrf_peers, [PCRF_REALM, PCEF_REALM])

    pcrf.node.start()
    pcrf.wait_for_ready()

    try:
        while True:
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit) as e:
        pcrf_node.stop()
