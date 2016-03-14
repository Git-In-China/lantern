#!/usr/bin/env python

import sys
sys.path.append('./lib')

import os
import argparse
from upload import upload
import local_android
import testdroid_android


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Testdroid test script')
    parser.add_argument('--local', action='store_true',
                        help='Test from local emulator/device')
    parser.add_argument('--no-upload', action='store_true',
                        help='Not upload APK to testdroid before run test (uses the latest one)')
    parser.add_argument('--group', type=int,
                        help='The device group to run tests on. If neither group nor device supplied, will pick whichever free device')
    parser.add_argument('--device', type=str,
                        help='The specific device to run tests on. If neither group nor device supplied, will pick whichever free device')

    args = parser.parse_args()
    if args.local:
        local_android.test()
    else:
        testdroid_api_key = os.environ.get('TESTDROID_APIKEY')
        if testdroid_api_key is None:
            print "TESTDROID_APIKEY environment variable is not set!"
            sys.exit(1)
        testdroid_app = "latest"
        if args.no_upload is not True:
            testdroid_app = upload(testdroid_api_key)

        testdroid_android.executeTests(testdroid_api_key,
                                       testdroid_app,
                                       args.group,
                                       args.device)
