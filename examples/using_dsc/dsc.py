from diameter.message.constants import *
from DiamTelecom.diameter.app import *
from typing import List, Dict
from DiamTelecom.diameter.create_nodes import *
from DiamTelecom.handle_request import handle_request_dsc, handle_request

from DiamTelecom.services import DataService

import logging
# this shows a human-readable message dump in the logs
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)

# this shows a human-readable message dump in the logs
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
from constant import *

dsc_node = create_node('dsc', 'dsc.realm', ['localhost'], 3870)

dsc_gx_peers = [
    {
        "host": "pcrf",
        "port": 3868,
        "realm": "example.com",
        "ip_addresses": ["127.0.0.1"],
        "is_persistent": True,
        "is_default": False
    },
    {
        "host": "pcef",
        "port": 3869,
        "realm": "example.com",
        "ip_addresses": ["localhost"],
        "is_persistent": True,
        "is_default": False
    }
]

gx_peers_obj = add_peers(dsc_node, dsc_gx_peers)
dsc_gx_app = create_gx_app(10, handle_request_dsc)
dsc_node.add_application(dsc_gx_app, gx_peers_obj)
dsc_node.vendor_id = VENDOR_TGPP
dsc_node.product_name = "DSC"

dsc_node.start()

import time
try:
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit) as e:
    dsc_node.stop()
