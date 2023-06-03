import os
import shutil

from appdirs import user_config_dir, user_cache_dir

application = "gentleman"
# 基本请求头
base_header = {
    # 表明自己身份
    "user-agent": "gentleman"
}
chrome_ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36"
cache_dir = user_cache_dir(application)
config_dir = user_config_dir(application)


def mkdirs():
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)


def rmdirs():
    shutil.rmtree(cache_dir)
