import os.path

from gentleman.options import Options
from urllib.parse import ParseResult
from .DownloadException import DownloadException
import requests
from .config import base_header, chrome_ua, temp_dir
from tempfile import mktemp
import re


class BiliBiliVideo:
    """
    BiliBili 视频信息
    """

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
    pass


class BiliBili:
    """
    BiliBili 视频下载器
    """

    url: ParseResult
    # 教学视频的课程 ID
    ep: str
    # 请求头
    header: dict
    # 视频的输出文件夹
    output: str
    # 用于提取文件名称的正则表达式
    filename_reg: re.Pattern

    def __init__(self, url: ParseResult, options: Options):
        self.url = url
        self.cookie = options.cookie
        self.header = base_header.copy()
        self.output = options.output
        self.filename_reg = options.filename_reg and re.compile(options.filename_reg) or None

        self.header["cookie"] = options.cookie
        self.header["referer"] = "https://www.bilibili.com/"
        path: str = url.path
        prefix = "/cheese/play/ep"
        if path.startswith(prefix):
            self.ep = path[len(prefix): len(path)]
        else:
            raise DownloadException(f"Unsupported video address: {url.geturl()}")
        pass

    def download(self):
        videos: list[BiliBiliVideo] = self._get_video_list()
        for item in videos:
            print(f"Downloading {item.title}...")
            self._get_play_list(item)
            self._video_download(item)
        pass

    def _get_video_list(self) -> list[BiliBiliVideo]:
        """
        获取视频的编集列表中，所有视频的 ID 和标题
        """
        url = f"https://api.bilibili.com/pugv/view/web/season?ep_id={self.ep}"
        res = requests.get(url=url, headers=self.header).json()
        if res["code"] != 0:
            raise DownloadException(f"Failed to get video information, url: {url}, response: {res}")
        data = res["data"]

        videos: list[BiliBiliVideo] = []
        episodes: list = data['episodes']
        for i, item in enumerate(episodes):
            video = BiliBiliVideo()
            video.number = i
            video.id = item["id"]
            video.aid = item["aid"]
            video.cid = item["cid"]
            video.title = item["title"]
            videos.append(video)
            pass
        return videos

    def _get_play_list(self, video: BiliBiliVideo):
        """
        获得视频的图片流和音频流下载地址
        """
        play_url = "https://api.bilibili.com/pugv/player/web/playurl?" \
                   f"avid={video.aid}&cid={video.cid}&qn=0&fnver=0&fnval=16&fourk=1&ep_id={video.id}"
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
            pass
        # BiliBili 按照视频的清晰度进行降序，所以第一个视频文件就是账户所能得到的最高清晰度的视频
        video.video_url = dash_video[0]["base_url"]
        video.audio_url = audio[0]["base_url"]
        pass

    def _video_download(self, video: BiliBiliVideo):
        """
        下载视频的画面流和音频流
        """
        print("Downloading image stream...")
        video_file: str = self._file_download(video.video_url)
        print("Downloading audio stream...")
        audio_file: str = self._file_download(video.audio_url)
        print("Video and audio are being merged...")

        # 使用 ffmpeg 合并图片流和音频流
        # 去除文件路径不允许的字符
        filename = re.sub('[\\\\:/]', '-', video.title)
        if self.filename_reg:
            result = self.filename_reg.search(video.title)
            if result: filename = result.group(0)
        filename = f"{video.number:02d}-{filename}"
        output = f"{self.output}/{filename}.mp4"

        exit_code = os.system(f"ffmpeg -loglevel quiet -y -i '{video_file}' -i '{audio_file}' -codec copy '{output}'")
        if exit_code != os.EX_OK:
            raise DownloadException("Video merging failed.")
        pass

    def _file_download(self, url) -> str:
        """
        下载文件

        :param url: url 资源
        :return: 文件的临时保存目录，需要手动删除文件
        """
        temp_path: str = mktemp(prefix="bilibili-", dir=temp_dir)
        header = self.header.copy()
        header["user-agent"] = chrome_ua

        try:
            with open(file=temp_path, mode="w+b") as file:
                res = requests.get(url, headers=header, stream=True)
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
