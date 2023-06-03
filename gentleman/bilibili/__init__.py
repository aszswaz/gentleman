from argparse import ArgumentParser, Namespace
import os
import time

from urllib.parse import ParseResult, urlparse

from .bili_bili import BiliBili
from ._bilibili_error import BiliBiliError
from ..cookie import get_cookie


def cmd(parser: ArgumentParser):
    """
    注册 download 指令
    """
    parser.add_argument("url", metavar="URL", type=str, help="bilibili video address")
    parser.add_argument(
        "--filename", type=str,
        help="the naming method of the file, %%i specifies the location of the file serial number, the length of the "
             "file serial number is determined according to the number of videos to be downloaded, and the minimum is "
             "a two-digit integer"
    )
    parser.add_argument(
        "--output", type=str, default=os.getcwd(),
        help="the directory to save the video, the default is the working directory"
    )
    parser.set_defaults(func=_start)


def _start(opt: Namespace):
    """
    下载 bilibili 课堂的视频
    @param opt: 视频下载参数
    """
    if os.path.exists(opt.output):
        if not os.path.isdir(opt.output):
            raise BiliBiliError(f"{opt.output} is not a directory")
        if not os.access(opt.output, os.W_OK):
            raise PermissionError(f"cannot access {opt.output}: Permission denied")
    else:
        os.makedirs(opt.output)

    url_info: ParseResult = urlparse(opt.url)
    if url_info.scheme == "http" or url_info.scheme != "https":
        raise BiliBiliError(f"unsupported protocol: {url_info.scheme}")
    if url_info.hostname != "www.bilibili.com":
        raise BiliBiliError(f"unsupported platform: {url_info.hostname}")
    if not url_info.geturl().endswith("/cheese/play/ep"):
        raise BiliBiliError(f"unsupported channel: {url_info.geturl()}")

    if opt.cookie is not None:
        cookie = opt.cookie
    else:
        jar = get_cookie()
        if jar is not None:
            cookie = jar.content
            if int(time.time()) - jar.date > 30 * 24 * 60 * 60:
                raise BiliBiliError("the cookie of the bilibili account is invalid, please update the cookie")
        else:
            raise BiliBiliError("please set the cookie of bilibili account")

    bilibili = BiliBili(url_info, cookie, opt)
    bilibili.download()
