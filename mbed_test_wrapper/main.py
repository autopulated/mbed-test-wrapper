#! /usr/bin/env python
# Copyright 2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import subprocess
import argparse
import json
import sys
import os
import threading
import json

class RunWithTimeout(threading.Thread):
    def __init__(self, command):
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        self.process = subprocess.Popen(self.command)
        self.process.wait()

    def runFor(self, timeout):
        self.start()
        self.join(timeout)
        if self.is_alive():
            self.process.kill()
            self.join()
            return -1
        else:
            return self.process.returncode

def walkUpDirs():
    d = os.getcwd()
    while True:
        yield d
        parent_d = os.path.dirname(d)
        if parent_d == d:
            break
        else:
            d = parent_d

def findConfig():
    'Search the current directory then its parents for a yotta_config.json file'
    config = None
    for d in walkUpDirs():
        if os.path.isfile(os.path.join(d, 'yotta_config.json')):
            with open(os.path.join(d, 'yotta_config.json')) as f:
                config = f.read()
            break
        if os.path.isfile(os.path.join(d, 'module.json')):
            # stop: we found a yotta module, the merged json will always be in
            # a subdir of this
            break
    return config

def getBaudRateFromConfig():
    ''' mbed now writes the debug serial baud rate to yotta config:
        unfortunately there's no way to discover it automatically from the
        device, so to run a program we need to read this.

        Look for the yotta_config.json file in this directory and its parents,
        and then read the baud rate from it, if found. Otherwise return None
    '''
    baud_rate = None
    config = findConfig()
    if config is not None:
        parsed = json.loads(config)
        baud_rate = parsed.get('mbed-os', {}).get('stdio', {}).get('default-baud', None)
    return baud_rate


def run():
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--target', dest='target', help='execution target name (e.g. K64F)')
    p.add_argument('-i', '--timeout', dest='timeout', help='max time to wait for the program (seconds)', type=float, default=10.0)
    p.add_argument('program', help='executable file to run')

    args, unknown_args = p.parse_known_args()

    # run mbed-ls to find a board that matches the specified target:
    mbedls = subprocess.Popen(
        ['mbedls', '--json'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = mbedls.communicate()
    if mbedls.returncode:
        sys.stderr.write('Failed to list mbeds: %s, %s\n' % (out, err))
        sys.exit(-1)

    mbeds = json.loads(out.decode('utf-8'))

    serial_port = None
    mount_point = None
    for mbed in mbeds:
        if mbed['platform_name'] == args.target:
            mount_point = mbed['mount_point']
            serial_port = mbed['serial_port']
            break

    baud_rate = getBaudRateFromConfig()
    if baud_rate is not None:
        serial_port = serial_port + (':%s' % baud_rate)

    if not mount_point:
        sys.stderr.write(
            'Target "%s" not found. Available targets are: %s\n' %
            (args.target, ', '.join([x['platform_name'] for x in mbeds]))
        )
        sys.exit(-1)
    
    binfile_name = args.program + '.bin'
    # convert the executable to a .bin file, which the mbed test runner needs,
    # if we don't already have one:
    if not os.path.isfile(binfile_name):
        objcopy = subprocess.Popen(
            ['arm-none-eabi-objcopy', '-O', 'binary', args.program, binfile_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = objcopy.communicate()
        if objcopy.returncode:
            sys.stderr.write('Failed to generate bin file for executable: %s, %s\n' % (out, err))
            sys.exit(-1)

    # run mbedhtrun and pipe its output to our stdout & stderr
    returncode = RunWithTimeout([
        'mbedhtrun', '-d', mount_point, '-f', binfile_name, '-p', serial_port, '-C', '4', '-m', args.target
    ] + unknown_args).runFor(args.timeout)
    if returncode:
        sys.exit(returncode)

if __name__ == '__main__':
    run()

