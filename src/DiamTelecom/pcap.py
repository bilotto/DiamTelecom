import os
import subprocess
import logging
logger = logging.getLogger(__name__)
from typing import List
from datetime import datetime

class Pcap:
    from .diameter.message import DiameterMessage, Message

    def __init__(self, filepath, ports: list = [], sctp=False, filter='diameter'):
        self.filepath = filepath
        self.ports = ports
        self.sctp = sctp
        self.filter = filter
        self.start_timestamp = None
        self.end_timestamp = None
        self.n_diameter_messages = None
        # if start_timestamp:
        #     self.filter += f" && frame.time_epoch >= {start_timestamp}"
        self.pid_file = None
        # print(f"decode_as: {self.decode_as}")

    def __repr__(self):
        return f"Pcap(filepath={self.filepath}, start_date={self.start_date}, end_date={self.end_date}, n_diameter_messages={self.n_diameter_messages})"

    @property
    def filename(self):
        return os.path.basename(self.filepath)
    
    @property
    def filename_no_extension(self):
        return os.path.splitext(self.filename)[0]
    
    @property
    def dirname(self):
        return os.path.dirname(self.filepath)
    
    @property
    def pyshark_obj(self):
        return create_pyshark_object(self)
    
    @property
    def start_date(self):
        return datetime.fromtimestamp(float(self.start_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def end_date(self):
        return datetime.fromtimestamp(float(self.end_timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    @property
    def decode_as(self):
        decode_as = {}
        for port in self.ports:
            if not self.sctp:
                decode_as[f"tcp.port=={port}"] = 'diameter'
            else:
                decode_as[f"sctp.port=={port}"] = 'diameter'
        return decode_as
    
    def get_ports(self):
        command = ""
        for port in self.ports:
            if not self.sctp:
                command += f"-d tcp.port=={port},diameter "
            else:
                command += f"-d sctp.port=={port},diameter "
        return command

    def dump_packets(self, filter, output_file):
        # Use tshark to dump packets to a file
        command = f"tshark -r {self.filepath} {self.get_ports()} -Y \"{filter}\" -w {output_file}"
        # print(f"Running command: {command}")
        subprocess.run(command, shell=True)

    def tcpdump_command(self, interface="any"):
        return f"sudo tcpdump -i {interface} port {','.join(map(str, self.ports))} -w {self.filepath} &"
    
    def get_diameter_messages_from_pkt(self, pkt) -> List[DiameterMessage]:
        pkt_diameter_messages = []
        if isinstance(pkt.diameter_raw.value, list):
            payload_hex = pkt.diameter_raw.value[0]
        else:
            payload_hex = pkt.diameter_raw.value
        diameter_message = DiameterMessage(payload_hex)
        pkt_diameter_messages.append(diameter_message)
        diameter_message.set_timestamp(pkt.frame_info.time_epoch)
        diameter_message.pkt_number = pkt.number
        if pkt.diameter_raw.duplicate_layers:
            for i in pkt.diameter_raw.duplicate_layers:
                payload_hex = i.value
                if isinstance(payload_hex, list):
                    logger.error("payload_hex is list")
                if not isinstance(payload_hex, str):
                    continue
                diameter_bytes = bytes.fromhex(i.value)
                diameter_message = DiameterMessage(Message.from_bytes(diameter_bytes))
                diameter_message.set_timestamp(pkt.frame_info.time_epoch)
                diameter_message.pkt_number = pkt.number
                pkt_diameter_messages.append(diameter_message)

        return pkt_diameter_messages

    def get_diameter_messages_from_pcap(self) -> List[DiameterMessage]:
        pcap_diameter_messages = []
        for pkt in self.pyshark_obj:
            pkt_timestamp = pkt.frame_info.time_epoch
            pkt_number = pkt.number
            pkt_diameter_messages = self.get_diameter_messages_from_pkt(pkt)
            if not pkt_diameter_messages:
                logger.warning(f"No Diameter messages found in packet {pkt_number}")
            for diameter_message in pkt_diameter_messages:
                if not isinstance(diameter_message, DiameterMessage):
                    continue
                diameter_message.set_timestamp(pkt_timestamp)
                diameter_message.pkt_number = pkt_number
                pcap_diameter_messages.append(diameter_message)

        return pcap_diameter_messages

    def get_start_and_end_timestamp(self):
        from datetime import datetime
        # Get the start and end timestamps of the pcap file
        command = f"tshark -r {self.filepath} -T fields -e frame.time_epoch"
        output = subprocess.check_output(command, shell=True).decode().strip().split('\n')
        if not output:
            return None, None
        self.start_timestamp = float(output[0])
        self.end_timestamp = float(output[-1])
        self.n_diameter_messages = len(output)


def create_pyshark_object(pcap_file: Pcap):
    import pyshark
    return pyshark.FileCapture(pcap_file.filepath, decode_as=pcap_file.decode_as, display_filter=pcap_file.filter, include_raw=True, use_json=True, debug=False)



# def get_diameter_messages_from_pkt(pkt) -> List[DiameterMessage]:
#     pkt_diameter_messages = []
#     if isinstance(pkt.diameter_raw.value, list):
#         payload_hex = pkt.diameter_raw.value[0]
#     else:
#         payload_hex = pkt.diameter_raw.value
#     diameter_message = DiameterMessage(payload_hex)
#     pkt_diameter_messages.append(diameter_message)
#     if pkt.diameter_raw.duplicate_layers:
#         for i in pkt.diameter_raw.duplicate_layers:
#             payload_hex = i.value
#             if isinstance(payload_hex, list):
#                 logger.error("payload_hex is list")
#             if not isinstance(payload_hex, str):
#                 continue
#             diameter_bytes = bytes.fromhex(i.value)
#             diameter_message = DiameterMessage(Message.from_bytes(diameter_bytes))
#             pkt_diameter_messages.append(diameter_message)

#     return pkt_diameter_messages

# def get_diameter_messages_from_pcap(pcap: Pcap) -> List[DiameterMessage]:
#     pcap_diameter_messages = []
#     for pkt in pcap.pyshark_obj:
#         pkt_timestamp = pkt.frame_info.time_epoch
#         pkt_number = pkt.number
#         pkt_diameter_messages = get_diameter_messages_from_pkt(pkt)
#         if not pkt_diameter_messages:
#             logger.warning(f"No Diameter messages found in packet {pkt_number}")
#         for diameter_message in pkt_diameter_messages:
#             if not isinstance(diameter_message, DiameterMessage):
#                 continue
#             diameter_message.set_timestamp(pkt_timestamp)
#             diameter_message.pkt_number = pkt_number
#             pcap_diameter_messages.append(diameter_message)

#     return pcap_diameter_messages


from .diameter.message import DiameterMessage, Message
