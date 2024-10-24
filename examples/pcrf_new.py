from DiamTelecom import PCRF
import logging
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",level=logging.DEBUG)
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

pcrf_peers_list = [
    {
        "host": "pcef.example.com",
        "port": 3869,
        "realm": "example.com",
        "ip_addresses": ["localhost"],
        "is_persistent": False,
        "is_default": False
    }
]

pcrf = PCRF("pcrf.example.com", "example.com", ["localhost"], 3868, pcrf_peers_list)
pcrf.start()