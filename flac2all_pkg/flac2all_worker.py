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

import signal

from logging import console

log = console(stderr=True)


def worker_process(target_host):
	log.info("Spawned worker process")
	eworker = core.encode_worker(target_host)
	# because we are a process, we just exit at the end
	sys.exit(eworker.run())


try:
	hostname = sys.argv[1]
except IndexError:
	log.print("Usage: %s $master_hostname" % sys.argv[0])
	sys.exit(1)

procs = []
while len(procs) != mp.cpu_count():
	procs.append(mp.Process(target=worker_process, args=(hostname,)))
	# Here we filter out any dead processes.
	# procs = [x for x in procs if x.is_alive() is True]

[x.start() for x in procs]
# And now wait

terminate = False


def sig(signal, frame):
	global terminate
	terminate = True


signal.signal(signal.SIGINT, sig)

while True:
	[x.join(timeout=1) for x in procs]
	if terminate:
		[x.terminate() for x in procs]
	if len([x for x in procs if x.is_alive() is True]) == 0:
		# All worker processes are done, exit
		sys.exit(0)
