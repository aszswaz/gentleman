from .._gentleman_error import GentlemanError


class BiliBiliError(GentlemanError):
    def __init__(self, arg):
        self.args = arg
