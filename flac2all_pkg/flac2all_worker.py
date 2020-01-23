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
import sys
import signal

if __name__ == '__main__' and __package__ is None:
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

try:
	from core import encode_worker
	from logging import console
except ImportError:
	from .logging import console
	from .core import encode_worker

log = console(stderr=True)


def sig(signal, frame):
	global terminate
	terminate = True


def worker_process(target_host):
	log.info("Spawned worker process")
	eworker = encode_worker(target_host)
	# because we are a process, we just exit at the end
	sys.exit(eworker.run())


def main():
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

	signal.signal(signal.SIGINT, sig)

	while True:
		# We wait 30 seconds for a clean exit
		[x.join(timeout=30) for x in procs]
		# Force kill stragglers. This usually means
		# the master won't get the off line message, so
		# will have to wait for the response time out before
		# it exits
		if terminate:
			log.warn("Processes hung for >30 seconds, force terminating")
			[x.terminate() for x in procs]
		if len([x for x in procs if x.is_alive() is True]) == 0:
			# All worker processes are done, exit
			sys.exit(0)


if __name__ == "__main__":
	main()
