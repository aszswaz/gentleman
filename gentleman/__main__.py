#!/usr/bin/python3
import os

from . import config
from . import command


def main():
    try:
        command.main()
    except Exception as e:
        print(''.join(e.args))
        exit(1)
        pass


def init():
    _mkdir(config.data_dir)
    pass


def _mkdir(directory: str):
    """
    确保程序具有对指定文件夹的写入权限，如果文件夹不存在则自动创建文件夹
    """
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise PermissionError(f"not a directory: {directory}")
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Permission denied: {directory}")
    else:
        os.makedirs(directory)
    pass


if __name__ == '__main__':
    main()
    pass
