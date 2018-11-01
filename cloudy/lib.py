"""
Opinionated screenshot watcher
"""
import os
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List
from urllib.parse import quote_plus

import pyinotify
import requests
import yaml


# Configuration
def config_from_file(f: Path) -> Dict[str, Any]:
    """Return parsed config from a YAML file"""
    return yaml.safe_load(f.read_text()) or {}


# Watchin'
def watch_dir(d: Path, **kwargs) -> pyinotify.Notifier:
    """Return a notifier for handling dir changes"""
    wm = pyinotify.WatchManager()
    wm.add_watch(str(d), pyinotify.IN_CLOSE_WRITE, rec=True)
    return pyinotify.Notifier(wm, ProcessChange(**kwargs))


class ProcessChange(pyinotify.ProcessEvent):
    """Calls handler with the changed file path on CLOSE_WRITE"""
    __handler: Callable
    __error_handler: Callable

    def __init__(
            self,
            handler: Callable = print,
            error_handler: Callable = print,
            **kargs: Any
    ) -> None:
        self.__handler = handler
        self.__error_handler = error_handler
        super().__init__(**kargs)

    def process_IN_CLOSE_WRITE(self, event):
        """Handle CLOSE_WRITE"""
        try:
            self.__handler(Path(os.path.join(event.path, event.name)))
        except Exception as exc:
            self.__error_handler(exc)


# Processing
def effect_cmd(cmd: List, _: Any) -> Any:
    """Exec command as effect but proxy input value"""
    if cmd:
        subprocess.check_output(cmd)
    return _

def ssh_upload(dest: str, key: str, f: Path) -> Path:
    """Upload file to destination using rsync/ssh"""
    subprocess.check_output(['cioc'])
    cmd = ['rsync', '-av', '-e', f'ssh -i {key}', str(f.absolute()), dest]
    subprocess.check_output(cmd)
    return f


def bitly_shorten(token: str, web_root: str, f: Path) -> str:
    """Shorten the file URL through bitly"""
    return requests.get(
        'https://api-ssl.bitly.com/v3/shorten',
        params={
            'access_token': token,
            'longUrl': f'{web_root}/{quote_plus(f.name)}',
        }
    ).json()['data']['url']


def copy_to_clipboard(what: str) -> str:
    """Put the input string into all known clipboards"""
    # Primary + clipboard
    xsel_proc = subprocess.Popen(['xsel', '-pbi'], stdin=subprocess.PIPE)
    xsel_proc.communicate(bytes(what, encoding='utf-8'))
    return what


def show_notification(what: Any, urgency: str = 'normal') -> str:
    """Show a notification about the new screenshot"""
    coerced = str(what)
    subprocess.check_output(['notify-send', '-u', urgency, coerced])
    return coerced
