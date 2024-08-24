from urllib.parse import ParseResult

from ..options import Options
from ..DownloadError import DownloadError

from .Classroom import Classroom
from .TVSeries import TVSeries


def download(url_info: ParseResult, opt: Options):
    path: str = url_info.path
    if path.startswith("/cheese/play/ep"):
        # 下载 BiliBili 课堂的视频
        bilibili = Classroom(url_info, opt)
    elif path.startswith("/bangumi/play/ep"):
        # 下载 BiliBili 番剧
        bilibili = TVSeries(url_info, opt)
    else:
        raise DownloadError(f"Unsupported video address: {url_info.geturl()}")
    bilibili.download()
