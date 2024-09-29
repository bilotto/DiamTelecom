
class DiameterStatistics:
    def __init__(self):
        self.request_count = dict()
        self.request_count['success'] = 0
        self.request_count['failure'] = 0
        self.rc_count = dict()

    def increment_request_count(self, success: bool):
        if success:
            self.request_count['success'] += 1
        else:
            self.request_count['failure'] += 1

    def increment_rc_count(self, rc):
        if rc not in self.rc_count:
            self.rc_count[rc] = 1
        else:
            self.rc_count[rc] += 1

    def __repr__(self):
        return f"Request count: {self.request_count}, Result code count: {self.rc_count}"
