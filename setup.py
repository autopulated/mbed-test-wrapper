# Copyright 2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import os
from setuptools import setup, find_packages

setup(
    name = "mbed_test_wrapper",
    version = "0.0.2",
    author = "James Crosby",
    author_email = "James.Crosby@arm.com",
    description = "Wrap the mbed test loader for easy use from yotta targets.",
    license = "Apache-2.0",
    keywords = "mbed test script",
    url = "about:blank",
    packages=find_packages(),
    package_data={
    },
    long_description = "Wrap the mbed test loader for easy use from yotta targets.",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
    ],
    entry_points = {
        "console_scripts": [
            "mbed_test_wrapper=mbed_test_wrapper:run"
        ],
    },
    install_requires=[
    ]
)

