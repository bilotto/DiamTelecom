import re
import datetime
import yaml

def is_valid_msisdn(msisdn: str) -> bool:
    # Add your MSISDN validation logic here
    # For example, you can use a regular expression
    pattern = r"^\d{10,15}$"  # Assuming MSISDN is a 10 to 15-digit number
    return re.match(pattern, msisdn) is not None

def is_valid_imsi(imsi: str) -> bool:
    # Add your IMSI validation logic here
    # For example, you can use a regular expression
    pattern = r"^\d{15}$"  # Assuming IMSI is a 15-digit number
    return re.match(pattern, imsi) is not None


def convert_timestamp(timestamp: float) -> str:
    # Convert timestamp to datetime
    return datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
# self.time = datetime.datetime.fromtimestamp(float(self.timestamp)).strftime('%Y-%m-%d %H:%M:%S')

def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def decode_hex_string(hex_string: str) -> str:
    # Remover os ':' para que possamos converter de hex para bytes
    hex_string = hex_string.replace(':', '')
    # Convertendo a string hexadecimal em bytes
    byte_data = bytes.fromhex(hex_string)
    # Decodificando os bytes para obter a string ASCII
    return byte_data.decode('ascii')
