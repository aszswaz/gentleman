import os

import click

from . import cookiejar as cookie_mgr
from . import download


@click.group(help="Video Downloader")
def main():
    pass


@main.group("cookiejar", help="manage cookies")
def cmd_cookiejar():
    pass


@cmd_cookiejar.command("set", help="set cookie")
@click.argument("domain")
@click.argument("cookie")
def cmd_cookiejar_set(domain, cookie):
    cookie_mgr.set_cookiejar(domain, cookie)


@cmd_cookiejar.command("get", help="get cookie")
@click.argument("domain", nargs=1)
def cmd_cookiejar_get(domain: str | None):
    print(cookie_mgr.get_cookiejar(domain))
    pass


@main.command("download", help="download video")
@click.argument("url", type=str, nargs=1)
@click.option(
    "-o", "--out-dir", type=str,
    help="Video save directory, the default is the working directory"
)
def cmd_download(url: str, out_dir: str | None):
    if out_dir is not None:
        os.chdir(out_dir)
    download.start(url)
    pass
