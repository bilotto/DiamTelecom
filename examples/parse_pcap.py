from diameter.message import *
from DiamTelecom import *
from DiamTelecom.diameter.constants import *
#
import pyshark

import logging
import sys
import os
logging.basicConfig(format="%(asctime)s %(name)-22s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

from data_input import diameter_fields, avp_values

def set_fields_from_pkt(diameter_message: DiameterMessage, pkt):
    fields = {}
    for p in pkt.get_multiple_layers('diameter'):
        cmd_code = p.get_field_value('cmd_code')
        flags_request = p.get_field_value('flags_request')
        cc_request_type = p.get_field_value('cc-request-type')
        session_id = p.get_field_value('session_id')
        # check these fields against the ones in the object
        message_name = name_diameter_message(cmd_code, flags_request, cc_request_type)
        print("Message Name:", message_name)
        if message_name != diameter_message.name:
            continue
        if diameter_message.session_id and diameter_message.session_id != session_id:
            continue
        for field in diameter_fields.get(message_name, []):
            try:
                if p.get_field_value(field):
                    avp_value = p.get_field_value(field)
                    if ":" in avp_value:
                        # Remover os ':' para que possamos converter de hex para bytes
                        hex_string = avp_value.replace(':', '')
                        # Convertendo a string hexadecimal em bytes
                        byte_data = bytes.fromhex(hex_string)
                        # Decodificando os bytes para obter a string ASCII
                        avp_value = byte_data.decode('ascii')
                    if avp_values.get(field):
                        fields[field] = avp_values.get(field).get(avp_value) or avp_value
                    else:
                        fields[field] = avp_value
            except:
                logger.warning(f"Could not get field info {field}")
                pass
    diameter_message.avps.set_avps(fields)

def process_pkt(pkt, session_manager: SessionManager):
    subscribers = session_manager.subscribers
    gx_sessions = session_manager.gx_sessions
    rx_sessions = session_manager.rx_sessions
    sy_sessions = session_manager.sy_sessions
    #
    app_id = int(pkt.diameter.applicationid)
    request = int(pkt.diameter.flags_request)
    cmd_code = int(pkt.diameter.cmd_code)
    pkt_timestamp = pkt.frame_info.time_epoch
    cc_request_type = pkt.diameter.get_field_value("CC-Request-Type")
    #
    session_id = pkt.diameter.session_id
    framed_ip_address = pkt.diameter.get_field_value("framed_ip_address_ipv4")
    msisdn = pkt.diameter.get_field_value("e164_msisdn")
    imsi = pkt.diameter.get_field_value("e212_imsi")
    #
    country_code = pkt.diameter.get_field_value("e164_country_code")
    mcc = pkt.diameter.get_field_value("e212_mcc")
    mnc = pkt.diameter.get_field_value("e212_mnc")
    diameter_message = create_diameter_message(cmd_code, request, cc_request_type)
    diameter_message.set_timestamp(pkt_timestamp)
    diameter_message.set_session_id(session_id)
    set_fields_from_pkt(diameter_message, pkt)
    if app_id == APP_3GPP_GX:
        if diameter_message.name == CCR_I:
            if not subscribers.get_subscriber(msisdn):
                subscriber = subscribers.create_subscriber(id=msisdn, msisdn=msisdn, imsi=imsi)
            if gx_sessions.get(session_id):
                # The pcap sometimes has duplicated messages
                logging.warning(f"GxSession with session_id {session_id} already exists")
                return
            gx_session = gx_sessions.create_gx_session(subscriber, session_id, framed_ip_address)
            gx_session.set_start_time(pkt_timestamp)
        else:
            gx_session = gx_sessions.get(session_id)
            if not gx_session:
                return
            if gx_session.last_message and gx_session.last_message.name == diameter_message.name:
                return
        diameter_message.set_framed_ip_address(gx_session.framed_ip_address)
        gx_sessions.add_message(session_id, diameter_message)
    elif app_id == APP_3GPP_RX:
        if diameter_message.name == AAR:
            gx_session = None
            if framed_ip_address:
                gx_session = gx_sessions.get_gx_session_by_framed_ip_address(framed_ip_address)
            if not gx_session:
                raise ValueError(f"No GxSession found with framed IP address {framed_ip_address}")
            rx_session = rx_sessions.create_rx_session(gx_session.subscriber, session_id)
            rx_session.set_gx_session_id(gx_session.session_id)
        elif diameter_message.name == AAA:
            rx_session = rx_sessions.get(session_id)
            gx_session = gx_sessions.get(rx_session.gx_session_id)
            rx_session.set_start_time(pkt_timestamp)
        #
        diameter_message.set_framed_ip_address(gx_session.framed_ip_address)
        rx_sessions.add_message(session_id, diameter_message)
    elif app_id == APP_3GPP_SY:
        if diameter_message.name == SLR:
            subscriber = subscribers.get_subscriber(msisdn)
            if not subscriber:
                logging.warning(f"Subscriber with MSISDN {msisdn} not found")
                return
            gx_session = gx_sessions.get_subscriber_active_session(msisdn)
            sy_session = sy_sessions.create_sy_session(subscriber, session_id)
            sy_session.set_gx_session_id(gx_session.session_id)
        elif diameter_message.name == SLA:
            sy_session = sy_sessions.get(session_id)
            if not sy_session:
                return
            sy_session.set_start_time(pkt_timestamp)
        else:
            sy_session = sy_sessions.get(session_id)
            if not sy_session:
                return
            gx_session = gx_sessions.get(sy_session.gx_session_id)
        diameter_message.set_framed_ip_address(gx_session.framed_ip_address)
        sy_sessions.add_message(session_id, diameter_message)

def run_pyshark(pcap_file: Pcap, session_manager: SessionManager):
    with pyshark.FileCapture(pcap_file.filepath, decode_as=pcap_file.decode_as, display_filter=pcap_file.filter, debug=False) as cap:
        for pkt in cap:
            process_pkt(pkt, session_manager)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the path to the pcap file as a command line argument.")
        sys.exit(1)

    pcap_path = sys.argv[1]
    if not os.path.exists(pcap_path):
        print("The specified pcap file does not exist.")
        sys.exit(1)

    BASE_FILTER = "diameter && !(diameter.cmd.code == 280) && !(diameter.cmd.code == 257)"
    DIAMETER_PORTS = [30101, 30001, 31501, 31601, 30003]
    session_manager = SessionManager()
    pcap = Pcap(pcap_path, DIAMETER_PORTS, BASE_FILTER)
    run_pyshark(pcap, session_manager)
    session_manager.parse_sessions()