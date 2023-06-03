import os
import tempfile
import time

import requests

from . import config
from ._gentleman_error import GentlemanError


class HttpError(GentlemanError):
    def __init__(self, msg, url, res: requests.Response):
        headers = ""
        for key in res.headers:
            headers = headers + f"\n{key}: {res.headers[key]}"

        if res.status_code >= 400:
            self.msg = msg + f"\nstatus code: {res.status_code}\nurl: {url}" + f"\n{headers}\n\n{res.text}"
        else:
            self.msg = msg + f"\nstatus code: {res.status_code}\nurl: {url}" + f"\n{headers}"


class _DownloadTask:
    url: str
    headers: dict
    file: str
    total_size: int
    download_size: int

    def __init__(self, url, headers, file):
        self.url = url
        self.headers = headers
        self.file = file
        self.total_size = 0
        self.download_size = 0

    def start(self):
        with open(file=self.file, mode="ab") as file:
            file.seek(self.download_size)
            self.headers["Range"] = f"bytes={self.download_size}-"
            res = requests.get(self.url, headers=self.headers, stream=True, timeout=config.http_timeout)
            if res.status_code != 206:
                raise HttpError("resource download failed.", self.url, res)
            total_size = int(res.headers["content-length"])
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)
                self.download_size += len(chunk)
                print(f"\rdownloaded: {self.download_size / total_size * 100:.2f}%", end="")
            print()
            if self.download_size != self.total_size:
                raise HttpError("file truncation", self.url, res)


def file_download(url: str, headers: dict):
    """
    下载文件

    @param url: url 资源
    @param headers:
    @return: 文件的临时保存路径，需要手动删除文件
    """
    temp_path: str = tempfile.mktemp(prefix="bilibili-", dir=config.cache_dir)

    error = None
    task = _DownloadTask(url, headers, temp_path)
    for _ in range(10):
        try:
            task.start()
            return temp_path
        except Exception as e:
            error = e
            time.sleep(60 * 10)
    if os.path.exists(temp_path):
        os.remove(temp_path)
    raise error
