# -*- coding: utf-8 -*-
#
# For help on setting up your machine and configuring this TestScript go to
# http://help.testdroid.com/customer/portal/topics/631129-appium/articles
#

import time
import unittest
from device_finder import DeviceFinder
from suite import TestLantern, ParametrizedTestCase

appium_url = 'http://appium.testdroid.com/wd/hub'


def log(msg):
    print (time.strftime("%H:%M:%S") + ": " + msg)


class TestdroidAndroid(TestLantern):
    def setUp(self):
        device = self.param['device']
        app = self.param['app']
        api_key = self.param['api_key']

        # Ref http://docs.testdroid.com/appium/testdroid-desired-caps/
        self.desired_caps = {
            'testdroid_apiKey': api_key,
            'testdroid_project': 'Lantern',
            'testdroid_testrun': 'Lantern test',
            'testdroid_device': device,
            'testdroid_app': app,
            'platformName': 'Android',
            'deviceName': 'Android Phone',
            'aut': 'org.getlantern.lantern'
        }

        apiLevel = DeviceFinder().device_API_level(device)
        if apiLevel > 16:
            self.desired_caps['testdroid_target'] = 'Android'
        else:
            self.desired_caps['testdroid_target'] = 'Selendroid'

        self.hub_url = appium_url
        self.device_name = device
        TestLantern.setUp(self)


def available_free_android_device():
    ret = []
    # Loop will not exit until free device is found
    deviceFinder = DeviceFinder()
    while True:
        d = deviceFinder.available_free_android_device()
        if d is not None:
            ret.append(d)
            return ret


def executeTests(api_key, app, group_id=None, device_name=None):
    devices = []
    if device_name is not None:
        devices.append(device_name)
    if group_id is None:
        if len(devices) == 0:
            devices = available_free_android_device()
    else:
        devices.extend(DeviceFinder(apiKey=api_key).devices_by_group(group_id))

    suite = unittest.TestSuite()
    map(lambda d: suite.addTest(
        ParametrizedTestCase.parametrize(
            TestdroidAndroid, param={
                'api_key': api_key,
                'device': d,
                'app': app}
        )),
        devices)
    unittest.TextTestRunner(verbosity=2).run(suite)
