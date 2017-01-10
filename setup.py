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

from setuptools import setup, find_packages
setup(
    name="flac2all",
    version="4.0",
    packages=find_packages(),
)


# metadata for upload to PyPI
author = "ZivaVatra",
author_email = "zv@ziva-vatra.com",
description = "Started in 2003, flac2All has grown into a multi-process script that will convert your collection of FLAC files into various other formats (currently mp3,ogg vorbis, opus, flac and acc), complete with any tags that the source file had. Designed to be extended with new formats easily as time goes on, it is a utility for people with with large FLAC collections who also want a way to convert multiple files in parallel.",
license = "GPLv3",
keywords = "multithread multiprocess batch flac converter mp3 vorbis opus aac lame",
url = "http://ziva-vatra.com/index.php?aid=23",   # project home page, if any
