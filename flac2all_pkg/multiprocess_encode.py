#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 ai expandtab
#    flac2all: Multi process flac converter
#       - Homepage: http://flac2all.witheredfire.com/
#       - Devpage: https://github.com/ZivaVatra/flac2all/
#
#    If you like the software, donations are appreciated:
#       BTC: 3QNErPVkkrn2R9R7uop9stfhzqUr8wecX6
#       BCH: bitcoincash:qpy377yuntryz4zmlt5zukn82rxmuphr5q0y895nwp
#       XMR: 45piRzk4fJxTNXdtLEoZ8QbQk2MQk6dAeGbHjaAWVtLEbR8tQUp7wo82EYGwD9AtJyFEfvitnvvJtfCftdetfgQASdJbdpH
#
#    All donations go to the ZV caffination fund, to keep me going through hacking sessions :-)
#
# LEGAL BIT:
#
#    Copyright (C) 2003 Z.V (info@ziva-vatra.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import multiprocessing as mp
from shutil import copy as copytarget
import sys
import os
import time
import queue

if __name__ == '__main__' and __package__ is None:
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

try:
	from config import opts
	from core import encode_thread, generate_summary
	from shell import shell
	from logging import console
except ImportError:
	from .config import opts
	from .core import encode_thread, generate_summary
	from .shell import shell
	from .logging import console



log = console(stderr=True)


def encode():
    sh = shell()  # Shell commands

    # process queue,the queue that will hold all the flac files we want to convert.
    #  format: [ $infile, $target_format ]
    pQ = mp.Queue()

    # copy queue (for copying non flac files if requested)
    #  format: [ $infile, $outfile ]
    cQ = mp.Queue()

    # logging queue, the encoders log progress to this
    # format: [
    #   $infile,
    #   $outfile,
    #   $format,
    #   $error_status,
    #   $return_code,
    #   $execution_time
    #   ]
    lQ = mp.Queue()

    # The non clustered (original) method
    # 1. populate the queue with flac files
    files = sh.getfiles(opts['dirpath'])
    count = 0
    for infile in files:

        for mode in opts['mode'].split(','):
            if infile.endswith(".flac"):
                pQ.put([infile, opts['dirpath'], opts['outdir'], mode])
                count += 1
            else:
                if opts['copy']:
                    cQ.put([infile, opts['dirpath'], opts['outdir'], mode])

    time.sleep(1)  # Delay to resolve queue "broken pipe" errors

    log.info("We have %d flac files to convert" % count)
    log.info("We have %d non-flac files to copy across" % cQ.qsize())

    # Right, how this will work here, is that we will pass the whole queue
    # to the encode threads (one per processor) and have them pop off/on as
    # necessary. Allows for far more fine grained control.

    opts['threads'] = int(opts['threads'])

    # keep flags for state (pQ,cQ)
    sflags = [0, 0]
    ap = []  # active processes
    start_time = time.time()
    while True:

        cc = opts['threads']

        while int(cc) > (len(ap)):
            log.info("Spawning execution process")
            proc = encode_thread(int(cc), "Thread %d" % int(cc), pQ, opts, lQ)
            proc.start()
            ap.append(proc)

        time.sleep(0.5)

        # Believe it or not, the only way way to be sure a queue is actually
        # empty is to try to get with a timeout. So we get and put back
        # and if we get a timeout error (10 secs), register it

        try:
            pQ.put(pQ.get(timeout=10))
        except mp.TimeoutError as e:
            log.ok("Process queue finished.")
            sflags[0] = 1
        except queue.Empty as e:
            log.ok("Process queue finished.")
            sflags[0] = 1
        else:
            sflags[0] = 0

        try:
            command = cQ.get(timeout=10)
            srcfile, srcroot, dest, encformat = command
            outdir = sh.generateoutdir(srcfile, os.path.join(dest, encformat), srcroot)
            copytarget(srcfile, outdir)
            log.info(("%s => %s" % (srcfile, outdir)))
        except mp.TimeoutError as e:
            sflags[1] = 1
        except queue.Empty as e:
            sflags[1] = 1
        else:
            sflags[1] = 0

        if sflags == [1, 1]:
            log.ok("Processing Complete!")
            break

        # Sometimes processes die (due to errors, or exit called), which
        # will slowly starve the script as they are not restarted. The below
        # filters out dead processes, allowing us to respawn as necessary
        ap = [x for x in ap if x.isAlive()]

    # Now wait for all running processes to complete
    log.info("Waiting for all running process to complete.")

    # We don't use os.join because if a child hangs, it takes the entire program
    # with it
    st = time.time()
    while True:

        if len([x for x in ap if x.is_alive()]) == 0:
            break
        log.info("-" * 80)
        for proc in [x for x in ap if x.is_alive()]:
            log.warn("\"%s\" is still running! Waiting..." % proc.name)
            log.info("-" * 80)
        time.sleep(4)
        log.info("")
        if (time.time() - st) > 600:
            log.crit("Process timeout reached, terminating stragglers and continuing\
            anyway")
            list(map(lambda x: x.terminate(), [x for x in ap if x.is_alive()]))
            break

    end_time = time.time()
    # Now we fetch the log results, for the summary
    log.info("Processing run log...")
    result_log = []
    while not lQ.empty():
        result_log.append(lQ.get(timeout=2))

    failures = generate_summary(start_time, end_time, len(files), result_log, opts['outdir'])

    if failures != 0:
        log.crit("We had some failures in encoding :-(")
        log.crit("Check conversion log file for info.")
        log.crit("Done! Returning non-zero exit status! ")
        sys.exit(-1)
    else:
        sys.exit(0)
