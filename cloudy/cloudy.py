import os
import string
from pathlib import Path
from random import choices
from functools import partial, reduce
from typing import Callable, Optional

import click
from click import argument, group, option

from cloudy import lib

PATH_ARG = partial(click.Path, exists=True, resolve_path=True)


@group()
def cli():
    """Wrap command group"""
    pass


@cli.command()
def test():
    """Run tests through CLI... I know, right?"""
    # test config_from_file
    c_path = Path(f'/tmp/{_random_str()}')
    c_path.write_text('foo: bar')
    assert lib.config_from_file(c_path) == dict(foo='bar')

    print('OK!')


@cli.command()
@argument(
    'to_watch',
    type=PATH_ARG(dir_okay=True, file_okay=False)
)
@option(
    'config', '--config', '-c',
    type=PATH_ARG(dir_okay=False, file_okay=True),
    default=None
)
def watch(to_watch: str, config: Optional[str] = None):
    """Watch directory"""
    print(f'Watching {to_watch}...')
    cfg = lib.config_from_file(Path(config) if config else _config_path())

    handler = _compose(
        partial(
            lib.ssh_upload,
            cfg['ssh']['dest'],
            cfg['ssh']['key']
        ),
        partial(
            lib.bitly_shorten,
            cfg['bitly_token'],
            cfg['web_root']
        ),
        lib.copy_to_clipboard,
        lambda x: f'New Screenshot: {x}',
        lib.show_notification,
    )

    error_handler = partial(lib.show_notification, urgency='critical')

    notifier = lib.watch_dir(
        Path(to_watch),
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
    return ''.join(choices(string.ascii_uppercase + string.digits, k=n))


def _config_path(f_name: str = '../config.yaml') -> Path:
    """Returns an absolute path to the config file"""
    return Path(os.path.abspath(os.path.dirname(__file__))) / f_name


def _compose(*functions: Callable) -> Callable:
    """Compose a bunch of functions"""
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        functions[::-1],
        lambda x: x
    )


if __name__ == '__main__':
    cli()
