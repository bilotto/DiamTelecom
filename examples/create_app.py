from diameter.message.constants import *
from DiamTelecom.diameter.app import *
from typing import List, Dict
from DiamTelecom.diameter.create_nodes import *
from DiamTelecom.handle_request import handle_request

from DiamTelecom.services import DataService

import yaml

class PeersYaml:
    def __init__(self, file_path):
        self.file_path = file_path
        self.peers_config = self.read_file()
        # self.apps = []
        self.apps = dict()
        self.apps_config = dict()

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
        return list(self.apps.values())

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
        if node_init_connection == True:
            app.init_connection = True
        # self.apps.append(app)
        self.apps[node_id] = app
        self.apps_config[node_id] = node_config
        return app

    def get_app(self, app_id):
        return self.apps[app_id]
    
    def get_app_config(self, app_id):
        return self.apps_config[app_id]


# if __name__ == "__main__":
peers_file = "../input/peers.yaml"
peers_yaml = PeersYaml(peers_file)

# peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-0', ['miadsc'])
# peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-1', ['miadsc'])
# peers_yaml.create_node_and_add_peers('pgw_gtt', ['miadsc'])
# peers_yaml.create_node_and_add_peers('miadsc', ['aop-guy-gtt-sigm-gx-data-0', 'aop-guy-gtt-sigm-gx-data-1', 'pgw_gtt'], node_init_connection=True)


peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-0', ['pgw_gtt'])
peers_yaml.create_node_and_add_peers('aop-guy-guy-sigm-sy-data-0', ['ocs_guyana'])
peers_yaml.create_node_and_add_peers('pgw_gtt', ['aop-guy-gtt-sigm-gx-data-0'], True)
peers_yaml.create_node_and_add_peers('ocs_guyana', ['aop-guy-guy-sigm-sy-data-0'], True)

