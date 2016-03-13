# -*- coding: utf-8 -*-

import requests
import os
import sys

upload_url = 'http://appium.testdroid.com/upload'
myfile = '../app/build/outputs/apk/lantern-debug.apk'


def upload(api_key):
    print "Uploading %s to %s" % (myfile, upload_url)
    files = {'file': (os.path.basename(myfile),
                      open(myfile, 'rb'),
                      'application/octet-stream')}
    r = requests.post(upload_url,
                      files=files,
                      headers={'Accept': 'application/json'},
                      auth=(api_key, ''))
    if "successful" in r.json()['value']['message']:
        apk_path = r.json()['value']['uploads']['file']
        print "Filename to use in testdroid capabilities in test: {}".format(apk_path)
        return apk_path
    else:
        print "Upload response: \n{}".format(r.json())
        sys.exit(-1)
