# mbed-test-wrapper
Wrap the mbed test loader so it can easily be used by yotta targets to run
tests on target hardware.

Usage:

```
usage: mbed-test-wrapper [-h] [-t TARGET] [-i TIMEOUT] program

positional arguments:
  program               executable file to run

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        execution target name
  -i TIMEOUT, --timeout TIMEOUT
                        max time to wait for the program (seconds)

```



