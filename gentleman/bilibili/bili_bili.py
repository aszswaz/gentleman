from argparse import Namespace
from urllib.parse import ParseResult

import requests

from ._bilibili_error import BiliBiliError
from .bili_bili_video import BiliBiliVideo
from .. import config


class BiliBili:
    """
    BiliBili 视频下载器
    """

    url: ParseResult
    cookie: str
    # 教学视频的课程 ID
    ep: str
    # 视频的输出文件夹
    output: str
    # 用于提取文件名称的正则表达式
    filename: str

    def __init__(self, url: ParseResult, cookie: str, opt: Namespace):
        self.url = url
        self.cookie = cookie
        self.header = config.base_header.copy()
        self.output = opt.output

        prefix = "/cheese/play/ep"
        self.ep = url.path[len(prefix): len(url.path)]

    def download(self):
        header = config.base_header.copy()
        videos: list[BiliBiliVideo] = self._get_video_list()

        header["cookie"] = self.cookie
        header["referer"] = "https://www.bilibili.com/"

        for item in videos:
            print(f"Downloading {item.title}...")
            output = str(item.number).zfill(len(str(len(videos))))
            output = f"{self.output}/{output}.mp4"
            item.download(header, output)
        pass

    def _get_video_list(self) -> list[BiliBiliVideo]:
        """
        获取视频的编集列表中，所有视频的 ID 和标题
        """
        url = f"https://api.bilibili.com/pugv/view/web/season?ep_id={self.ep}"
        res = requests.get(url=url, headers=self.header, timeout=config.http_timeout).json()
        if res["code"] != 0:
            raise BiliBiliError(f"Failed to get video information, url: {url}, response: {res}")
        data = res["data"]

        videos: list[BiliBiliVideo] = []
        episodes: list = data['episodes']
        for i, item in enumerate(episodes):
            videos.append(BiliBiliVideo(
                number=i,
                video_id=item["id"],
                aid=item["aid"],
                cid=item["cid"],
                title=item["title"]
            ))
        return videos
