from .helpers import is_valid_msisdn, is_valid_imsi

class Subscriber:
    msisdn: str
    imsi: str
    """
    Represents a telecommunications subscriber with an MSISDN and an IMSI.
    """
    def __init__(self, msisdn: str, imsi: str):
        if not is_valid_msisdn(msisdn):
            raise ValueError("Invalid MSISDN")
        if not is_valid_imsi(imsi):
            raise ValueError("Invalid IMSI")
        
        self.msisdn = msisdn
        self.imsi = imsi