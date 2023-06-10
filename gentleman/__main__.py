#!/usr/bin/python3
import signal
from argparse import ArgumentParser
import atexit
import os

from . import config, task
from .gentleman_error import GentlemanError


def main():
    try:
        main_parser = ArgumentParser(description="video downloader")
        sub_parser = main_parser.add_subparsers(title="instruction", required=True)

        # 设置子命令
        create_cmd: ArgumentParser = sub_parser.add_parser("create", help="create video download tasks")
        start_cmd: ArgumentParser = sub_parser.add_parser("start", help="execute the specified video download task")
        show_cmd: ArgumentParser = sub_parser.add_parser("show", help="print a list of tasks")

        create_cmd.add_argument(
            "--name", type=str, required=True, help="the task name, usually the name of the video collection"
        )
        create_cmd.add_argument("--url", type=str, required=True, help="video url")
        create_cmd.add_argument(
            "--save-directory", type=str, default=os.getcwd(),
            help="video save directory, the default value is the working directory"
        )
        create_cmd.add_argument("--cookie", type=str, required=True, help="account cookie")
        create_cmd.add_argument("--offset", type=int, default=0, help="skip N episodes")
        create_cmd.set_defaults(func=task.create)

        start_cmd.add_argument(
            "task_index", type=int,
            help="the index of the task, obtained by the \"show\" command"
        )
        start_cmd.set_defaults(func=task.start)

        show_cmd.set_defaults(func=task.show)

        args = main_parser.parse_args()
        args.func(args)
    except GentlemanError as e:
        print(e.msg)
        exit(1)


if __name__ == '__main__':
    main()
    pass
