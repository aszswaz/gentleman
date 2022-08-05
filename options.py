from argparse import ArgumentParser
from os import getcwd


class Options:
    urls: list[str]
    cookie: str
    output: str
    filename_reg: str

    def __init__(self):
        arg_parse = ArgumentParser(description="bilibili video vdownload")
        arg_parse.add_argument("urls", metavar="URL", type=str, nargs="+", help="video url.")
        arg_parse.add_argument("--cookie", type=str, required=True, help="account cookies.")
        arg_parse.add_argument("--filename-reg", type=str, help="Extract the filename from the video's title via a regular expression.")
        arg_parse.add_argument("--output", type=str, help="video save path, the default is working directory.")
        args = arg_parse.parse_args()

        self.urls = args.urls
        self.cookie = args.cookie
        self.filename_reg = args.filename_reg
        if args.output is None:
            self.output = getcwd()
        elif args.output.endswith("/"):
            self.output = args.output[0: len(self.output) - 1]
        else:
            self.output = args.output

    def __repr__(self):
        return self.__dict__.__repr__()

    pass
