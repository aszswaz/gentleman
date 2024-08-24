import tempfile
import os

from platformdirs import user_data_dir

# 基本请求头
base_header = {
    # 表明自己身份
    "user-agent": "gentleman"
}
chrome_ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36"
temp_dir = tempfile.mkdtemp(prefix="gentleman-")
data_dir = user_data_dir("gentleman", "aszswaz")
cookie_path = os.path.abspath(f"{data_dir}/cookie")
