import json
import os

from .config import cookie_path

cookies: dict | None = None


def set_cookiejar(domain, cookie):
    domain = _primary_domain(domain)
    cookie_dict = _load_file()
    cookie_dict[domain] = cookie
    _save(cookie_dict)
    pass


def get_cookiejar(domain) -> str | None:
    domain = _primary_domain(domain)
    d = _load_file()
    if domain in d.keys():
        return d[domain]
    else:
        return None


def _load_file() -> dict:
    global cookies
    if cookies is not None:
        return cookies

    if os.path.exists(cookie_path):
        fs = open(cookie_path, "r")
        content = fs.read()
        fs.close()
        cookies = json.loads(content)
        return cookies
    else:
        cookies = {}
        return cookies


def _primary_domain(domain: str):
    items = domain.split(".")
    if len(items) < 2:
        raise Exception("不合法的域名")
    items = items[len(items) - 2:]
    return items[0] + "." + items[1]


def _save(d: dict):
    content = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    fs = open(cookie_path, "w")
    fs.write(content)
    fs.close()
