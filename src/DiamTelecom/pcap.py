import os
import subprocess

class Pcap:
    def __init__(self,
                 filepath,
                 ports: list = [],
                 filter='diameter',
                 start_timestamp=None):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.filter = filter
        self.ports = ports
        if start_timestamp:
            self.filter += f" && frame.time_epoch >= {start_timestamp}"

    @property
    def decode_as(self):
        decode_as = {}
        for port in self.ports:
            decode_as[f"tcp.port=={port}"] = 'diameter'
        return decode_as
    
    def get_ports(self):
        command = ""
        for port in self.ports:
            command += f"-d tcp.port=={port},diameter "
        return command
    
    def dump_packets(self, filter, output_file):
        # Use tshark to dump packets to a file
        command = f"tshark -r {self.filepath} {self.get_ports()} -Y \"{filter}\" -w {output_file}"
        # print(f"Running command: {command}")
        subprocess.run(command, shell=True)
    
def create_pyshark_object(pcap_file: Pcap):
    import pyshark
    return pyshark.FileCapture(pcap_file.filepath, decode_as=pcap_file.decode_as, display_filter=pcap_file.filter, debug=False)
