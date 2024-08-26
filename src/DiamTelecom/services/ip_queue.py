from queue import Queue
import socket
import struct
from collections import deque

def ip_to_bytes(ip):
    return socket.inet_aton(ip)

class IpQueue(Queue):
    def __init__(self, start_ip, end_ip):
        super().__init__()
        self.queue = self.generate_ips(start_ip, end_ip)
        # Print print queue
        # print(self.queue)

    def generate_ips(self, start_ip, end_ip):
        start = struct.unpack('>I', socket.inet_aton(start_ip))[0]
        end = struct.unpack('>I', socket.inet_aton(end_ip))[0]
        return deque([socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end+1)])

    # def ip_to_bytes(self, ip):
    #     return socket.inet_aton(ip)

    def get_ip(self):
        return self.get()

    def put_ip(self, ip):
        self.put(ip)
