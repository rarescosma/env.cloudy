""" Check for new files and upload them into the clouds. """

import os
import string
import sys
from functools import partial, reduce
from pathlib import Path
from random import choices
from subprocess import Popen, check_output
from typing import Callable
from unittest.mock import patch

import click
from click import group, option
from xdg.BaseDirectory import xdg_config_home

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
@option(
    "config",
    "--config",
    "-c",
    type=PATH_ARG(dir_okay=False, file_okay=True),
    default=os.path.join(xdg_config_home, "cloudy.yaml"),
)
def watch(config: str) -> None:
    """Watch directory"""
    cfg_path = Path(config)
    if not cfg_path.exists() or not cfg_path.is_file():
        print(f"Could not open config file at '{config}'. Bailing...", file=sys.stderr)
        sys.exit(1)

    cfg = lib.config_from_file(cfg_path)
    exec_before = cfg.get("exec_before", [])

    handler = _compose(
        partial(lib.effect_cmd, exec_before),
        partial(lib.ssh_upload, cfg["ssh"]["dest"], cfg["ssh"]["key"]),
        partial(lib.bitly_shorten, cfg["bitly_token"], cfg["url_prefix"]),
        lib.copy_to_clipboard,
        lambda x: f"New Screenshot: {x}",
        lib.show_notification,
    )

    error_handler = partial(lib.show_notification, urgency="critical")

    print(f"Watching '{cfg['watch_dir']}'")
    notifier = lib.watch_dir(
        Path(cfg["watch_dir"]),
        rec=bool(cfg.get("rec", True)),
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


def _compose(*functions: Callable) -> Callable:
    """Compose a bunch of functions"""
    return reduce(lambda f, g: lambda x: f(g(x)), functions[::-1], lambda x: x)


if __name__ == "__main__":
    cli()
