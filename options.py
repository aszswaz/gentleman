from argparse import ArgumentParser
import os


class Options:
    urls: list[str]
    cookie: str
    output: str
    filename_reg: str

    def __init__(self):
        arg_parse = ArgumentParser(description="bilibili video vdownload")
        arg_parse.add_argument("urls", metavar="URL", type=str, nargs="+", help="video url.")
        arg_parse.add_argument("--cookie", type=str, required=True, help="account cookies.")
        arg_parse.add_argument(
            "--filename-reg", type=str,
            help="Extract the filename from the video's title via a regular expression.")
        arg_parse.add_argument("--output", type=str, default=os.getcwd(),
                               help="video save path, the default is working directory.")
        args = arg_parse.parse_args()

        self.urls = args.urls
        self.cookie = args.cookie
        self.filename_reg = args.filename_reg
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
