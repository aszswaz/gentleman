from urllib.parse import ParseResult

from ..DownloadError import DownloadError

from .Classroom import Classroom
from .TVSeries import TVSeries
from ...cookiejar import get_cookiejar


def download(url_info: ParseResult):
    path: str = url_info.path

    cookie = get_cookiejar(url_info.hostname)
    if cookie is None:
        raise DownloadError(f"no cookie found for {url_info.hostname}")

    if path.startswith("/cheese/play/ep"):
        # 下载 BiliBili 课堂的视频
        bilibili = Classroom(url_info, cookie)
    elif path.startswith("/bangumi/play/ep"):
        # 下载 BiliBili 番剧
        bilibili = TVSeries(url_info, cookie)
    else:
        raise DownloadError(f"Unsupported video address: {url_info.geturl()}")
    bilibili.download()
