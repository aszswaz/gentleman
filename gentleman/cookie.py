import os
import time
from argparse import ArgumentParser, Namespace

from . import config

# 存储 cookie 的文件
_cookie_jar = config.config_dir + "/cookie.json"


class Cookie:
    date: int
    content: str


def cmd(parser: ArgumentParser):
    """
    注册 cookie 指令
    """
    sub_parser = parser.add_subparsers(title="instruction")
    set_cmd = sub_parser.add_parser("set", help="set cookie")
    show_cmd = sub_parser.add_parser("show", help="show cookie")

    set_cmd.add_argument("cookie", type=str, help="account cookie")
    set_cmd.set_defaults(func=_set_cookie)

    show_cmd.set_defaults(func=_show_cookie)


def get_cookie() -> Cookie | None:
    if not os.path.exists(_cookie_jar):
        return None

    with open(file=_cookie_jar, mode="rb") as jar:
        cookie = Cookie()
        buffer = jar.read()
        cookie.date = int.from_bytes(buffer[0:4], "big")
        str_bytes_len = int.from_bytes(buffer[4:8], "big")
        cookie.content = str(buffer[8:str_bytes_len], "utf-8")
        return cookie


def _set_cookie(opt: Namespace):
    """
    设置 cookie
    @param opt: cookie 的相关参数
    """
    with open(file=_cookie_jar, mode="wb") as jar:
        str_bytes = bytes(opt.cookie, "utf-8")
        str_bytes_len: int = len(str_bytes)
        jar.write(
            int(time.time()).to_bytes(4, "big") +
            str_bytes_len.to_bytes(4, "big") +
            str_bytes
        )


def _show_cookie(_: Namespace):
    cookie = get_cookie()
    print("update time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cookie.date)))
    print("cookie:", cookie.content)
