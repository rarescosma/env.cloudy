## Cloudy

Dead-simple tool to handle screenshot sharing from Linux.

It:

* watches a directory for new images
* uploads any new image to a remote server through rysnc-ssh
* infers an URL for the uploaded image
* shortens the URL using bit.ly
* copies the short URL to the clipboard
* displays a notification

Check out the [sample configuration](config.yaml.sample) for a list of
configuration keys you need to provide.


### Installing

Install [pyenv](https://github.com/pyenv/pyenv#installation) and Python 3.7.2:

```
pyenv install 3.7.2
```

Generate a one-file PyInstaller executable and copy it to `${HOME}/bin`:

```
make && make install
```
