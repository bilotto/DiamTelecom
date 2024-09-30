
class DiameterStatistics:
    def __init__(self):
        self.transaction_count = dict()
        self.transaction_count['success'] = 0
        self.transaction_count['failure'] = 0
        self.rc_count = dict()
        self.cmd_code_count = dict()

    def increment_based_on_answer(self, answer):
        if answer:
            self.increment_transaction_count(True)
        result_code = answer.result_code
        cmd_code = int(answer.header.command_code)
        # self.increment_rc_count(rc)
        self.increment_cmd_code_count(cmd_code, result_code)

    def increment_transaction_count(self, success: bool):
        if success:
            self.transaction_count['success'] += 1
        else:
            self.transaction_count['failure'] += 1

    # def increment_rc_count(self, rc):
    #     if rc not in self.rc_count:
    #         self.rc_count[rc] = 1
    #     else:
    #         self.rc_count[rc] += 1

    def increment_cmd_code_count(self, cmd_code, result_code):
        if cmd_code not in self.cmd_code_count:
            self.cmd_code_count[cmd_code] = {}
        if result_code not in self.cmd_code_count[cmd_code]:
            self.cmd_code_count[cmd_code][result_code] = 1
        else:
            self.cmd_code_count[cmd_code][result_code] += 1


    def __repr__(self):
        return f"transaction_count: {self.transaction_count}, cmd_code_count: {self.cmd_code_count}"
