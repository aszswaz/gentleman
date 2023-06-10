class GentlemanError(RuntimeError):
    msg: str

    def __init__(self, msg):
        self.msg = msg
