# -*- coding: utf-8 -*-

import os
import time
import unittest
from appium import webdriver
# from time import sleep
# from selenium.common.exceptions import WebDriverException


def log(msg):
    print (time.strftime("%H:%M:%S") + ": " + msg)


class ParametrizedTestCase(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """
    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite


class TestLantern(ParametrizedTestCase):
    def setUp(self):
        log("Starting Appium test using device '%s'" % self.device_name)
        tm = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        self.screenshotDir = os.path.join('./screenshots', self.device_name+'_'+tm)
        log("Will save screenshots at: " + self.screenshotDir)
        try:
            os.makedirs(self.screenshotDir)
        except OSError, e:
            log("Fail to create screenshot directory %s: %s", self.screenshotDir, e)

        log("WebDriver request initiated. Waiting for response, this typically takes 2-3 mins")
        self.driver = webdriver.Remote(self.hub_url, self.desired_caps)
        log("WebDriver response received")

    def tearDown(self):
        log("Quitting")
        self.driver.quit()

    def testStartAndQuit(self):
        log("Test: start and quit app")
        self.driver.save_screenshot(self.screenshotDir + "/1_appLaunch.png")

        self.by_id('settings_icon').click()
        self.driver.save_screenshot(self.screenshotDir + "/2_showDrawer.png")

        self.elem('Quit').click()
        self.driver.save_screenshot(self.screenshotDir + "/3_quit.png")

        # log("  Typing in name")
        # elems = self.driver.find_elements_by_class_name('android.widget.EditText')
        # log("  info: EditText:" + repr("len(elems)"))
        # log("  Filling in name")
        # elems[0].send_keys("Testdroid User")
        # sleep(2)
        # log("  Taking screenshot: 2_nameTyped.png")
        # self.driver.save_screenshot(self.screenshotDir + "/2_nameTyped.png")

        # try:
        #     log("  Hiding keyboard")
        #     self.driver.hide_keyboard()
        # except:
        #     pass  # pass exception, if keyboard isn't visible already
        # log("  Taking screenshot: 3_nameTypedKeyboardHidden.png")
        # self.driver.save_screenshot(self.screenshotDir + "/3_nameTypedKeyboardHidden.png")

        # log("  Clicking element 'Buy 101 devices'")
        # self.elem('Buy 101 devices').click()

        # log("  Taking screenshot: 4_clickedButton1.png")
        # self.driver.save_screenshot(self.screenshotDir + "/4_clickedButton1.png")

        # log("  Clicking Answer")
        # self.elem('Answer').click()

        # log("  Taking screenshot: 5_answer.png")
        # self.driver.save_screenshot(self.screenshotDir + "/5_answer.png")

        # log("Navigating back to Activity-1")
        # self.driver.back()
        # log("  Taking screenshot: 6_mainActivity.png")
        # self.driver.save_screenshot(self.screenshotDir + "/6_mainActivity.png")

        # log("  Clicking element 'Use Testdroid Cloud'")
        # self.elem('Use Testdroid Cloud').click()

        # log("  Taking screenshot: 7_clickedButton2.png")
        # self.driver.save_screenshot(self.screenshotDir + "/7_clickedButton2.png")

        # log("  Clicking Answer")
        # self.elem('Answer').click()

    def isSelendroid(self):
        if self._isSelendroid is None:
            return self._isSelendroid

        self._isSelendroid = False
        if 'automationName' in self.driver.capabilities:
            if self.driver.capabilities['automationName'] == 'selendroid':
                self._isSelendroid = True

        return self._isSelendroid

    def elem(self, text):
        if self.isSelendroid:
            return self.driver.find_element_by_link_text(text)
        else:
            return self.driver.find_element_by_name(text)

    def by_id(self, id):
        return self.driver.find_element_by_id(id)
