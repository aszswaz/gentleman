#!/usr/bin/python3
from atexit import register
import signal
import shutil

from urllib.parse import urlparse, ParseResult

from . import config, bilibili
from .options import Options


def main():
    options = Options()

    # 用户发送的退出信号处理
    # kill pid
    signal.signal(signal.SIGINT, sig_handler)
    # ctrl - c
    signal.signal(signal.SIGTERM, sig_handler)

    video_download(options)


def video_download(options: Options):
    """
    下载视频
    :param options:下载选项
    """
    for url in options.urls:
        url_info: ParseResult = urlparse(url)
        if url_info.hostname == "www.bilibili.com":
            bilibili.download(url_info, options)
        else:
            raise Exception("Unsupported url:", url)
    pass


@register
def exit_handler():
    """程序退出时，清理资源
    """
    shutil.rmtree(config.temp_dir)
    pass


def sig_handler(signum, _):
    exit_handler()
    exit(0)


if __name__ == '__main__':
    main()
    pass
