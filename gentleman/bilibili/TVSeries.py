import json
import os.path
from urllib.parse import ParseResult, urlparse
import subprocess

import requests

from ..options import Options
from ..config import base_header
from ..DownloadError import DownloadError


def _join_header(header: dict) -> str:
    header_str = ""
    for key in header.keys():
        header_str = f"{header_str}{key}: {header[key]}\r\n"
        pass
    return header_str


class _Video:
    def __init__(self, data: dict, header: dict):
        self.link = data["link"]
        self.title = data["title"]
        self.full_title = data["share_copy"]
        self.header = header.copy()

        self.header["referer"] = self.link

    def download(self):
        """
        下载视频文件
        """
        self._get_video_information()
        self._download()

    def _get_video_information(self):
        response = requests.get(url=self.link, headers=self.header)
        if response.status_code != 200:
            raise DownloadError("unable to fetch video page")

        response = response.text.split("\n")
        for item in response:
            item = item.strip()
            if item.startswith("const playurlSSRData"):
                data = item
                break
            pass
        else:
            raise DownloadError("failed to obtain video information")

        data = json.loads(data[len("const playurlSSRData = "): len(data)])
        dash = data["result"]["video_info"]["dash"]
        self.video = dash["video"][0]["baseUrl"]
        self.audio = dash["audio"][0]["baseUrl"]
        pass

    def _download(self):
        video_header = self.header.copy()
        audio_header = self.header.copy()

        url = urlparse(self.video)
        video_header["authority"] = f"{url.hostname}:{url.port}"
        url = urlparse(self.audio)
        audio_header["authority"] = f"{url.hostname}:{url.port}"

        out_file = f"{self.title}.mp4"

        if os.path.exists(out_file):
            return

        video_header_str = _join_header(video_header)
        audio_header_str = _join_header(audio_header)

        subprocess.run(args=[
            "ffmpeg",
            "-f", "mp4", "-headers", video_header_str, "-i", self.video,
            "-f", "mp4", "-headers", audio_header_str, "-i", self.audio,
            "-codec", "copy", "-f", "mp4",
            "-metadata", f"title={self.full_title}",
            out_file
        ], check=True)
        pass


class TVSeries:
    """
    BiliBili 番剧下载器
    """

    def __init__(self, url_info: ParseResult, opt: Options):
        self.url = url_info
        self.header = base_header.copy()
        self.cookie = opt.cookie
        self.output = opt.output
        self.filename = opt.filename

        self.header["cookie"] = opt.cookie

        # 解析 ep id
        path = self.url.path
        self.ep_id = path[len("/bangumi/play/ep"): len(path)]
        pass

    def download(self):
        video_list = self._get_video_list()
        for item in video_list:
            item.download()
        pass

    def _get_video_list(self) -> list[_Video]:
        """
        获取视频分集列表
        """
        result = requests.get(
            url=f"https://api.bilibili.com/pgc/view/web/ep/list?ep_id={self.ep_id}",
            headers=self.header
        )
        if result.status_code != 200:
            raise DownloadError("unable to get video list")
        body = result.json()
        if body["code"] != 0:
            raise DownloadError(f"unable to obtain the video list, the server returns the message: {body["message"]}")

        episodes = body["result"]["episodes"]
        # 删除视频集中的预告视频，并且转换为 _Video 对象
        return [_Video(item, self.header) for item in episodes if item["badge_type"] != 1]
