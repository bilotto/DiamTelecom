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
        #
        realms = node_config.get('realms')
        print(f"realms: {realms}")
        host = node_config['origin_host']
        realm = node_config['origin_realm']
        new_host = f"{host}"
        node = create_node(new_host,
                           realm,
                           node_config['ip_addresses'],
                           node_config['tcp_port'])
        peer_list = []
        for i in self.peers_config:
            if i['id'] in peer_id_list:
                if node_init_connection == True:
                    i['is_persistent'] = True
                else:
                    i['is_persistent'] = False
                # realms.append(i['origin_realm'])
                peer_list.append(i)
        actual_peer_list = add_peers(node, peer_list)
        if node_config['app_id'] == 'gx':
            app = create_gx_app(1, handle_request)
        elif node_config['app_id'] == 'sy':
            app = create_sy_app(1, handle_request)
        node.add_application(app, actual_peer_list, realms)
        app.init_connection = node_init_connection
        if node_config.get('load_balancer'):
            app.load_balancer = True
        # self.apps.append(app)
        self.apps[node_id] = app
        self.apps_config[node_id] = node_config
        return app

    def get_app(self, app_id):
        return self.apps[app_id]
    
    def get_app_config(self, app_id):
        return self.apps_config[app_id]
    
    def start_apps(self):
        import time
        for app in self.get_apps():
            if app.init_connection == True:
                continue
            app.node.start()
        for app in self.get_apps():
            if app.init_connection != True:
                continue
            app.node.start()
        for app in self.get_apps():
            app.wait_for_ready()


peers_file = "../input/peers.yaml"
peers_yaml = PeersYaml(peers_file)

# peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-0', ['miadsc'])
# peers_yaml.create_node_and_add_peers('aop-guy-gtt-sigm-gx-data-1', ['miadsc'])
# peers_yaml.create_node_and_add_peers('pgw_gtt', ['miadsc'])
# peers_yaml.create_node_and_add_peers('miadsc', ['aop-guy-gtt-sigm-gx-data-0', 'aop-guy-gtt-sigm-gx-data-1', 'pgw_gtt'], node_init_connection=True)

peers_yaml.create_node_and_add_peers('aop_gtt_d0', ['miadsc'])
peers_yaml.create_node_and_add_peers('pgw_gtt', ['miadsc'])
peers_yaml.create_node_and_add_peers('miadsc', ['aop_gtt_d0', 'pgw_gtt'], True)

# peers_yaml.start_apps()

if __name__ == "__main__":
    import logging
    import time
    logging.basicConfig(format="%(asctime)s %(levelname)-7s %(message)s",
                        level=logging.DEBUG)
    logging.getLogger("diameter.avp").setLevel(logging.DEBUG)
    logging.getLogger("diameter.message.avp").setLevel(logging.DEBUG)
    logging.getLogger("diameter.node").setLevel(logging.DEBUG)
    logging.getLogger("diameter.application").setLevel(logging.DEBUG)
    logging.getLogger("diameter.connection").setLevel(logging.DEBUG)
    logging.getLogger("diameter.peer").setLevel(logging.DEBUG)
    logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)

    # peers_yaml.start_apps()

