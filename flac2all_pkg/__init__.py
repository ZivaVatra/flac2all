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


from shell import shell

import multiprocessing as mp
from optparse import OptionParser
from config import opts
from core import modetable, generate_summary
from multiprocess_encode import encode as threaded_encode

import sys
import os
import time
import signal

terminate = False

from logging import console

log = console(stderr=True)


def signal_handler(signal, frame):
    global terminate
    log.info("Caught signal: %s" % signal)
    terminate = True


signal.signal(signal.SIGINT, signal_handler)

here = os.path.abspath(os.path.dirname(__file__))

if os.path.exists(os.path.join(here, "version")):
    with open(os.path.join(here, "version"), 'r') as fd:
        version = fd.read().strip()
else:
    version = "DEVELOPMENT"

# error handling
modeError = Exception("Error understanding mode. Is mode valid?")


def flatten(iterable):
    try:
        iterator = iter(iterable)
    except TypeError:
        yield iterable
    else:
        for element in iterator:
            if type(element) is str:
                yield element
            else:
                yield from flatten(element)


def prog_usage():
    return """
Flac2all python script, %s. Copyright 2003 ziva-vatra
Licensed under the GPLv3 or later. Please see included LICENCE file,
or visit http://www.gnu.org/licenses/gpl.txt for the full licence.

Dev website: https://github.com/ZivaVatra/flac2all

\tUsage: %s enctype1[,enctype2..] [options]  inputdir

\tValid encode types are as follows:\n\t\t%s
\tYou can specify multiple encode targets with a comma seperated list.

""" % (version, sys.argv[0], "\n\t\t".join([x[0] for x in modetable if not x[0].startswith("_")]))


def clustered_encode():
    sh = shell()
    # Here we do the clustering magic

    # This is here rather than at the top as is usual so that flac2all can work
    # even if ZeroMQ is not installed. Perhaps in future zmq will become a hard
    # dependency, and then we can move it.
    import zmq

    zcontext = zmq.Context()

    # Task socket (to send tasks out)
    tsock = zcontext.socket(zmq.PUSH)
    tsock.bind("tcp://*:2019")

    # recieve socket (gets results from workers)
    rsock = zcontext.socket(zmq.PULL)
    rsock.bind("tcp://*:2020")

    # connect loopback to recieve socket
    csock = zcontext.socket(zmq.PUSH)
    csock.connect("tcp://localhost:2020")

    # Gathering file data
    files = sh.getfiles(opts['dirpath'])
    inlist = []
    for infile in files:
        for mode in opts['mode'].split(','):
            if mode.startswith("_"):
                # This should never happen unless some smart-alec tries to call
                # a private mode publicly, but just in case
                continue
            if not infile.endswith(".flac"):
                if opts['copy'] is True:
                    line = [infile, "_copy", opts]
                    inlist.append(line)
            else:
                line = [infile, mode, opts]
                inlist.append(line)

    incount = len(inlist)
    log.info("We have %d tasks" % incount)
    start_time = time.time()
    workers = []
    log.info("Waiting for at least one worker to join")
    results = []

    while True:
        if terminate is True:
            # If we want to terminate, clear the entire inlist
            # This will clean up the same as when we end normally
            inlist = []

        try:
            line = rsock.recv_json(flags=zmq.NOBLOCK)
        except zmq.error.Again as e:
            # errno 11 is "Resource temporarily unavailable"
            # We expect this if no data, so we sit in a loop and wait
            if (e.errno == 11):
                if terminate is True:
                    rsock.close()
                    csock.close()
                    rsock.close()
                    sys.exit(0)
                time.sleep(0.01)  # wait a little bit and try again
                continue
            else:
                raise(e)  # re-raise other errnos

        if line[0].startswith('ONLINE'):
            worker_id = line[0].split('~')[-1]
            # A worker has joined. Add the ID and timestamp of last seen
            workers.append({worker_id: time.time()})
            log.ok("Got %d worker(s)" % len(workers))
        elif line[0].startswith('EOLACK'):
            worker_id = line[0].split('~')[-1]
            if worker_id in workers:
                del(workers[worker_id])
            log.warn("Worker %s terminated (%d running)" % (worker_id, len(workers)))
            if len(workers) == 0:
                break
        elif line[0].startswith('OFFLINE'):
            worker_id = line[0].split('~')[-1]
            if worker_id in workers:
                del(workers[worker_id])

            log.crit("Worker %s gone OFF LINE (%d running)" % (worker_id, len(workers)))
            if len(workers) == 0:
                break

        elif line[0].startswith("READY"):
            # A worker is ready for a new task, so push it
            if len(inlist) == 0:
                # We have reached the end. Send EOL
                tsock.send_json(["EOL", None, None])
                continue
            else:
                # Pop a job off the list and send to worker as task
                tsock.send_json(inlist.pop())
        elif line[0].startswith("NACK"):
            worker_id = line[0].split('~')[-1]
            log.warn("Task '%s' refused by worker %s, rescheduling" % (line[2], worker_id))
            # For whatever reason the worker is refusing the task, so
            # put it back onto the inlist for another worker to do
            inlist.append(line[1:])
        elif len(line) == 6:
            name = line[0].split('/')[-1]
            name = name.replace(".flac", "")
            if len(name) > 55:
                name = name[:55] + "..."
            line = [str(x).strip() for x in line]
            log.status("n:%-60s\tt:%-10s\ts:%-10s" % (name.encode("utf-8", "backslashreplace").decode(), line[2], line[3]))
            results.append(line)
        else:
            log.crit("UNKNOWN RESULT!")
            log.crit(results)

    end_time = time.time()
    rsock.close()
    csock.close()
    rsock.close()

    # Now, we confirm that the number of files sent equals the number processed
    log.info("input: %d, output: %d" % (incount, len(results)))
    assert incount == len(results), "Execution failure. Not all tasks were completed."
    # log.print(list(set([x[0] for x in inlist]) - set([x[0] for x in results])))
    generate_summary(start_time, end_time, incount, results, opts['outdir'])


def build_parser():
    # I've decided that the encoder options should just be long options.
    # quite frankly, we are running out of letters that make sense.
    # plus it makes a distinction between encoder opts, and program opts
    # (which will continue to use single letters)
    parser = OptionParser(usage=prog_usage())
    parser.add_option(
        "-c", "--copy", action="store_true", dest="copy",
        default=False, help="Copy non flac files across (default=False)"
    )
    parser.add_option(
        "", "--ffmpeg-options", dest="ffmpegopts",
        default="-b:a 128k", help="Comma delimited options to pass to ffmpeg. Exact options will vary based on which of the ffmpeg codecs you are using"
    )

    parser.add_option(
        "", "--opus-options", dest="opusencopts",
        default="vbr", help="Colon delimited options to pass to opusenc.\
        Any oggenc long option (one with two '--' in front) can be specified\
        in the above format."
    )

    parser.add_option(
        "", "--vorbis-options", dest="oggencopts",
        default="quality=2", help="Colon delimited options to pass to oggenc,for\
        example: 'quality=5:resample 32000:downmix:bitrate_average=96'.\
        Any oggenc long option (one with two '--' in front) can be specified\
        in the above format."
    )

    parser.add_option(
        "", "--lame-options", dest="lameopts",
        default="-preset standard:q 0", help="Options to pass to lame,\
for example:           '-preset extreme:q 0:h:-abr'. Any lame\
option can be specified here, if you want a short option (e.g. -h),\
then just do 'h'. If you want a long option (e.g. '--abr'), then you need\
a dash: '-abr'"
    )

    parser.add_option(
        "-o", "--outdir", dest="outdir", metavar="DIR",
        help="Set custom output directory (default='./')",
        default="./"
    )

    parser.add_option(
        "-f", "--force", dest="overwrite", action="store_true",
        help="Force overwrite of existing files (by default we skip)",
        default=False
    )

    parser.add_option(
        "-t", "--threads", dest="threads", default=mp.cpu_count(),
        help="How many threads to run in parallel (default: autodetect\
    [found %d cpu(s)] )" % mp.cpu_count()
    )

    parser.add_option(
        "-n", "--nodirs", dest="nodirs", action="store_true",
        default=False, help="Don't create Directories, put everything together"
    )

    parser.add_option(
        "-m", "--master", dest="master_enable", action="store_true",
        default=False, help="Start flac2all in master mode (for clustering)."
    )

    (options, args) = parser.parse_args()
    return (options, args)


def main():
    options, args = build_parser()

    # update the opts dictionary with new values
    opts.update(eval(options.__str__()))

    # convert the formats in the args to valid formats for lame and oggenc
    opts['oggencopts'] = ' --' + ' --'.join(opts['oggencopts'].split(':'))
    opts['opusencopts'] = ' --' + ' --'.join(opts['opusencopts'].split(':'))

    # lame is not consistent, sometimes using long opts,sometimes not
    # so we need to specify on command line with dashes whether it is a long op or
    # short
    opts['lameopts'] = ' -' + ' -'.join(opts['lameopts'].split(':'))

    # ffmpeg uses colons as delimiters, just like flac2all (of course), so we had to
    # switch to commas for this one
    opts['ffmpegopts'] = opts['ffmpegopts'].split(',')
    opts['ffmpegopts'] = list(flatten([x.split(' ') for x in opts['ffmpegopts']]))

    try:
        opts['mode'] = args[0]

    except(IndexError):  # if no arguments specified
        log.print("No mode specified! Run with '-h' for help")
        sys.exit(1)  # quit the program with non-zero status

    try:
        opts['dirpath'] = os.path.abspath(args[1])

    except(IndexError):
        log.print("No directory specified! Run with '-h' for help")
        sys.exit(2)  # quit the program with non-zero status

    # end command line checking

    if not os.path.exists(opts['outdir']):
        log.info("Creating output directory")
        os.mkdir(opts['outdir'])

    # Check if we have the special mode "all", which really brings flac2all into
    # perspective. We convert to every single format supported. This is mainly added for
    # testing reasons.
    if opts['mode'] == "all":
        opts['mode'] = ','.join([x[0] for x in modetable if not x[0].startswith("_")])

    # In this version, we can convert multiple format at once, so for e.g.
    # mode = mp3,vorbis will create both in parallel
    for mode in opts['mode'].split(','):
        if mode != "":
            try:
                os.mkdir(os.path.join(opts['outdir'], mode))
            except OSError as e:
                if e.errno == 17:
                    log.info("Folder %s already exists, reusing..." % mode)
                elif e.errno == 2:
                    log.info("Parent path %s does not exist! quitting..." % (
                        opts['outdir']
                    ))
                else:
                    # everything else, raise error
                    raise e

    # Magic goes here :)
    if opts['master_enable']:
        clustered_encode()
    else:
        threaded_encode()


if __name__ == "__main__":
    main()
