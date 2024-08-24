from argparse import ArgumentParser
import os

from . import config


class Options:
    urls: list[str]
    cookie: str
    output: str
    filename: str

    def __init__(self):
        arg_parse = ArgumentParser(description="视频下载器。")
        arg_parse.add_argument("urls", metavar="URL", type=str, nargs="+", help="视频链接")
        arg_parse.add_argument(
            "--cookie", type=str, required=False,
            help=f"指定帐号的 cookie，并保存到 {config.cookie_path}"
        )
        arg_parse.add_argument(
            "--filename", type=str,
            help="文件的命名规则，目前仅支持指定视频的序号，比如 name-{:02d}.mp4，02d 表示使用两位数，不足两位数填充 0"
        )
        arg_parse.add_argument(
            "--output", type=str, default=os.getcwd(),
            help="保存视频的目录，默认是工作目录"
        )
        args = arg_parse.parse_args()

        self.urls = args.urls
        self.cookie = args.cookie
        self.filename = args.filename
        self.output = args.output.endswith("/") and args.output[0: len(self.output) - 1] or args.output

    def __repr__(self):
        return self.__dict__.__repr__()

    pass
