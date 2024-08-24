#!/usr/bin/python3
from atexit import register
import signal
import shutil
import os

from urllib.parse import urlparse, ParseResult

from .DownloadError import DownloadError
from . import config, bilibili
from .options import Options


def main():
    try:
        options = Options()
        init(options)

        # 用户发送的退出信号处理
        # kill pid
        signal.signal(signal.SIGINT, sig_handler)
        # ctrl - c
        signal.signal(signal.SIGTERM, sig_handler)

        video_download(options)
    except RuntimeError as e:
        print(''.join(e.args))
        pass


def init(opt: Options):
    _mkdir(opt.output)
    _mkdir(config.data_dir)

    os.chdir(opt.output)

    # 更新或读取 cookie
    if opt.cookie is None:
        if os.path.exists(config.cookie_path):
            fs = open(config.cookie_path, "r")
            opt.cookie = fs.read().strip()
            fs.close()
        else:
            raise DownloadError("please set cookies")
        pass
    else:
        print("update cookies to", config.cookie_path)
        fs = open(config.cookie_path, "w")
        fs.write(opt.cookie)
        fs.close()
    pass


def _mkdir(directory: str):
    """
    确保程序具有对指定文件夹的写入权限，如果文件夹不存在则自动创建文件夹
    """
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise PermissionError(f"not a directory: {directory}")
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Permission denied: {directory}")
    else:
        os.makedirs(directory)
    pass


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
            raise DownloadError(f"Unsupported url: {url}")
    pass


@register
def exit_handler():
    """程序退出时，清理资源
    """
    shutil.rmtree(config.temp_dir)
    pass


def sig_handler(signum, _):
    exit_handler()
    exit(signum)


if __name__ == '__main__':
    main()
    pass
