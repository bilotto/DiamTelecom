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


if __name__ == "__main__":
    pcef_node = create_node(PCEF_HOST, PCEF_REALM, ["localhost"], 3869)

    pcef_peers_list = [
        # {
        #     "host": "pcrf",
        #     "port": 3868,
        #     "realm": "example.com",
        #     "ip_addresses": ["127.0.0.1"],
        #     "is_persistent": True,
        #     "is_default": False
        # },
        {
            "host": DSC_HOST,
            "port": 3870,
            "realm": DSC_REALM,
            "ip_addresses": ["127.0.0.1"],
            "is_persistent": False,
            "is_default": False
        }
    ]

    pcef_peers = add_peers(pcef_node, pcef_peers_list)
    pcef = create_gx_app(10, handle_request)
    pcef_node.add_application(pcef, pcef_peers, [PCRF_REALM])
    pcef.node.vendor_id = VENDOR_TGPP
    pcef.node.product_name = "PCEF"
    pcef.node.start()
    pcef.wait_for_ready()

    import time
    time.sleep(5)
    from DiamTelecom.services import GxService

    pcef_config = {}
    pcef_svc = GxService(pcef, pcef_config)

    subs = Subscriber(id="5511986168351", msisdn="5511986168351", imsi="724050000000000")
    gx_session = pcef_svc.create_gx_session(subs)
    gx_session.mcc_mnc = "72405"
    gx_session.apn = "internet"

    ccr_i = pcef_svc.create_ccr_i(
                                PCRF_HOST,
                                PCRF_REALM,
                                gx_session.session_id,
                                gx_session.framed_ip_address,
                                gx_session.mcc_mnc,
                                gx_session.rat_type,
                                gx_session.apn,
                                gx_session.msisdn,
                                gx_session.imsi
                                )
    cca_i = pcef_svc.send_gx_request(gx_session, ccr_i, timeout=10)


    import time
    try:
        while True:
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit) as e:
        pcef_node.stop()
