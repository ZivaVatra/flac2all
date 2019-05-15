#!/bin/python2.6
# -*- coding: utf-8 -*-
# vim: ts=4 ai expandtab

#    flac2all: Multi process flac converter
#       -  https://github.com/ZivaVatra/flac2all/
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


from aac import aacplusNero, aacplus
from vorbis import vorbis
from flac import flac
from mp3 import lameMp3 as mp3
from shell import shell
from opus import opus

import multiprocessing as mp
import threading as mt
from shutil import copy as copytarget
from optparse import OptionParser
from config import opts

import sys
import os
import time
import Queue

here = os.path.abspath(os.path.dirname(__file__))

if os.path.exists(os.path.join(here, "version")):
    with open(os.path.join(here, "version"), 'r') as fd:
        version = fd.read().strip()
else:
    version = "v4"

# error handling
modeError = Exception("Error understanding mode. Is mode valid?")


def prog_usage():
    return """
Flac2all python script, %s. Copyright 2003 ziva-vatra
Licensed under the GPLv3 or later. Please see included LICENCE file,
or visit http://www.gnu.org/licenses/gpl.txt for the full licence.

Dev website: https://github.com/ZivaVatra/flac2all

\tUsage: %s enctype1[,enctype2..] [options]  inputdir

\tValid encode types are as follows: %s
\tYou can specify multiple encode targets with a comma seperated list.

""" % (version, sys.argv[0], "mp3 vorbis aacplusnero opus flac test")


# Classes
class encode_thread(mt.Thread):
    def __init__(self, threadID, name, taskq, opts, logq):
        mt.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.taskq = taskq
        self.opts = opts
        self.logq = logq

    def run(self):
        taskq = self.taskq
        opts = self.opts
        logq = self.logq
        while not taskq.empty():
            try:
                # Get the task, with one minute timeout
                task = taskq.get(timeout=60)
            except Queue.Empty:
                # No more tasks after 60 seconds, we can quit
                return True

            mode = task[3].lower()
            if mode == "vorbis":
                mode = "ogg"

            infile = task[0]
            outfile = task[0].replace(task[1], os.path.join(task[2], task[3]))
            outpath = os.path.dirname(outfile)
            try:
                if not os.path.exists(outpath):
                    os.makedirs(outpath)
            except OSError as e:
                # Error 17 means folder exists already. We can reach this
                # despite the check above, due to a race condition when a
                # bunch of spawned processes all try to mkdir at once.
                # So if Error 17, continue, otherwise re-raise the exception
                if e.errno != 17:
                    raise(e)

            if mode == "mp3":
                encoder = mp3(opts['lameopts'])
                encf = encoder.mp3convert
            elif mode == "ogg":
                encoder = vorbis(opts['oggencopts'])
                encf = encoder.oggconvert
            elif mode == "aacplus":
                encoder = aacplus(opts['aacplusopts'])
                encf = encoder.AACPconvert
            elif mode == "aacplusnero":
                encoder = aacplusNero(opts['neroaacplusopts'])
                encf = encoder.AACPconvert
            elif mode == "opus":
                encoder = opus(opts['opusencopts'])
                encf = encoder.opusConvert
            elif mode == "flac":
                encoder = flac(opts['flacopts'])
                encf = encoder.flacConvert
            elif mode == "test":
                encoder = flac() # We don't need any opts for testing
                encf = encoder.flactest
            else:
                logq.put([
                    infile,
                    outfile,
                    mode,
                    "ERROR: Not understanding mode '%s' is mode valid?" % mode,
                    1,
                    0
                ])
                raise modeError

            outfile = outfile.replace('.flac', '')
            if opts['overwrite'] is False:
                if os.path.exists(outfile + "." + mode):
                    print("Output file already exists, skipping")
                    continue

            print("Converting: \t %-40s  target: %8s" % (
                task[0].split('/')[-1],
                task[3]
            ))
            encf(infile, outfile, logq)


def main():
    sh = shell()

    # process Queue,the queue that will hold all the flac files we want to convert.
    #  format: [ $infile, $target_format ]
    pQ = mp.Queue()

    # copy Queue (for copying non flac files if requested)
    #  format: [ $infile, $outfile ]
    cQ = mp.Queue()

    # logging Queue, the encoders log progress to this
    # format: [
    #   $infile,
    #   $outfile,
    #   $format,
    #   $error_status,
    #   $return_code,
    #   $execution_time
    #   ]
    lQ = mp.Queue()

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
        "", "--opus-options", dest="opusencopts",
        default="", help="Colon delimited options to pass to opusenc.\
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
        "", "--aacplus-options", dest="neroaacplusopts",
        default="q 0.3", help="Nero AACplus options, valid options is one of:\
    Quality (q $float), bitrate (br $int), or streaming bitrate (cbr $int) "
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

    (options, args) = parser.parse_args()

    # update the opts dictionary with new values
    opts.update(eval(options.__str__()))

    # convert the formats in the args to valid formats for lame and oggenc
    opts['oggencopts'] = ' --' + ' --'.join(opts['oggencopts'].split(':'))
    opts['opusencopts'] = ' --' + ' --'.join(opts['opusencopts'].split(':'))

    # Nero codec is annoying, as it takes bitrate in actual bits/s, rather than
    # kbit/s as every other codec on earth works. So we need to parse things out
    # and convert

    enctype, rate = opts['neroaacplusopts'].split(' ')
    if enctype == "br" or enctype == "cbr":
        opts['neroaacplusopts'] = ' -%s %d' % (enctype, int(rate) * 1000)
    else:
        opts['neroaacplusopts'] = ' -%s %s' % (enctype, rate)

    # lame is not consistent, sometimes using long opts,sometimes not
    # so we need to specify on command line with dashes whether it is a long op or
    # short
    opts['lameopts'] = ' -' + ' -'.join(opts['lameopts'].split(':'))

    try:
        opts['mode'] = args[0]

    except(IndexError):  # if no arguments specified
        print("No mode specified! Run with '-h' for help")
        sys.exit(1)  # quit the program with non-zero status

    try:
        opts['dirpath'] = os.path.abspath(args[1])
        print("DEBUG: %s" % opts['dirpath'])

    except(IndexError):
        print("No directory specified! Run with '-h' for help")
        sys.exit(2)  # quit the program with non-zero status

    # end command line checking

    if not os.path.exists(opts['outdir']):
        print("Creating output directory")
        os.mkdir(opts['outdir'])

    # In this version, we can convert multiple format at once, so for e.g.
    # mode = mp3,vorbis will create both in parallel
    for mode in opts['mode'].split(','):
        if mode != "":
            try:
                os.mkdir(os.path.join(opts['outdir'], mode))
            except OSError as e:
                if e.errno == 17:
                    print("Folder %s already exists, reusing..." % mode)
                elif e.errno == 2:
                    print("Parent path %s does not exist! quitting..." % (
                        opts['outdir']
                    ))
                else:
                    # everything else, raise error
                    raise e

    # Magic goes here :)

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

    print "We have %d flac files to convert" % count
    print "We have %d non-flac files to copy across" % cQ.qsize()

    # Right, how this will work here, is that we will pass the whole queue
    # to the encode threads (one per processor) and have them pop off/on as
    # necessary. Allows for far more fine grained control.

    opts['threads'] = int(opts['threads'])

    # keep flags for state (pQ,cQ)
    sflags = [0, 0]
    ap = []  # active processes
    while True:

        cc = opts['threads']

        while int(cc) > (len(ap)):
            print(">> Spawning execution process")
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
            print "Process queue finished."
            sflags[0] = 1
        except Queue.Empty as e:
            print "Process queue finished."
            sflags[0] = 1
        else:
            sflags[0] = 0

        # sflags[1] = 1
        # Commented out until we get the shell_process_thread function written
        #
        try:
            command = cQ.get(timeout=10)
            srcfile, srcroot, dest, encformat = command
            outdir = sh.generateoutdir(srcfile, os.path.join(dest, encformat), srcroot)
            copytarget(srcfile, outdir)
            print("%s => %s" % (srcfile, outdir))
        except mp.TimeoutError as e:
            sflags[1] = 1
        except Queue.Empty as e:
            sflags[1] = 1
        else:
            sflags[1] = 0

        if sflags == [1, 1]:
            print "Processing Complete!"
            break

        # Sometimes processes die (due to errors, or exit called), which
        # will slowly starve the script as they are not restarted. The below
        # filters out dead processes, allowing us to respawn as necessary
        ap = filter(lambda x: x.isAlive(), ap)

    # Now wait for all running processes to complete
    print "Waiting for all running process to complete."
    print ap

    # We don't use os.join because if a child hangs, it takes the entire program
    # with it
    st = time.time()
    while True:

        if len(filter(lambda x: x.is_alive(), ap)) == 0: break
        print "-" * 80
        for proc in filter(lambda x: x.is_alive(), ap):
            print "Process \"%s\" is still running! Waiting..." % proc.name
            print "-" * 80
        time.sleep(4)
        print ""
        if (time.time() - st) > 600:
            print "Process timeout reached, terminating stragglers and continuing\
            anyway"
            map(lambda x: x.terminate(), filter(lambda x: x.is_alive(), ap))
            break

    # Now we fetch the log results, for the summary
    print "Processing run log..."
    log = []
    while not lQ.empty():
        log.append(lQ.get(timeout=2))

    total = len(log)
    successes = len(filter(lambda x: x[4] == 0, log))
    failures = total - successes
    if total != 0:
        percentage_fail = (failures / float(total)) * 100
        execution_rate = (float(total) / count) * 100
    else:
        percentage_fail = 0
        execution_rate = 0
    print "\n\n"
    print "=" * 80
    print "| Summary "
    print "-" * 80
    print """
Total files on input: %d
Total files actually processed: %d
--
Execution rate: %.2f %%


Files we managed to convert successfully: %d
Files we failed to convert due to errors: %d
--
Conversion error rate: %.2f %%
""" % (count,
       total,
       execution_rate,
       successes,
       failures,
       percentage_fail
       )

    for mode in opts['mode'].split(','):
        # 1. find all the logs corresponding to a particular mode
        x = filter(lambda x: x[2] == mode, log)
        # 2. Get the execution time for all relevant logs
        execT = map(lambda y: y[5], x)
        if len(execT) != 0:
            esum = sum(execT)
            emean = sum(execT) / len(execT)
        else:
            # Empty set, just continue
            print("For mode %s:\nNo data (no files converted)\n" % mode)
            continue

        execT.sort()
        if len(execT) % 2 != 0:
            # Odd number, so median is middle
            emedian = execT[(len(execT) - 1) / 2]
        else:
            # Even set. So median is average of two middle numbers
            num1 = execT[((len(execT) - 1) / 2) - 1]
            num2 = execT[((len(execT) - 1) / 2)]
            emedian = (sum([num1, num2]) / 2.0)

        etime = "Total execution time: "
        if esum < 600:
            etime += "%.4f seconds" % esum
        elif esum > 600 < 3600:
            etime += "%.4f minutes" % (esum / 60)
        else:
            etime += "%.4f hours" % (esum / 60 / 60)

        print """
For mode: %s
%s
Per file conversion:
\tMean execution time: %.4f seconds
\tMedian execution time: %.4f seconds
""" % (mode, etime, emean, emedian)

    errout_file = opts['outdir'] + "/conversion_results.log"
    print "Writing log file (%s)" % errout_file
    fd = open(errout_file, "w")
    fd.write(
        "infile,outfile,format,conversion_status,return_code,execution_time\n"
    )
    for item in log:
        item = map(lambda x: str(x), item)
        line = ','.join(item)
        fd.write("%s\n" % line)
    fd.close()
    print "Done!"

    if failures != 0:
        print "We had some failures in encoding :-("
        print "Check %s file for info." % errout_file
        print "Done! Returning non-zero exit status! "
        sys.exit(-1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
