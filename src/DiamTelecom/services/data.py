from ..diameter import *
from .ip_queue import IpQueue, ip_to_bytes
from ..telecom.subscriber import Subscriber
from diameter.message.constants import *
from diameter.message.commands import *
from .gx import GxService
from .sy import SyService
from diameter.message.avp.grouped import *
import time
from typing import List, Tuple
import logging
logger = logging.getLogger(__name__)

class DataService():
    gx_service: GxService
    sy_service: SyService
    
    def __init__(self,
                 gx_service: GxService,
                 sy_service: SyService = None,
                 ):
        if not isinstance(gx_service, GxService):
            raise Exception("DataService: gx_service must be an instance of GxService")
        if sy_service and not isinstance(sy_service, SyService):
            raise Exception("DataService: sy_service must be an instance of SyService")
        self.gx_service = gx_service
        self.sy_service = sy_service
        self.logger = logging.getLogger("DiamTelecom.services")

    @property
    def gx_sessions(self):
        return self.gx_service.sessions
    
    @property
    def sy_sessions(self):
        if self.sy_service:
            return self.sy_service.sessions
        return []
    
    @property
    def gx(self):
        return self.gx_service
    
    @property
    def sy(self):
        return self.sy_service

    def start_gx_session(self, gx_session: GxSession) -> GxSession:
        ccr_i = self.gx_service.create_ccr_i(gx_session)
        # Add specific data flow AVPs
        ccr_i.bearer_usage = E_BEARER_USAGE_GENERAL
        cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
        if not isinstance(cca_i, CreditControlAnswer):
            raise Exception("CCA is not received")
        if cca_i.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            gx_session.start()
        return gx_session

    def send_policy_counter_status_report(self, sy_session: SySession, policy_counter_dict, wait_raa=True):
        self.logger.info(f"Sending SSN Request: {policy_counter_dict}")
        gx_session = self.gx_service.gx_app.sessions.get_session(sy_session.gx_session_id)
        ssnr = self.sy_service.create_ssnr(sy_session, policy_counter_dict)
        ssna = self.sy_service.send_sy_request(sy_session, ssnr)
        if wait_raa:
            self.logger.info(f"Waiting for RAA for {gx_session}")
            self.gx_service.wait_for_gx_raa(gx_session, timeout=5)
        if not isinstance(ssna, SpendingStatusNotificationAnswer):
            raise Exception("SSNA is not received")
        if ssna.result_code != E_RESULT_CODE_DIAMETER_SUCCESS:
            self.logger.error(f"SSNA Result-Code is not 2001. RC: {ssna.result_code}")
        #

    def start_data_session(self, subscriber: Subscriber) -> Tuple[GxSession, SySession]:
        gx_session = None
        sy_session = None
        gx_session = self.gx_service.create_gx_session(subscriber)
        self.start_gx_session(gx_session)
        if self.sy_service:
            sy_session = self.sy_service.wait_for_sy_session(subscriber.msisdn, timeout=5)
            if sy_session:
                sy_session.gx_session_id = gx_session.session_id
        return gx_session, sy_session
    
    def update_gx_session(self, gx_session: GxSession):
        ccr_u = self.gx_service.create_ccr_u(gx_session)
        ccr_u.event_trigger.append(E_EVENT_TRIGGER_RAT_CHANGE)
        # ccr_u.event_trigger.append(E_EVENT_TRIGGER_USER_LOCATION_CHANGE)
        # ccr_u.user_location_info = b"Tset"
        ccr_u.origin_state_id = 19
        ccr_u.rat_type = E_RAT_TYPE_UTRAN
        cca_u = self.gx_service.send_gx_request(gx_session, ccr_u, timeout=5)
        if not isinstance(cca_u, CreditControlAnswer):
            raise Exception("CCA is not received")
        return gx_session
