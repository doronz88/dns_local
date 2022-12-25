#!/usr/bin/env python

from distutils.core import setup

setup(name='dns_local',
      version='1.0',
      description='Simple CLI manager for dnsmasq entries on OSX',
      author='DoronZ',
      author_email='doron88@gmail.com',
      url='https://github.com/doronz88/dns_local',
      packages=['dns_local'],
      requires=['click', 'ifaddr'],
      entry_points={
          'console_scripts': ['dns_local=dns_local.__main__:cli'],
      }
      )
