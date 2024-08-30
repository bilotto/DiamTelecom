from diameter.message.constants import *
from DiamTelecom.diameter.app import *
from typing import List, Dict
import logging
# this shows a human-readable message dump in the logs
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s [%(threadName)s]",
                    level=logging.DEBUG)

# this shows a human-readable message dump in the logs
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

from DiamTelecom.diameter.create_nodes import *
from DiamTelecom.handle_request import handle_request


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
            
    def get_apps(self) -> List[CustomSimpleThreadingApplication]:
        return self.apps

    def create_node_and_add_peers(self, node_id, peer_id_list, node_init_connection=False) -> CustomSimpleThreadingApplication:
        node_config = self.get_peer_attributes(node_id)
        node = create_node(node_config['origin_host'],
                           node_config['origin_realm'],
                           node_config['ip_addresses'],
                           node_config['tcp_port'])
        peer_list = []
        for i in self.peers_config:
            if i['id'] in peer_id_list:
                if node_init_connection == True:
                    i['is_persistent'] = True
                else:
                    i['is_persistent'] = False
                peer_list.append(i)
        actual_peer_list = add_peers(node, peer_list)
        if node_config['app_id'] == 'gx':
            app = create_gx_app(1, handle_request)
        elif node_config['app_id'] == 'sy':
            app = create_sy_app(1, handle_request)
        node.add_application(app, actual_peer_list)
        self.apps.append(app)
        return app

            

if __name__ == "__main__":
    peers_file = "../input/peers.yaml"
    peers_yaml = PeersYaml(peers_file)
    
    peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-0', ['pgw_gtt'])
    peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-1', ['pgw_gtt'])
    # peers_yaml.create_node_and_add_peers('aop-guy-ocm-sigm-gx-data-0', ['pgw_ocm'])
    # peers_yaml.create_node_and_add_peers('aop-guy-ocm-sigm-gx-data-1', ['pgw_ocm'])
    peers_yaml.create_node_and_add_peers('aop-guy-guy-sigm-sy-data-0', ['ocs_guyana'])
    peers_yaml.create_node_and_add_peers('aop-guy-guy-sigm-sy-data-1', ['ocs_guyana'])
    peers_yaml.create_node_and_add_peers('aop-guy-mia-sigm-sy-data-0', ['ocs_miami'])
    peers_yaml.create_node_and_add_peers('aop-guy-mia-sigm-sy-data-1', ['ocs_miami'])

    for app in peers_yaml.get_apps():
        app.node.start()
    for app in peers_yaml.get_apps():
        app.wait_for_ready()

