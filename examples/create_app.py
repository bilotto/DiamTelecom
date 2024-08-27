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

import yaml

class PeersYaml:
    def __init__(self, file_path):
        self.file_path = file_path
        self.peers_config = self.read_file()
        self.apps = []

    def read_file(self):
        with open(self.file_path, 'r') as stream:
            try:
                return yaml.safe_load(stream)['peers']
            except yaml.YAMLError as exc:
                print(exc)

    def get_peer_attributes(self, peer_id):
        for i in self.peers_config:
            if i['id'] == peer_id:
                return i
            
    # def create_node(self, node_id) -> Node:
    #     node_config = self.get_peer_attributes(node_id)
    #     return create_node(node_config['origin_host'], node_config['origin_realm'], node_config['ip_addresses'], node_config['tcp_port'])
    
    # def add_peers(self, node: Node, peers: List[str]):
    #     peer_list = []
    #     for i in self.peers_config:
    #         if i['id'] in peers:
    #             peer_list.append(i)
    #     add_peers(node, peer_list)

    def create_node_and_add_peers(self, node_id, peer_id_list) -> List[Peer]:
        # node = self.create_node(node_id)
        # return self.add_peers(node, peer_id_list)
        node_config = self.get_peer_attributes(node_id)
        node = create_node(node_config['origin_host'], node_config['origin_realm'], node_config['ip_addresses'], node_config['tcp_port'])
        peer_list = []
        for i in self.peers_config:
            if i['id'] in peer_id_list:
                peer_list.append(i)
        actual_peer_list = add_peers(node, peer_list)
        if node_config['app_id'] == 'gx':
            app = create_gx_app(10, handle_request)
        elif node_config['app_id'] == 'sy':
            app = create_sy_app(10, handle_request)
        node.add_application(app, actual_peer_list)
        self.apps.append(app)
        return app

            

if __name__ == "__main__":
    # Read file and parse the content
    peers_file = "../input/peers.yaml"

    peers_yaml = PeersYaml(peers_file)
    
    peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-0', ['pgw_gtt'])
    peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-1', ['pgw_gtt'])
    peers_yaml.create_node_and_add_peers('aop-guy-guy-sigm-sy-data-0', ['ocs_guyana'])
    peers_yaml.create_node_and_add_peers('aop-guy-guy-sigm-sy-data-1', ['ocs_guyana'])
    peers_yaml.create_node_and_add_peers('aop-guy-mia-sigm-sy-data-0', ['ocs_miami'])
    peers_yaml.create_node_and_add_peers('aop-guy-mia-sigm-sy-data-1', ['ocs_miami'])

    for app in peers_yaml.apps:
        app.node.start()
        # app.wait_for_ready()

    # app = peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-0', ['pgw_gtt'])
    # app.node.start()
    # app.wait_for_ready()


    # How to create an app:
        # pcrf_node = create_node("pcrf", "example.com", ["127.0.0.1"], 3868)

        # pcrf_peers_list = [
        #     {
        #         "host": "pcef",
        #         "port": 3869,
        #         "realm": "example.com",
        #         "ip_addresses": ["localhost"],
        #         "is_persistent": False,
        #         "is_default": False
        #     }
        # ]
        # pcrf_peers = add_peers(pcrf_node, pcrf_peers_list)
        # pcrf = create_gx_app(10, handle_request)
        # pcrf_node.add_application(pcrf, pcrf_peers)

        # pcrf.node.vendor_id = VENDOR_TGPP
        # pcrf.node.product_name = "PCRF"

        # pcrf.node.start()
        # pcrf.wait_for_ready()
