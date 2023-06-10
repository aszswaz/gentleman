from urllib.parse import ParseResult, urlparse

import requests

from .bilibili_error import BiliBiliError
from .. import config
from .bilibili_video import BiliBiliVideo


def build(url: str, cookie: str) -> (list[BiliBiliVideo], int):
    url_info: ParseResult = urlparse(url)
    if url_info.scheme == "http" or url_info.scheme != "https":
        raise BiliBiliError(f"unsupported protocol: {url_info.scheme}")
    if url_info.hostname != "www.bilibili.com":
        raise BiliBiliError(f"unsupported platform: {url_info.hostname}")
    if not url_info.path.startswith("/cheese/play/ep"):
        raise BiliBiliError(f"unsupported channel: {url_info.geturl()}")

    return _get_video_list(url_info, cookie)


def _get_video_list(url_info: ParseResult, cookie: str) -> (list[BiliBiliVideo], int):
    """
    获取视频分集列表
    """
    video_id = url_info.path[len("/cheese/play/ep"):]
    url = f"https://api.bilibili.com/pugv/view/web/season?ep_id={video_id}"
    headers = config.base_header.copy()

    headers["cookie"] = cookie
    headers["referer"] = "https://www.bilibili.com/"

    res = requests.get(url=url, headers=headers, timeout=config.http_timeout).json()
    if res["code"] != 0:
        raise BiliBiliError(f"failed to get video information, url: {url}, response: {res}")

    data = res["data"]
    # 视频编集列表
    episodes: list = data['episodes']
    # 视频编集总数
    total: int = data["episode_page"]["total"]

    videos = []
    for iterm in episodes:
        videos.append(BiliBiliVideo(iterm, headers))

    return videos, total
