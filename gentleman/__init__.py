from urllib.parse import urlparse, ParseResult
from .options import Options
from .BiliBili import BiliBili


def video_download(options: Options):
    """
    下载视频
    :param options:下载选项
    """
    for url in options.urls:
        url_info: ParseResult = urlparse(url)
        if url_info.hostname == "www.bilibili.com":
            bilibili = BiliBili(url_info, options)
            bilibili.download()
        else:
            raise Exception("Unsupported url:", url)
    pass
