#!/usr/bin/python3
from . import Options, video_download, config
from atexit import register
import signal
import shutil


def main():
    options = Options()

    # 用户发送的退出信号处理
    # kill pid
    signal.signal(signal.SIGINT, sig_handler)
    # ctrl - c
    signal.signal(signal.SIGTERM, sig_handler)

    video_download(options)


@register
def exit_handler():
    """程序退出时，清理资源
    """
    shutil.rmtree(config.temp_dir)
    pass


# noinspection PyUnusedLocal
def sig_handler(signum, frame):
    exit_handler()
    exit(0)


if __name__ == '__main__':
    main()
    pass
