import os
import subprocess

import requests
import re

from urllib.parse import ParseResult

from gentleman.download.DownloadError import DownloadError
from gentleman.config import base_header


class Video:
    def __init__(
            self,
            number: int,
            aid: int,
            cid: int,
            vid: int,
            title: str
    ) -> None:
        self.header: dict = {}
        self.number = number
        self.aid = aid
        self.cid = cid
        self.id = vid
        self.title = title

    def download(self, header: dict):
        self.header = header

        self._get_play_list()
        self._video_download()

    def _get_play_list(self):
        """
        获得视频的图片流和音频流下载地址
        """
        play_url = "https://api.bilibili.com/pugv/player/web/playurl?" \
                   f"avid={self.aid}&cid={self.cid}&qn=0&fnver=0&fnval=16&fourk=1&ep_id={self.id}"
        res = requests.get(url=play_url, headers=self.header).json()
        if res["code"] != 0:
            raise DownloadError(f"Failed to get video information, url: {play_url}, response: {res}")

        dash: dict = res["data"]["dash"]
        dash_video: list[dict] = dash["video"]
        audio: list[dict] = dash["audio"]

        # 为了以防万一，对 mime_type 进行检查
        if dash_video[0]["mime_type"] != "video/mp4" or audio[0]["mime_type"] != "audio/mp4":
            raise DownloadError(
                "Video file format not supported. "
                f"video mime type: {dash_video[0]['mime_type']}, audio mime type: {audio[0]['mime_type']}"
            )
        # BiliBili 按照视频的清晰度进行降序，所以第一个视频文件就是账户所能得到的最高清晰度的视频
        self.video_url = dash_video[0]["base_url"]
        self.audio_url = audio[0]["base_url"]
        pass

    def _video_download(self):
        """
        下载视频的画面流和音频流
        """
        output = f"{re.sub('[\\\\:/]', '-', self.title)}.mp4"
        if os.path.exists(output):
            print("skip:", self.title)
            return

        headers = ""
        for k, v in self.header.items():
            headers = f"{headers}{k}: {v}\r\n"

        subprocess.run(
            args=[
                "ffmpeg",
                "-y",
                "-f", "mp4", "-headers", headers, "-i", self.video_url,
                "-f", "mp4", "-headers", headers, "-i", self.audio_url,
                "-codec", "copy",
                "-metadata", f"title={self.title}",
                "-f", "mp4", output
            ],
            check=True
        )
        pass


class Classroom:
    """
    BiliBili 课堂的视频下载器
    """

    def __init__(
            self,
            url: ParseResult,
            cookie: str
    ):
        self.url = url
        self.cookie = cookie
        self.header = base_header.copy()

        path = url.path
        self.ep = path[len("/cheese/play/ep"):len(path)]

    def download(self):
        header = base_header.copy()
        videos: list[Video] = self._get_video_list()

        header["cookie"] = self.cookie
        header["referer"] = "https://www.bilibili.com/"

        for item in videos:
            print(f"Downloading {item.title}...")
            item.download(header)
        pass

    def _get_video_list(self) -> list[Video]:
        """
        获取视频的编集列表中，所有视频的 ID 和标题
        """
        url = f"https://api.bilibili.com/pugv/view/web/season?ep_id={self.ep}"
        res = requests.get(url=url, headers=self.header).json()
        if res["code"] != 0:
            raise DownloadError(f"Failed to get video information, url: {url}, response: {res}")
        data = res["data"]

        videos: list[Video] = []
        episodes: list = data['episodes']
        for i, item in enumerate(episodes):
            videos.append(Video(
                number=i,
                vid=item["id"],
                aid=item["aid"],
                cid=item["cid"],
                title=item["title"]
            ))
        return videos
