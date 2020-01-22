#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4 expandtab ai
#
# File Created: Tue 10 Jan 00:31:22 GMT 2017
# Copyright 2017
#
# Licensced under the GPLv3
#
#  =============================================================|

from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open("./flac2all_pkg/version", 'r') as fd:
    vers = fd.read()
    vers = str(vers.strip())
    vers = vers.replace("test.", "")  # Remove test marker for publishing to test repo

setup(
    name="flac2all",
    version=vers,
    packages=["flac2all_pkg"],
    # metadata for upload to PyPI
    author="ZivaVatra",
    author_email="info@ziva-vatra.com",
    description="Multi process, clustered, FLAC to multi codec audio converter with tagging support",
    long_description='''
Started in 2003 as a flac to ogg vorbis converter, flac2All has grown into a multiprocess, network clustered program that will convert your collection of FLAC files into mp3,ogg vorbis,opus,flac,aac and another 60+ audio formats, complete with any tags that the source file had. Designed to be extended with new formats easily as time goes on, it is a utility for people with with large FLAC collections who want a way to convert multiple files in parallel.

Tested on Linux and FreeBSD, let me know how it works on other Unix OS'es.
''',
    long_description_content_type="text/plain",
    license="GPLv3",
    url="https://github.com/ZivaVatra/flac2all",
    # From https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],
    keywords='multithread, multiprocess, batch, flac, converter, mp3, vorbis,\
opus, aac, lame, music, audio, ffmpeg',

    entry_points={
        'console_scripts': [
            'flac2all = flac2all_pkg.__init__:main',
        ],
    }
)
