#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-jobserver",
    version="0.1.0",
    author="Tom Milligan",
    author_email="code@tommilligan.net",
    maintainer="Tom Milligan",
    maintainer_email="code@tommilligan.net",
    license="Apache Software License 2.0",
    url="https://github.com/tommilligan/pytest-jobserver",
    description="Parellise tests with posix jobserver.",
    long_description=read("README.md"),
    py_modules=["pytest_jobserver"],
    python_requires=">=3.4",
    install_requires=["pytest"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={"pytest11": ["jobserver = pytest_jobserver.plugin"]},
)
