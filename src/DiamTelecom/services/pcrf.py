from .data import DataService


class PCRFService(DataService):
    def __init__(self, gx_service, sy_service):
        super().__init__(gx_service, sy_service)
        self.gx_

