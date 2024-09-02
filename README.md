## Cloudy

Dead-simple tool to handle screenshot sharing from Linux.

It:

* watches a directory for new images
* uploads any new image to a remote server through rsync-ssh
* infers the URL of the uploaded image
* shortens the URL using bit.ly
* copies the short URL to the clipboard
* displays a notification

Check out the [sample configuration](config.yaml.sample) for a list of
configuration keys you need to provide.


### Installing

#### Option 1 - download a static binary

Head over to the [releases](https://github.com/rarescosma/env.cloudy/releases)
page and download a tarball containing a statically built binary.

#### Option 2 - build and install locally

Clone the repo.

Install [pyenv](https://github.com/pyenv/pyenv#installation) and Python 3.12:

```
pyenv install $(pyenv install --list \
 | sed 's/^[[:space:]]*//' | grep '^3.12' \
 | sort --version-sort | tail -1)
```

Generate a one-file [PyInstaller](https://pyinstaller.org/en/v6.10.0/) 
executable and copy it to `${HOME}/bin`:

```
make && make install
```
