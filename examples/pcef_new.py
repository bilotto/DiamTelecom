from DiamTelecom import *
import logging
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",level=logging.DEBUG)
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

pcef_peers_list = [
    {
        "host": "pcrf.example.com",
        "port": 3868,
        "realm": "example.com",
        "ip_addresses": ["localhost"],
        "is_persistent": True,
        "is_default": False
    }
]

pcef = PCEF("pcef.example.com", "example.com", ["localhost"], 3869, pcef_peers_list)
pcef.start()

