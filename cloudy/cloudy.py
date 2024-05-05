""" Check for new files and upload them into the clouds. """
import os
import string
from functools import partial, reduce
from pathlib import Path
from random import choices
from subprocess import Popen, check_output
from typing import Callable, Optional
from unittest.mock import patch

import click
from click import argument, group, option

from cloudy import lib
from cloudy._version import __version__

PATH_ARG = partial(click.Path, exists=True, resolve_path=True)


@group()
@click.version_option(__version__)
def cli() -> None:
    """Wrap command group"""
    patch("subprocess.Popen", lib.monkey_patch_pyi(Popen), spec=True).start()


@cli.command()
def test() -> None:
    """Run tests through CLI... I know, right?"""
    # test config_from_file
    c_path = Path(f"/tmp/{_random_str()}")
    c_path.write_text("foo: bar")
    assert lib.config_from_file(c_path) == {"foo": "bar"}

    # test pyinstaller compat
    os.environ["LD_LIBRARY_PATH"] = "foo"
    os.environ["LD_LIBRARY_PATH_ORIG"] = "not-foo"
    assert "LD_LIBRARY_PATH=not-foo" in str(check_output(["env"]))

    print("OK!")


@cli.command()
@argument("to_watch", type=PATH_ARG(dir_okay=True, file_okay=False))
@option(
    "config",
    "--config",
    "-c",
    type=PATH_ARG(dir_okay=False, file_okay=True),
    default=None,
)
def watch(to_watch: str, config: Optional[str] = None) -> None:
    """Watch directory"""
    print(f"Watching {to_watch}...")
    cfg = lib.config_from_file(Path(config) if config else _config_path())
    exec_before = cfg.get("exec_before", [])
    use_knock = bool(cfg["ssh"].get("use_knock", False))

    handler = _compose(
        partial(lib.effect_cmd, exec_before),
        partial(
            lib.ssh_upload, cfg["ssh"]["dest"], cfg["ssh"]["key"], use_knock
        ),
        partial(lib.bitly_shorten, cfg["bitly_token"], cfg["web_root"]),
        lib.copy_to_clipboard,
        lambda x: f"New Screenshot: {x}",
        lib.show_notification,
    )

    error_handler = partial(lib.show_notification, urgency="critical")

    notifier = lib.watch_dir(
        Path(to_watch),
        rec=bool(cfg.get('rec', True)),
        handler=handler,
        error_handler=error_handler,
    )

    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break


def _random_str(n: int = 12) -> str:
    """Produce a random string of length n"""
    return "".join(choices(string.ascii_uppercase + string.digits, k=n))


def _config_path(f_name: str = "../config.yaml") -> Path:
    """Returns an absolute path to the config file"""
    return Path(os.path.abspath(os.path.dirname(__file__))) / f_name


def _compose(*functions: Callable) -> Callable:
    """Compose a bunch of functions"""
    return reduce(lambda f, g: lambda x: f(g(x)), functions[::-1], lambda x: x)


if __name__ == "__main__":
    cli()
