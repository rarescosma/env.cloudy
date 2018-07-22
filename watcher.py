#!/usr/bin/env python2
"Watches a local folder for images and calls the uploader script"
import os
import pyinotify
import subprocess
import yaml

def pathToSelf():
    "Returns the current script path"
    return os.path.dirname(os.path.realpath(__file__))

def loadConfig():
    "Loads the YAML config"
    stream = open(pathToSelf() + '/config.yaml', 'r')
    return yaml.load(stream)

class PTmp(pyinotify.ProcessEvent):
    "Processes file events"
    def process_IN_CLOSE_WRITE(self, event):
        "CREATE event handler"
        filename = os.path.join(event.path, event.name)
        print "Create: %s " % filename
        print subprocess.check_output([ pathToSelf() + '/uploader.py', '-f', filename])

config = loadConfig()

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CLOSE_WRITE
notifier = pyinotify.Notifier(wm, PTmp())
wdd = wm.add_watch(config['images'], mask, rec=True)

while True:
    try:
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        break
