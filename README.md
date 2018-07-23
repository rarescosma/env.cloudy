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

Obtain a Python3.6 virtual environment.

`pip install -r requirements.txt`

`make dist/cloudy` will give you a one-file PyInstaller executable

`make install` will copy it to `${HOME}/bin`

