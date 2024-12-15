from urllib.parse import urlparse, ParseResult

from . import bilibili
from .DownloadError import DownloadError


def start(url: str):
    result: ParseResult = urlparse(url)
    if result.hostname == "www.bilibili.com":
        bilibili.download(result)
    else:
        raise DownloadError(f"Unsupported url: {url}")
    pass
