
import binascii
import xml.etree.ElementTree as ET
from xml.dom import minidom

from diameter.message import Avp, AvpGrouped, Message
from diameter.message.constants import *

def _create_avp_element(avp: Avp) -> ET.Element:
    """
    Create an XML element for an AVP.
    """
    avp_element = ET.Element("avp", name=avp.name, mandatory=str(avp.is_mandatory).lower())

    # If the AVP has a dynamic tag, include it as an attribute
    if hasattr(avp, 'dynamictag') and avp.dynamictag:
        avp_element.set("dynamictag", avp.dynamictag)

    # If it's an AVPGrouped, recursively process the contained AVPs
    if isinstance(avp, AvpGrouped):
        grouped_avp_element = ET.Element("groupedavp", name=avp.name, mandatory=str(avp.is_mandatory).lower())
        for child_avp in avp.value:
            child_element = _create_avp_element(child_avp)
            grouped_avp_element.append(child_element)
        return grouped_avp_element
    else:
        # Set the AVP value as the text content, handling binary strings correctly
        avp_value = avp.value
        if isinstance(avp_value, bytes):
            try:
                # Try to decode the value as UTF-8
                avp_value = avp_value.decode('utf-8')
            except UnicodeDecodeError:
                # If it can't be decoded, represent it as a hexadecimal string
                avp_value = binascii.hexlify(avp_value).decode('utf-8')
        
        avp_element.text = str(avp_value)
    
    return avp_element

def prettify_xml(xml_string: str) -> str:
    """Prettify the XML string with indentation."""
    parsed = minidom.parseString(xml_string)
    return parsed.toprettyxml(indent="    ")  # Using 4 spaces for indentation

def generate_xml(msg: Message, file_path: str = None) -> str:
    application_id = msg.header.application_id
    if application_id == APP_3GPP_GX:
        application_name = "Gx"
    elif application_id == APP_3GPP_SY:
        application_name = "Sy"
    elif application_id == APP_3GPP_RX:
        application_name = "Rx"
    else:
        application_name = "Unknown"
    
    # Create the root element (application)
    root = ET.Element("application", name=application_name, id=str(application_id))
    
    # Create the message element with corrected boolean attributes
    msg_element = ET.SubElement(root, "message", {
        "code": str(msg.header.command_code),
        "request": str(bool(msg.header.is_request)).lower(),
        "proxiable": str(bool(msg.header.command_flag_proxiable_bit)).lower(),
        "error": str(bool(msg.header.command_flag_error_bit)).lower(),
        "retransmit": str(bool(msg.header.command_flag_retransmit_bit)).lower(),
        "hopbyhop": "AUTO",  # Assuming we want to keep AUTO as the hop-by-hop identifier
        "endtoend": "AUTO"   # Assuming AUTO for end-to-end identifier as well
    })

    # Add AVPs to the message element
    for avp in msg.avps:
        avp_element = _create_avp_element(avp)
        msg_element.append(avp_element)

    # Convert the tree to a string and prettify the output
    xml_string = ET.tostring(root, encoding='unicode', method='xml')
    pretty_xml = prettify_xml(xml_string)

    # If a file path is provided, save the prettified XML to the file
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

    return pretty_xml
