from .helpers import is_valid_msisdn, is_valid_imsi

class Subscriber:
    id: str
    msisdn: str
    imsi: str
    """
    Represents a telecommunications subscriber with an MSISDN and an IMSI.
    """
    def __init__(self, id: str, msisdn: str, imsi: str):
        id = str(id)
        msisdn = str(msisdn)
        imsi = str(imsi)
        if not is_valid_msisdn(msisdn):
            raise ValueError("Invalid MSISDN")
        if not is_valid_imsi(imsi):
            raise ValueError("Invalid IMSI")
        
        self.id = id
        self.msisdn = msisdn
        self.imsi = imsi