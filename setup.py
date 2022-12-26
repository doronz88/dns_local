#!/usr/bin/env python

from pathlib import Path

from setuptools import setup, find_packages

BASE_DIR = Path(__file__).parent.resolve(strict=True)
VERSION = '2.0.0'
PACKAGE_NAME = 'dns_local'
PACKAGES = [p for p in find_packages() if not p.startswith('tests')]


def parse_requirements():
    reqs = []
    with open(BASE_DIR / 'requirements.txt', 'r') as fd:
        for line in fd.readlines():
            line = line.strip()
            if line:
                reqs.append(line)
    return reqs


def get_description():
    # on Windows, read_text() will replace the emoji unicode characters
    return (BASE_DIR / 'README.md').read_text(errors='ignore')


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description='Simple python3 DNS server',
    long_description=get_description(),
    long_description_content_type='text/markdown',
    author='DoronZ',
    author_email='doron88@gmail.com',
    license='GNU GENERAL PUBLIC LICENSE - Version 3, 29 June 2007',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    url='https://github.com/doronz88/dns_local',
    project_urls={
        'dns_local': 'https://github.com/doronz88/dns_local'
    },
    packages=PACKAGES,
    install_requires=parse_requirements(),
    entry_points={
        'console_scripts': ['dns_local=dns_local.__main__:cli'],
    }
)
