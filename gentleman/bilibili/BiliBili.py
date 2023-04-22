import os
import requests
from tempfile import mktemp
import re

from urllib.parse import ParseResult

from ..DownloadError import DownloadError
from ..options import Options
from ..config import base_header, chrome_ua, temp_dir
from .BiliBiliVideo import BiliBiliVideo


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

    def __init__(self, url: ParseResult, options: Options):
        self.url = url
        self.cookie = options.cookie
        self.header = base_header.copy()
        self.output = options.output
        self.filename = options.filename

        path: str = url.path
        prefix = "/cheese/play/ep"
        if path.startswith(prefix):
            self.ep = path[len(prefix): len(path)]
        else:
            raise DownloadError(f"Unsupported video address: {url.geturl()}")
        pass

    def download(self):
        output = ""
        header = base_header.copy()
        videos: list[BiliBiliVideo] = self._get_video_list()

        header["cookie"] = self.cookie
        header["referer"] = "https://www.bilibili.com/"

        for item in videos:
            print(f"Downloading {item.title}...")
            if self.filename != "":
                output = self.filename.format(item.number)
            else:
                output = re.sub('[\\\\:/]', '-', item.title)
                output = f"{output}-{item.number:02d}"
            output = f"{self.output}/{output}.mp4"
            item.download(header, output)
        pass

    def _get_video_list(self) -> list[BiliBiliVideo]:
        """
        获取视频的编集列表中，所有视频的 ID 和标题
        """
        url = f"https://api.bilibili.com/pugv/view/web/season?ep_id={self.ep}"
        res = requests.get(url=url, headers=self.header).json()
        if res["code"] != 0:
            raise DownloadError(f"Failed to get video information, url: {url}, response: {res}")
        data = res["data"]

        videos: list[BiliBiliVideo] = []
        episodes: list = data['episodes']
        for i, item in enumerate(episodes):
            videos.append(BiliBiliVideo(
                number=i,
                id=item["id"],
                aid=item["aid"],
                cid=item["cid"],
                title=item["title"]
            ))
        return videos
