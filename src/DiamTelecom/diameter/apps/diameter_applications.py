from typing import List, Dict
from .custom_simple_threading_application import CustomSimpleThreadingApplication
from diameter.node import Node
from diameter.message.constants import *
from .gx_app_ import GxApplication
from .sy_app_ import SyApplication

class DiameterApplications:
    apps_per_id: Dict[int, List[CustomSimpleThreadingApplication]]
    apps_per_node: Dict[Node, List[CustomSimpleThreadingApplication]]
    def __init__(self):
        self.apps_per_id = {}
        self.apps_per_node = {}

    def add_application(self, app: CustomSimpleThreadingApplication):
        if not isinstance(app, CustomSimpleThreadingApplication):
            raise Exception("Application is not CustomSimpleThreadingApplication")
        if not self.apps_per_id.get(app.application_id):
            self.apps_per_id[app.application_id] = []
        self.apps_per_id[app.application_id].append(app)
        #
        node = app.node
        if self.apps_per_node.get(node) is None:
            self.apps_per_node[node] = []
        self.apps_per_node[node].append(app)

    @property
    def nodes(self) -> List[Node]:
        return list(self.apps_per_node.keys())
    
    @property
    def apps(self) -> List[CustomSimpleThreadingApplication]:
        apps = []
        for app_list in self.apps_per_id.values():
            apps.extend(app_list)
        return apps
    
    def get_app_per_id(self, app_id: int) -> List[CustomSimpleThreadingApplication]:
        return self.apps_per_id.get(app_id, [])
    
    def get_gx_apps(self) -> List[GxApplication]:
        return self.get_app_per_id(APP_3GPP_GX)
    
    def get_sy_apps(self) -> List[SyApplication]:
        return self.get_app_per_id(APP_3GPP_SY)
    
    @property
    def ports(self) -> List[int]:
        ports = set()
        for node in self.nodes:
            ports.add(node.tcp_port)
            for peer in node.peers.values():
                ports.add(peer.port)
        return list(ports)
    
    def start(self):
        import threading
        threads = []
        for node in self.nodes:
            t = threading.Thread(target=node.start)
            threads.append(t)
            t.start()
            print(f"Node {node} started")
        for t in threads:
            t.join()                                                                                                                        
        print("Nodes started")

    def wait_for_ready(self, timeout=30):
        for app in self.apps:
            app.wait_for_ready(timeout)
            print(f"App {app} ready")

    def stop(self):
        import threading
        threads = []
        for node in self.nodes:
            t = threading.Thread(target=node.stop)
            threads.append(t)
            t.start()
            print(f"Node {node} stopping")
        for t in threads:
            t.join()
        print("Nodes stopped")

