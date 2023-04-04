from argparse import ArgumentParser
import os


class Options:
    urls: list[str]
    cookie: str
    output: str
    filename: str

    def __init__(self):
        arg_parse = ArgumentParser(description="视频下载器。")
        arg_parse.add_argument("urls", metavar="URL", type=str, nargs="+", help="视频链接。")
        arg_parse.add_argument("--cookie", type=str, required=True, help=r"帐号的 cookie。")
        arg_parse.add_argument(
            "--filename", type=str,
            help="文件的命名规则，比如 name-%%i.mp4，%%i 是文件序号，下载器会自动根据不同平台的排序规则，生成不同的序号。"
        )
        arg_parse.add_argument(
            "--output", type=str, default=os.getcwd(),
            help=r"保存视频的目录，默认是工作目录。"
        )
        args = arg_parse.parse_args()

        self.urls = args.urls
        self.cookie = args.cookie
        self.filename = args.filename
        self.output = args.output.endswith("/") and args.output[0: len(self.output) - 1] or args.output

        # 确保程序具有对指定文件夹的写入权限，如果文件夹不存在则自动创建文件夹
        if os.path.exists(self.output):
            if not os.path.isdir(self.output):
                raise PermissionError(f"not a directory: {self.output}")
            if not os.access(self.output, os.W_OK):
                raise PermissionError(f"Permission denied: {self.output}")
        else:
            os.makedirs(self.output)

    def __repr__(self):
        return self.__dict__.__repr__()

    pass
