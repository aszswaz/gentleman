from ..gentleman_error import GentlemanError


class BiliBiliError(GentlemanError):
    def __init__(self, msg):
        self.msg = msg
