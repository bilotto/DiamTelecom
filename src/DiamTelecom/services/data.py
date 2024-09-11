from ..diameter import *
from .ip_queue import IpQueue, ip_to_bytes
from ..telecom.subscriber import Subscriber
from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
import time
from .services import Service, GxService, SyService

import logging
logger = logging.getLogger(__name__)

class DataService(Service):
    def __init__(self, gx_config: dict, sy_config: dict, carrier_data: dict, gx_app: GxApplication, sy_app: SyApplication):
        super().__init__(gx_service=GxService(gx_app, gx_config), sy_service=SyService(sy_app, sy_config))
    
    def wait_for_sy_session(self, subscriber_msisdn, timeout=3):
        return self.sy_service.wait_for_sy_session(subscriber_msisdn, timeout)
    
    def create_gx_session(self, subscriber: Subscriber):
        return self.gx_service.create_gx_session(subscriber)

    def start_gx_session(self, gx_session: GxSession):
        logger.info(f"Starting GX session: {gx_session}")
        ccr_i = self.create_ccr_i(gx_session)
        try:
            cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
        except:
            # First one failed. Try again
            logger.info("Sending CCR-I request again")
            cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
        sy_session = self.sy_service.wait_for_sy_session(gx_session.msisdn, timeout=5)
        if cca_i.result_code != E_RESULT_CODE_DIAMETER_SUCCESS:
            logger.info(f"CCA-I Result-Code is not 2001. RC: {cca_i.result_code}")
            return gx_session, sy_session
        # Get timestamp
        ts = time.time()
        gx_session.set_start_time(ts)
        # gx_session.active = True
        logger.info("GX session started")
        #
        return gx_session, sy_session
    
    def stop_gx_session(self, gx_session: GxSession):
        logger.info(f"Stopping GX session: {gx_session}")
        ccr_t = self.create_ccr_t(gx_session)
        cca_t = self.gx_service.send_gx_request(gx_session, ccr_t, timeout=5)
        if not isinstance(cca_t, CreditControlAnswer):
            raise Exception("CCA is not received")
        if cca_t.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            self.gx_service.ip_queue.put_ip(gx_session.framed_ip_address)
            ts = time.time()
            gx_session.set_end_time(ts)
        logger.info("GX session stopped")
        return gx_session

    def send_policy_counter_status_report(self, gx_session: GxSession, sy_session: SySession, policy_counter_dict, wait_raa=True):
        logger.info(f"Sending SSN Request: {policy_counter_dict}")
        ssnr = self.sy_service.create_ssnr(sy_session, policy_counter_dict)
        ssna = self.sy_service.send_sy_request(sy_session, ssnr)
        if wait_raa:
            self.gx_service.wait_for_gx_raa(gx_session, len(gx_session.messages), timeout=5)

    def create_ccr_i(self, gx_session: GxSession) -> CreditControlRequest:
        # Define CCR-I in the upper carrier Data class
        pass

    def create_ccr_t(self, gx_session: GxSession) -> CreditControlRequest:
        ccr = self.gx_service.create_ccr()
        ccr.session_id = gx_session.session_id
        ccr.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST
        ccr.cc_request_number = gx_session.cc_request_number + 1
        #
        ccr.framed_ip_address = ip_to_bytes(gx_session.framed_ip_address)

        ccr.supported_features = SupportedFeatures()
        ccr.supported_features.vendor_id = VENDOR_TGPP
        ccr.supported_features.feature_list = 1032
        ccr.supported_features.feature_list_id = 1

        ccr.origin_state_id = 1448374171

        return ccr


    def create_ccr_u(self, gx_session: GxSession) -> CreditControlRequest:
        # Define CCR-I in the upper carrier Data class
        pass
