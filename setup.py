#!/usr/bin/env python

import codecs
import os

from setuptools import find_packages, setup

from pytest_jobserver.metadata import VERSION


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-jobserver",
    version=VERSION,
    author="Tom Milligan",
    author_email="code@tommilligan.net",
    maintainer="Tom Milligan",
    maintainer_email="code@tommilligan.net",
    license="Apache Software License 2.0",
    url="https://github.com/tommilligan/pytest-jobserver",
    description="Limit parallel tests with posix jobserver.",
    keywords="pytest jobserver posix make cargo limit cap parallel limit",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.4",
    install_requires=["pytest"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={"pytest11": ["jobserver = pytest_jobserver.plugin"]},
)
