"""
Opinionated screenshot watcher
"""
import os
import traceback
from functools import wraps
from pathlib import Path
from subprocess import PIPE, Popen, check_output
from typing import Any, Callable, Dict, List
from urllib.parse import quote_plus

import pyinotify
import requests
import yaml


# used to monkeypatch subprocess primitives for pyinstaller compatibility
# see https://github.com/pyinstaller/pyinstaller/tree/master/doc/runtime-information.rst
def monkey_patch_pyi(thing: Callable) -> Callable:
    @wraps(thing)
    def inner(*args, **kwargs):  # type: ignore
        os_env = dict(os.environ)
        lp_key = "LD_LIBRARY_PATH"
        lp_orig = os_env.get(lp_key + "_ORIG")
        kwargs["env"] = kwargs.get("env", os_env)
        if lp_orig is not None:
            kwargs["env"][lp_key] = lp_orig
        else:
            kwargs["env"].pop(lp_key, None)
        return thing(*args, **kwargs)

    return inner


# Configuration
def config_from_file(file_path: Path) -> Dict[str, Any]:
    """Return parsed config from a YAML file"""
    return yaml.safe_load(file_path.read_text()) or {}


# Watchin'
def watch_dir(dir_path: Path, **kwargs: Any) -> pyinotify.Notifier:
    """Return a notifier for handling dir changes"""
    watch_manager = pyinotify.WatchManager()
    watch_manager.add_watch(str(dir_path), pyinotify.IN_CLOSE_WRITE, rec=True)
    return pyinotify.Notifier(watch_manager, ProcessChange(**kwargs))


class ProcessChange(pyinotify.ProcessEvent):
    """Calls handler with the changed file path on CLOSE_WRITE"""

    __handler: Callable
    __error_handler: Callable

    def __init__(
        self,
        handler: Callable = print,
        error_handler: Callable = print,
        **kargs: Any,
    ) -> None:
        self.__handler = handler  # type: ignore
        self.__error_handler = error_handler  # type: ignore
        super().__init__(**kargs)

    def process_IN_CLOSE_WRITE(self, event: pyinotify.Event) -> None:
        """Handle CLOSE_WRITE"""
        try:
            self.__handler(Path(os.path.join(event.path, event.name)))
        except Exception as exc:
            print(traceback.format_exc())
            self.__error_handler(exc)


# Processing
def effect_cmd(cmd: List, _: Any) -> Any:
    """Exec command as effect but proxy input value"""
    if cmd:
        check_output(cmd)
    return _


def ssh_upload(dest: str, key: str, use_knock: bool, file_path: Path) -> Path:
    """Upload file to destination using rsync/ssh"""
    if use_knock:
        check_output(["cioc"])
    cmd = [
        "rsync",
        "-av",
        "-e",
        f"ssh -i {key}",
        str(file_path.absolute()),
        dest,
    ]
    check_output(cmd)
    return file_path


def bitly_shorten(token: str, web_root: str, file_path: Path) -> str:
    """Shorten the file URL through bitly"""
    return requests.post(
        "https://api-ssl.bitly.com/v4/shorten",
        json={
            "long_url": f"{web_root}/{quote_plus(file_path.name)}",
        },
        headers={"Authorization": f"Bearer {token}"},
    ).json()["link"]


def copy_to_clipboard(what: str) -> str:
    """Put the input string into all known clipboards"""
    # Primary + clipboard
    # pylint: disable=consider-using-with
    xsel_proc = Popen(["xsel", "-pbi"], stdin=PIPE)
    xsel_proc.communicate(bytes(what, encoding="utf-8"))
    return what


def show_notification(what: Any, urgency: str = "normal") -> str:
    """Show a notification about the new screenshot"""
    coerced = str(what)
    check_output(["notify-send", "-u", urgency, coerced])
    return coerced
