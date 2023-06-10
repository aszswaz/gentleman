import os.path
from argparse import Namespace
import json
import time
import math
import atexit

from . import config, bilibili
from .gentleman_error import GentlemanError
from .bilibili.bilibili_video import BiliBiliVideo

_config_path = config.config_dir + "/task.json"


class Task:
    """
    视频下载任务
    """
    # 任务名称
    name: str
    # 视频地址
    url: str
    # 视频保存目录
    save_directory: str
    # 帐号 cookie
    cookie: str
    # 视频总数
    total: int
    # 已下载的视频数量
    downloaded: int
    # 是否下载成功
    success: bool
    # 更新时间
    update_time: int

    def __init__(self, args: dict):
        self.name = args["name"]
        self.url = args["url"]
        self.save_directory = args["save_directory"]
        self.cookie = args["cookie"]
        self.total = args["total"]
        self.downloaded = args["downloaded"]
        self.success = args["success"]
        self.update_time = args["update_time"]

    def start(self):
        """
        下载视频
        """
        videos: list[BiliBiliVideo]
        videos, total = bilibili.build(self.url, self.cookie)
        self.total = total
        digits = int(math.log10(total))

        videos = videos[self.downloaded + 1:]
        for index, iterm in enumerate(videos, self.downloaded + 1):
            print(f"total \033[91m{total}\033[0m, downloading \033[91m{index}\033[0m episodes")
            file = f"{self.save_directory}/{str(index).zfill(digits)}.mp4"
            iterm.download(file)
            self.downloaded = index
        pass


def create(args: Namespace):
    """
    创建视频下载任务
    @param args: CLI 参数
    """
    tasks = []

    if os.path.exists(_config_path):
        tasks = _read_config()

    for iterm in tasks:
        if iterm["url"] == args.url:
            raise GentlemanError("task already exists")

    tasks.append({
        "name": args.name,
        "url": args.url,
        "save_directory": args.save_directory,
        "cookie": args.cookie,
        "total": 0,
        "downloaded": args.offset <= 0 and 0 or args.offset - 1,
        "success": False,
        "update_time": int(time.time())
    })
    _save_config(tasks)
    pass


def show(_: Namespace):
    """
    展示任务列表
    """
    tasks = _read_config()

    titles = ["index", "name".center(17), "url".center(35), "save directory".center(17),
              "total".center(10), "downloaded".center(10),
              "success", "update time".center(19)]
    title = "| " + " | ".join(titles) + " |"
    print(title)
    print("-" * len(title))

    for idx, iterm in enumerate(tasks):
        name = iterm["name"]
        url = iterm["url"]
        save_directory = iterm["save_directory"]
        total = str(iterm["total"])
        downloaded = str(iterm["downloaded"])
        success = iterm["success"] and "true" or "false"
        update_time = iterm["update_time"]

        idx = str(idx).center(5)
        name = (len(name) < 17 and name or name[:14] + "...").center(17)
        url = (len(url) < 35 and url or url[:32] + "...").center(35)
        save_directory = (len(save_directory) < 17 and save_directory or save_directory[:14] + "...").center(17)
        total = total.center(10)
        downloaded = downloaded.center(10)
        success = success.center(7)
        update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(update_time))
        data = [idx, name, url, save_directory, total, downloaded, success, update_time]
        print("| " + " | ".join(data) + " |")
    pass


def start(args: Namespace):
    """
    执行视频下载任务
    """
    task_index = args.task_index
    tasks = _read_config()

    if task_index < 0 or task_index >= len(tasks):
        raise GentlemanError("task does not exist")

    task = tasks[args.task_index]
    task = Task(task)

    atexit.register(_exit, args.task_index, task)

    task.start()
    pass


def _read_config():
    """
    读取任务信息
    """
    f = open(_config_path, "rt")
    json_str = f.read()
    f.close()
    return json.loads(json_str)


def _save_config(tasks: list):
    """
    保存任务信息
    """
    f = open(_config_path, "wt")
    f.write(json.dumps(tasks, separators=(",", ":"), ensure_ascii=False))
    f.close()


def _exit(index: int, task: Task):
    """
    程序退出时保存任务信息
    """
    task.update_time = int(time.time())
    tasks = _read_config()
    tasks[index] = task.__dict__
    _save_config(tasks)
