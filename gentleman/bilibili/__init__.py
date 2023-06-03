from urllib.parse import ParseResult

from .bili_bili import BiliBili
from ..options import Options


def download(url_info: ParseResult, opt: Options):
    bilibili = BiliBili(url_info, opt)
    bilibili.download()
