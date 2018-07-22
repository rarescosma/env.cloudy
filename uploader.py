#!/usr/bin/env python2
"Uploads a file to cloudy or shortens the dropbox URL"

import sys
import subprocess
from subprocess import check_output
import os
import yaml
from cloudapp.cloud import Cloud
from optparse import OptionParser
import bitly_api
from urllib import quote_plus

class CloudUpload(object):
    "Uploader class"

    config = {}

    def __init__(self):
        # Add argument parser options
        parser = OptionParser(usage='usage: %prog --file path_to_file_you_want_to_upload.jpg')
        parser.add_option("-f", "--file", dest="filename", help="Path to the file you want to upload.")

        self.options = parser.parse_args()[0]

        # Check the filename
        if not self.options.filename:
            parser.error('Filename is required')
            sys.exit(-1)
        if not os.path.isfile(self.options.filename):
            parser.error('Invalid filename')
            sys.exit(-1)

        # Load yaml config
        self.loadConfig()

        # Upload file
        if self.config['upload_to_vps']:
            self.uploadVps()

        if self.config['provider'] == 'cloudy':
            self.uploadCloudy()
        elif self.config['provider'] == 'dropbox':
            self.shortenStatic()


    def loadConfig(self):
        "Loads the YAML config"
        stream = open(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml', 'r')
        self.config = yaml.load(stream)

    def uploadCloudy(self):
        "Handles cloudy uploads"
        cl = Cloud()
        cl.auth( self.config['cloudy_username'], self.config['cloudy_password'] )

        self.postProcess(cl.upload_file(self.options.filename))

    def shortenDropbox(self):
        "Handles dropbox shortening - disabled due to public folder gone"
        url = "%s/%s" % (self.config['dropbox_prefix'], os.path.basename(self.options.filename))
        conn = bitly_api.Connection(access_token=self.config['bitly_token'])

        self.postProcess(conn.shorten(url))

    def shortenStatic(self):
        "Handles static shortening"
        url = "%s/%s" % (self.config['static_prefix'], quote_plus(
            os.path.basename(self.options.filename)))
        conn = bitly_api.Connection(access_token=self.config['bitly_token'])

        self.postProcess(conn.shorten(url))

    def uploadVps(self):
        "Uploads the file to the VPS"
        cmd = [
            'rsync',
            '-avP',
            '-e',
            "ssh -i %s" % self.config['vps_identity'],
            os.path.realpath(self.options.filename),
            self.config['vps_connection']
        ]

        print check_output(cmd)
        self.shortenStatic()

    def postProcess(self, result):
        "Puts the resulting URL in the clipboard and notifies"
        self.toClipboard(result['url'])
        self.showNotification(result['url'])

    def toClipboard(self, what):
        "Adds a string to all clipboards"
        # "primary":
        xsel_proc = subprocess.Popen(['xsel', '-pi'], stdin=subprocess.PIPE)
        xsel_proc.communicate(what)
        # "clipboard":
        xsel_proc = subprocess.Popen(['xsel', '-bi'], stdin=subprocess.PIPE)
        xsel_proc.communicate(what)

    def showNotification(self, what):
        "Sends an inotification"
        subprocess.call(['notify-send', 'New Screenshot', what])


cu = CloudUpload()
sys.exit(0)
