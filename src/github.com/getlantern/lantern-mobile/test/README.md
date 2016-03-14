# Blackbox test on Lantern Android

## Perquisites

* Build the Lantern Android debug APK

```
(cd ../../../../../; make android-debug)
```

* Install required python packages

```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Run tests

Run `. venv/bin/activate` before executing any python scripts.

The screenshots took in each run will be in a separate directory under `./screenshots`.

Modify `lib/suite.py` to add more tests.

### Test on Testdroid cloud

Make sure you properly set `TESTDROID_APIKEY` environment variable.

You have several options to run tests on Testdroid cloud.

* Run on any available free cloud device.

```
./start_test.py
```

* Run on specific cloud device.

```
./start_test.py --device "Xiaomi MI 1S"
```

* Run on all devices in specific device group on cloud.

```
./start_test.py --group 14
```

Latter two options can be combined.

The script will upload the debug APK before running any test. Supply `--no-upload` option to skip uploading and use the latest uploaded APK.

### Test on locally connected device

* Uninstall Lantern from target device.

Selendroid will install the APK with a different signature. Installation will fail if there's an existing APK with different signature is installed.


* Connect device and keep screen unlocked.

* Start Selendroid standalone server (will download it at first time).

```
./selendroid.sh
```

* Run test script

```
./start_test.py --local
```

Check for Selendroid output if the error message is not clear enough.
