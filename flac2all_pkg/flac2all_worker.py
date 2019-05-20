#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 ai
#
# File Created: Fri 12 Apr 17:15:29 BST 2019
# Copyright 2019
#
# All rights reserved
#
# ============================================================|

__VERSION__ = (0, 0, 1)

import multiprocessing as mp
import core
import sys


def worker_process(target_host):
	print("Spawned worker process")
	encoder = core.transcoder()
	# because we are a process, we just exit at the end
	sys.exit(encoder.runworker(target_host))

try:
	hostname = sys.argv[1]
except IndexError:
	print("Usage: %s $master_hostname" % sys.argv[0])
	sys.exit(1)

procs = []
while len(procs) != mp.cpu_count():
	procs.append(mp.Process(target=worker_process, args=(hostname,)))

[x.start() for x in procs]
# And now wait
[x.join() for x in procs]
