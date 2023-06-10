import os

from appdirs import user_config_dir, user_cache_dir

application = "gentleman"
# 基本请求头
base_header = {
    # 表明自己身份
    "user-agent": "gentleman"
}
cache_dir = user_cache_dir(application)
config_dir = user_config_dir(application)
http_timeout = 60

if not os.path.isdir(config_dir):
    os.makedirs(config_dir)
if not os.path.isdir(cache_dir):
    os.makedirs(cache_dir)
