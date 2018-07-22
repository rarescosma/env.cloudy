"""
Opinionated screenshot watcher
"""
import os
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict
from urllib.parse import quote_plus

import pyinotify
import requests
import yaml

Url = str


# Configuration
def config_from_file(f: Path) -> Dict[str, Any]:
    """Return parsed config from a YAML file"""
    return yaml.safe_load(f.read_text()) or {}


# Watchin'
def watch_dir(d: Path, handler: Callable = print) -> pyinotify.Notifier:
    """Return a notifier for handling dir changes"""
    wm = pyinotify.WatchManager()
    wm.add_watch(str(d), pyinotify.IN_CLOSE_WRITE, rec=True)
    return pyinotify.Notifier(wm, ProcessChange(handler=handler))


class ProcessChange(pyinotify.ProcessEvent):
    """Calls handler with the changed file path on CLOSE_WRITE"""
    __handler: Callable

    def __init__(self, handler: Callable = print, **kargs: Any) -> None:
        self.__handler = handler
        super().__init__(**kargs)

    def process_IN_CLOSE_WRITE(self, event):
        """Handle CLOSE_WRITE"""
        self.__handler(Path(os.path.join(event.path, event.name)))


# Processing
def ssh_upload(dest: str, key: str, f: Path) -> Path:
    """Upload file to destination using rsync/ssh"""
    cmd = ['rsync', '-av', '-e', f'ssh -i {key}', str(f.absolute()), dest]
    subprocess.check_output(cmd)
    return f


def bitly_shorten(token: str, web_root: str, f: Path) -> Url:
    """Shorten the file URL through bitly"""
    return requests.get(
        'https://api-ssl.bitly.com/v3/shorten',
        params={
            'access_token': token,
            'longUrl': f'{web_root}/{quote_plus(f.name)}',
        }
    ).json()['data']['url']


def copy_to_clipboard(what: Url) -> Url:
    """Put the input string into all known clipboards"""
    # Primary + clipboard
    xsel_proc = subprocess.Popen(['xsel', '-pbi'], stdin=subprocess.PIPE)
    xsel_proc.communicate(bytes(what, encoding='utf-8'))
    return what


def show_notification(what: Url) -> Url:
    """Show a notification about the new screenshot"""
    subprocess.check_output(['notify-send', 'New Screenshot', what])
    return what
