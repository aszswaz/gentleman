import os
import tempfile

import requests

from ..DownloadException import DownloadException
from ..options import Options
from ..config import chrome_ua, temp_dir


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

    def _get_play_list(self):
        """
        获得视频的图片流和音频流下载地址
        """
        play_url = "https://api.bilibili.com/pugv/player/web/playurl?" \
                   f"avid={self.aid}&cid={self.cid}&qn=0&fnver=0&fnval=16&fourk=1&ep_id={self.id}"
        res = requests.get(url=play_url, headers=self.header).json()
        if res["code"] != 0:
            raise DownloadException(f"Failed to get video information, url: {play_url}, response: {res}")

        dash: dict = res["data"]["dash"]
        dash_video: list[dict] = dash["video"]
        audio: list[dict] = dash["audio"]

        # 为了以防万一，对 mime_type 进行检查
        if dash_video[0]["mime_type"] != "video/mp4" or audio[0]["mime_type"] != "audio/mp4":
            raise DownloadException(
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

        exit_code = os.system(
            "ffmpeg "
            "-loglevel quiet "
            "-y "
            "-f mp4"
            f"-i '{video_file}' "
            f"-i '{audio_file}' "
            f"'{self.output}'"
        )
        if exit_code != os.EX_OK:
            raise DownloadException("Video merging failed.")
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
                    raise DownloadException(f"file download failed. url: {url}")
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
