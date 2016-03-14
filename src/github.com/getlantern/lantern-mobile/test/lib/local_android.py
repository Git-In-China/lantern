# -*- coding: utf-8 -*-

import time
import unittest
from suite import TestLantern


def log(msg):
    print (time.strftime("%H:%M:%S") + ": " + msg)


class LocalAndroid(TestLantern):
    def setUp(self):

        # Ref http://appium.io/slate/en/master/?python#appium-server-capabilities
        self.desired_caps = {
            'platformName': 'Android',
            'automationName': 'Selendroid',
            'aut': 'org.getlantern.lantern',
            'emulator': False
        }
        self.hub_url = 'http://localhost:4444/wd/hub'
        self.device_name = "local"
        TestLantern.setUp(self)


def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(LocalAndroid)
    unittest.TextTestRunner(verbosity=2).run(suite)
