import os
import subprocess
import tempfile

import requests
import re

from urllib.parse import ParseResult

from ..DownloadError import DownloadError
from ..options import Options
from ..config import base_header
from ..config import temp_dir


class Video:
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
            id: int,
            title: str
    ) -> None:
        self.number = number
        self.aid = aid
        self.cid = cid
        self.id = id
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
        print("Downloading image stream...")
        video_file: str = self._file_download(self.video_url)
        print("Downloading audio stream...")
        audio_file: str = self._file_download(self.audio_url)
        print("Video and audio are being merged...")

        subprocess.run(
            [
                "ffmpeg",
                "-loglevel", "quiet",
                "-y",
                "-codec", "copy",
                "-f", "mp4",
                "-i", video_file,
                "-i", audio_file,
                self.output
            ],
            check=True
        )

        os.remove(video_file)
        os.remove(audio_file)
        pass

    def _file_download(self, url) -> str:
        """
        下载文件

        :param url: url 资源
        :return: 文件的临时保存目录，需要手动删除文件
        """
        temp_path: str = tempfile.mktemp(
            prefix="bilibili-",
            dir=temp_dir
        )

        try:
            with open(file=temp_path, mode="w+b") as file:
                res = requests.get(url, headers=self.header, stream=True)
                if res.status_code != 200:
                    raise DownloadError(f"file download failed. url: {url}")
                total_size = int(res.headers["content-length"])
                download_size = 0
                for cunk in res.iter_content(chunk_size=8192):
                    file.write(cunk)
                    download_size += len(cunk)
                    print(f"\r{download_size / total_size * 100:.2f}%", end="")
                print()
        except Exception as e:
            os.remove(temp_path)
            raise e
        return temp_path


class Classroom:
    """
    BiliBili 课堂的视频下载器
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

    def download(self):
        header = base_header.copy()
        videos: list[Video] = self._get_video_list()

        header["cookie"] = self.cookie
        header["referer"] = "https://www.bilibili.com/"

        for item in videos:
            print(f"Downloading {item.title}...")
            if self.filename is not None and self.filename != "":
                output = self.filename.format(item.number)
            else:
                output = re.sub('[\\\\:/]', '-', item.title)
                output = f"{output}-{item.number:02d}"
            output = f"{self.output}/{output}.mp4"
            item.download(header, output)
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
                id=item["id"],
                aid=item["aid"],
                cid=item["cid"],
                title=item["title"]
            ))
        return videos
