from ..diameter import *
from .ip_queue import IpQueue, ip_to_bytes
from ..telecom.subscriber import Subscriber
from diameter.message.constants import *
from diameter.message.commands import *
from diameter.message.avp.grouped import *
import time
from .gx import GxService
from .sy import SyService

import logging
logger = logging.getLogger(__name__)

class DataService():
    gx_service: GxService
    sy_service: SyService
    ip_queue: IpQueue
    _realm: str
    _mcc_mnc: str
    _apn: str
    def __init__(self,
                 gx_service: GxService,
                 sy_service: SyService = None,
                 ip_start = "10.0.0.0",
                 ip_end = "10.0.0.100",
                 ):
        if not isinstance(gx_service, GxService):
            raise Exception("DataService: gx_service must be an instance of GxService")
        if sy_service and not isinstance(sy_service, SyService):
            raise Exception("DataService: sy_service must be an instance of SyService")
        self.gx_service = gx_service
        self.sy_service = sy_service
        self.ip_queue = IpQueue(ip_start, ip_end)
        self._realm = None
        self._mcc_mnc = None
        self._apn = None
        self.logger = logging.getLogger(__name__)

    @property
    def realm(self) -> str:
        if self._realm:
            return self._realm
        raise Exception(f"DataService: {self}. Realm is not set")
    
    @property
    def mcc_mnc(self) -> str:
        if self._mcc_mnc:
            return self._mcc_mnc
        raise Exception(f"DataService: {self}. MCC/MNC is not set")
    
    @property
    def apn(self) -> str:
        if self._apn:
            return self._apn
        raise Exception(f"DataService: {self}. APN is not set")
    
    def set_realm(self, realm: str):
        self._realm = realm

    def set_mcc_mnc(self, mcc_mnc: str):
        self._mcc_mnc = mcc_mnc

    def set_apn(self, apn: str):
        self._apn = apn

    def create_gx_session(self, subscriber: Subscriber) -> GxSession:
        gx_session_id = self.gx_service.gx_app.node.session_generator.next_id()
        framed_ip_address = self.ip_queue.get_ip()
        gx_session = self.gx_service.gx_app.sessions.create_session(subscriber, gx_session_id, framed_ip_address)
        return gx_session

    def start_gx_session(self, gx_session: GxSession):
        #
        ccr_i = self.gx_service.create_ccr_i(gx_session, self.mcc_mnc, self.apn)
        if self.realm:
            ccr_i.destination_realm = self.realm.encode()
        #
        ccr_i.bearer_usage = E_BEARER_USAGE_GENERAL
        cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
        if not isinstance(cca_i, CreditControlAnswer):
            raise Exception("CCA is not received")
        if cca_i.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            ts = time.time()
            gx_session.set_start_time(ts)

    def stop_gx_session(self, gx_session: GxSession):
        if not gx_session.active:
            return
        ccr_t = self.gx_service.create_ccr_t(gx_session)
        cca_t = self.gx_service.send_gx_request(gx_session, ccr_t, timeout=5)
        if not isinstance(cca_t, CreditControlAnswer):
            raise Exception("CCA is not received")
        if cca_t.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
            self.ip_queue.put_ip(gx_session.framed_ip_address)
            ts = time.time()
            gx_session.set_end_time(ts)
            gx_session.active = False

    def create_sy_session(self, subscriber: Subscriber) -> SySession:
        sy_session = self.sy_service.sy_app.get_subscriber_active_session(subscriber.msisdn)
        if not sy_session:
            return None
        self.logger.info(f"SY Session found for subscriber {subscriber}: {sy_session}")
        return sy_session

    def send_policy_counter_status_report(self, sy_session: SySession, policy_counter_dict, wait_raa=True):
        logger.info(f"Sending SSN Request: {policy_counter_dict}")
        ssnr = self.sy_service.create_ssnr(sy_session, policy_counter_dict)
        if self.realm:
            ssnr.destination_realm = self.realm.encode()
        ssna = self.sy_service.send_sy_request(sy_session, ssnr)
        #
        if wait_raa:
            pass


    # def wait_for_sy_session(self, subscriber_msisdn, timeout=3):
    #     return self.sy_service.wait_for_sy_session(subscriber_msisdn, timeout)
    
    # # def create_gx_session(self, subscriber: Subscriber):
    # #     return self.gx_service.create_gx_session(subscriber)

    # def start_gx_session(self, gx_session: GxSession):
    #     logger.info(f"Starting GX session: {gx_session}")
    #     ccr_i = self.create_ccr_i(gx_session)
    #     try:
    #         cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
    #     except:
    #         # First one failed. Try again
    #         logger.info("Sending CCR-I request again")
    #         cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
    #     sy_session = self.sy_service.wait_for_sy_session(gx_session.msisdn, timeout=5)
    #     if cca_i.result_code != E_RESULT_CODE_DIAMETER_SUCCESS:
    #         logger.info(f"CCA-I Result-Code is not 2001. RC: {cca_i.result_code}")
    #         return gx_session, sy_session
    #     # Get timestamp
    #     ts = time.time()
    #     gx_session.set_start_time(ts)
    #     # gx_session.active = True
    #     logger.info("GX session started")
    #     #
    #     return gx_session, sy_session
    
    # def start_data_session(self, gx_session: GxSession):
    #     logger.info(f"Starting GX session: {gx_session}")
    #     ccr_i = self.create_ccr_i(gx_session)
    #     try:
    #         cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
    #     except:
    #         # First one failed. Try again
    #         logger.info("Sending CCR-I request again")
    #         cca_i = self.gx_service.send_gx_request(gx_session, ccr_i, timeout=10)
    #     sy_session = self.sy_service.wait_for_sy_session(gx_session.msisdn, timeout=5)
    #     if cca_i.result_code != E_RESULT_CODE_DIAMETER_SUCCESS:
    #         logger.info(f"CCA-I Result-Code is not 2001. RC: {cca_i.result_code}")
    #         return gx_session, sy_session
    #     # Get timestamp
    #     ts = time.time()
    #     gx_session.set_start_time(ts)
    #     # gx_session.active = True
    #     logger.info("GX session started")
    #     #
    #     return gx_session, sy_session
    
    # def stop_gx_session(self, gx_session: GxSession):
    #     logger.info(f"Stopping GX session: {gx_session}")
    #     ccr_t = self.create_ccr_t(gx_session)
    #     cca_t = self.gx_service.send_gx_request(gx_session, ccr_t, timeout=5)
    #     if not isinstance(cca_t, CreditControlAnswer):
    #         raise Exception("CCA is not received")
    #     if cca_t.result_code == E_RESULT_CODE_DIAMETER_SUCCESS:
    #         self.gx_service.ip_queue.put_ip(gx_session.framed_ip_address)
    #         ts = time.time()
    #         gx_session.set_end_time(ts)
    #     logger.info("GX session stopped")
    #     return gx_session


    # def create_ccr_i(self, gx_session: GxSession) -> CreditControlRequest:
    #     # Define CCR-I in the upper carrier Data class
    #     pass

    # def create_ccr_t(self, gx_session: GxSession) -> CreditControlRequest:
    #     ccr = self.gx_service.create_ccr()
    #     ccr.session_id = gx_session.session_id
    #     ccr.cc_request_type = E_CC_REQUEST_TYPE_TERMINATION_REQUEST
    #     ccr.cc_request_number = gx_session.cc_request_number + 1
    #     #
    #     ccr.framed_ip_address = ip_to_bytes(gx_session.framed_ip_address)

    #     ccr.supported_features = SupportedFeatures()
    #     ccr.supported_features.vendor_id = VENDOR_TGPP
    #     ccr.supported_features.feature_list = 1032
    #     ccr.supported_features.feature_list_id = 1

    #     ccr.origin_state_id = 1448374171

    #     return ccr


    # def create_ccr_u(self, gx_session: GxSession) -> CreditControlRequest:
    #     # Define CCR-I in the upper carrier Data class
    #     pass
