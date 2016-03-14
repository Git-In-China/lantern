# -*- coding: utf-8 -*-

import requests


class DeviceFinder:
    """ Full constructor with username and password
    """
    def __init__(self, url="https://cloud.testdroid.com", apiKey=None, download_buffer_size=65536):
        self.cloud_url = url
        self.apiKey = apiKey
        self.download_buffer_size = download_buffer_size

    """ Append dictionary items to header
    """
    def _build_headers(self, headers=None):
        hdrs = {}
        hdrs["Accept"] = "application/json"
        if headers is not None:
            hdrs.update(headers)
        return hdrs

    """ Returns list of devices
    """
    def get_devices(self, limit=0):
        return self.get("devices?limit=%s" % (limit))

    """ GET from API resource
    """
    def get(self, path=None, get_headers=None, auth=None):
        url = "%s/api/v2/%s" % (self.cloud_url, path)
        headers = self._build_headers(get_headers)
        res = requests.get(url, headers=headers, auth=auth)
        if res.ok:
            return res.json()
        else:
            res.raise_for_status()

    """ Find all devices in a device group
    """
    def devices_by_group(self, group_id):
        if self.apiKey is None:
            print "API KEY not found"
            return []
        resp = self.get("me/device-groups/%d/devices" % (group_id),
                        auth=(self.apiKey, ''))
        return map(lambda d: str(d['displayName']), resp['data'])

    """ Find available free Android device
    """
    def available_free_android_device(self, limit=0):
        print "Searching Available Free Android Device..."

        for device in self.get_devices(limit)['data']:
            if (device['creditsPrice'] == 0
                    and device['locked'] is False
                    and device['osType'] == "ANDROID"
                    and device['softwareVersion']['apiLevel'] > 16):
                print "Found device '%s'" % device['displayName']
                return str(device['displayName'])

        print "No available device found"
        print ""
        return None

    """ Find available free iOS device
    """
    def available_free_ios_device(self, limit=0):
        print "Searching Available Free iOS Device..."

        for device in self.get_devices(limit)['data']:
            if (device['creditsPrice'] == 0
                    and device['locked'] is False
                    and device['osType'] == "IOS"):
                print "Found device '%s'" % device['displayName']
                return str(device['displayName'])

        print "No available device found"
        return None

    """ Find out the API level of a Device
    """
    def device_API_level(self, deviceName):
        print "Searching for API level of device '%s'" % deviceName

        try:
            device = self.get(path="devices?search=%s" % deviceName)
            apiLevel = device['data'][0]['softwareVersion']['apiLevel']
            print "Found API level: %s" % apiLevel
            return apiLevel
        except Exception, e:
            print "Error: %s" % e
            return
