from .diameter import GxSession
import logging
logger = logging.getLogger(__name__)

class Assertions:
    def __init__(self, assertions: dict, raise_error: bool = True):
        if not isinstance(assertions, dict):
            raise ValueError("assertions must be a dictionary")
        self.values = assertions
        self.raise_error = raise_error
        self.failed = False

    def assert_gx_session(self, gx_session: GxSession, raise_error: bool = True):
        gx_session_assertions = self.values.get("gx_session")
        for key, value in gx_session_assertions.items():
            if hasattr(gx_session, key):
                logger.debug(f"Asserting {key} == {value}")
                if isinstance(value, list):
                    if isinstance(getattr(gx_session, key), list):
                        for item in value:
                            try:
                                assert item in getattr(gx_session, key)
                            except:
                                logger.error(f"Assertion failed for {key} == {item}")
                                self.failed = True
                elif isinstance(value, dict):
                    pass
                else:
                    try:
                        assert getattr(gx_session, key) == value
                    except:
                        logger.error(f"Assertion failed for {key} == {value}")
                        self.failed = True
        if self.raise_error and self.failed:
            raise AssertionError("GxSession attributes assertion failed")
