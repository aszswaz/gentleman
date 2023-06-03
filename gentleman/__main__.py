#!/usr/bin/python3
import signal
from argparse import ArgumentParser
from atexit import register

from . import config, bilibili, cookie
from ._gentleman_error import GentlemanError


def main():
    try:
        # 用户发送的退出信号处理
        # kill pid
        signal.signal(signal.SIGINT, sig_handler)
        # ctrl - c
        signal.signal(signal.SIGTERM, sig_handler)

        config.mkdirs()

        main_parser = ArgumentParser(description="video downloader")
        sub_parser = main_parser.add_subparsers(title="instruction", required=True)

        cookie.cmd(sub_parser.add_parser("cookie", help="manage cookie"))
        bilibili.cmd(sub_parser.add_parser("download", help="download video file"))

        args = main_parser.parse_args()
        args.func(args)
    except GentlemanError as e:
        print(e.msg)


@register
def exit_handler():
    """程序退出时，清理资源
    """
    config.rmdirs()
    pass


def sig_handler(signum, _):
    exit_handler()
    exit(signum)


if __name__ == '__main__':
    main()
    pass
