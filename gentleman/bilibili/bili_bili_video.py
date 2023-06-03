import os
import subprocess

import requests

from ._bilibili_error import BiliBiliError
from .. import http, config


class BiliBiliVideo:
    """
    BiliBili 视频信息
    """

    # HTTP 请求头
    header: dict
    # 文件输出路径
    output: str

    # 视频的序号，从 0 开始
    number: int
    aid: int
    cid: int
    id: int
    title: str
    # 视频图片流下载地址
    video_url: str
    # 视频的音频流下载地址
    audio_url: str

    def __init__(
            self,
            number: int,
            aid: int,
            cid: int,
            video_id: int,
            title: str
    ) -> None:
        self.number = number
        self.aid = aid
        self.cid = cid
        self.id = video_id
        self.title = title
        pass

    def download(self, header: dict, output: str):
        self.header = header
        self.output = output

        self._get_play_list()
        self._video_download()

    def _get_play_list(self):
        """
        获得视频的图片流和音频流下载地址
        """
        play_url = "https://api.bilibili.com/pugv/player/web/playurl?" \
                   f"avid={self.aid}&cid={self.cid}&qn=0&fnver=0&fnval=16&fourk=1&ep_id={self.id}"
        res = requests.get(url=play_url, headers=self.header, timeout=config.http_timeout).json()
        if res["code"] != 0:
            raise BiliBiliError(f"Failed to get video information, url: {play_url}, response: {res}")

        dash: dict = res["data"]["dash"]
        dash_video: list[dict] = dash["video"]
        audio: list[dict] = dash["audio"]

        # 为了以防万一，对 mime_type 进行检查
        if dash_video[0]["mime_type"] != "video/mp4" or audio[0]["mime_type"] != "audio/mp4":
            raise BiliBiliError(
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
        print("Downloading image stream...")
        video_file: str = http.file_download(self.video_url, self.header)
        print("Downloading audio stream...")
        audio_file: str = http.file_download(self.audio_url, self.header)
        print("Video and audio are being merged...")

        subprocess.run(
            [
                "ffmpeg",
                "-loglevel", "quiet",
                "-y",
                "-f", "mp4",
                "-i", video_file,
                "-i", audio_file,
                "-metadata", f"title={self.title}",
                self.output
            ],
            check=True
        )

        os.remove(video_file)
        os.remove(audio_file)
        pass
