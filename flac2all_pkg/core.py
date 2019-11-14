# -*- coding: utf-8 -*-
# vim: ts=4 ai expandtab

from aac import aacplus
from vorbis import vorbis
from flac import flac
from mp3 import lameMp3 as mp3
from opus import opus
from ffmpeg import ffmpeg

import threading as mt

import os
import queue
import signal
import time

try:
    import zmq
except ImportError:
    has_zmq = False
else:
    has_zmq = True

# If we want to refuse tasks, this global controls it
# e.g. we ctrl-c, and want to empty the worker before a
# clean terminate
refuse_tasks = False
terminate = False

modeError = Exception("Error understanding mode. Is mode valid?")
# The modetable holds all the "modes" (read: formats we can convert to), in the format:
# [ "codec_name", "description" ]. The codec name is what the end_user will issue to
# flac2all as a mode command, so no spaces, or other special characters, and we will
# keep it lowercase
modetable = [
    ["mp3", "Lame mp3 encoder"],
    ["vorbis", "Ogg vorbis encoder"],
    ["aacplus", "aac-enc encoder"],
    ["opus", "Opus Encoder"],
    ["flac", "FLAC encoder"],
    ["test", "FLAC testing procedure"],
]
# Add the ffmpeg codecs to the modetable, we prefix "f:", so end user knows to use the ffmpeg
# options
modetable.extend([["f:" + x[0], x[1]] for x in ffmpeg(None, None).codeclist()])


# functions
def signal_handler(signal, frame):
    global terminate
    print("Caught signal: %s" % signal)
    terminate = True


def generate_summary(start_time, end_time, count, results, outdir):
    total = len(results)
    successes = len([x for x in results if int(x[4]) == 0])
    failures = total - successes
    if total != 0:
        percentage_fail = (failures / float(total)) * 100
    else:
        percentage_fail = 0

    print("\n\n")
    print("=" * 80)
    print("| Summary ")
    print("-" * 80)
    print("""
Total files on input: %d
Total files actually processed: %d
--
Execution rate: %.2f%%
Files we managed to convert successfully: %d
Files we failed to convert due to errors: %d
--
Conversion error rate: %.2f%%
""" % (count, total, (
        (float(total) / count) * 100),
        successes,
        failures,
        (percentage_fail)
       ))

    # Each result provides the mode, so we can build a set of modes
    # from this
    modes = set([x[2] for x in results])

    for mode in modes:
        # 1. find all the logs corresponding to a particular mode
        x = [x for x in results if x[2] == mode]
        # 2. Get the execution time for all relevant logs.
        #    -1 times are events which were no-ops (either due to errors or
        #    file already existing when overwrite == false), and are filtered out
        execT = [float(y[5]) for y in x if float(y[5]) != -1]
        if len(execT) != 0:
            esum = sum(execT)
            emean = sum(execT) / len(execT)
        else:
            # Empty set, just continue
            print(("For mode %s:\nNo data (no files converted)\n" % mode))
            continue
        execT.sort()
        if len(execT) % 2 != 0:
            # Odd number, so median is middle
            emedian = execT[int((len(execT) - 1) / 2)]
        else:
            # Even set. So median is average of two middle numbers
            num1 = execT[int((len(execT) - 1) / 2) - 1]
            num2 = execT[int(((len(execT) - 1) / 2))]
            emedian = (sum([num1, num2]) / 2.0)

        etime = "Total execution time: "
        if esum < 600:
            etime += "%.4f seconds" % esum
        elif esum > 600 < 3600:
            etime += "%.4f minutes" % (esum / 60)
        else:
            etime += "%.4f hours" % (esum / 60 / 60)

        print("""
For mode: %s
%s
Per file conversion:
\tMean execution time: %.4f seconds
\tMedian execution time: %.4f seconds
""" % (mode, etime, emean, emedian))

    print("Total execution time: %.2f seconds" % (end_time - start_time))
    errout_file = outdir + "/conversion_results.log"
    print("Writing log file (%s)" % errout_file)
    fd = open(errout_file, "w")
    fd.write(
        "infile,outfile,format,conversion_status,return_code,execution_time\n"
    )
    for item in results:
        item = [str(x) for x in item]
        line = ','.join(item)
        fd.write("%s\n" % line.encode("utf-8", "backslashreplace"))
    fd.close()
    print("Done!")
    return failures


# Classes
class transcoder():
    def __init__(self):
        pass

    def modeswitch(self, mode, opts):
        if mode == "mp3":
            encoder = mp3(opts)
        elif mode == "ogg" or mode == "vorbis":
            encoder = vorbis(opts)
        elif mode == "aacplus":
            encoder = aacplus(opts['aacplusopts'])
        elif mode == "opus":
            encoder = opus(opts['opusencopts'])
        elif mode == "flac":
            encoder = flac(opts['flacopts'])
        elif mode == "test":
            pass  # 'test' is special as it isn't a converter, it is handled below
        elif mode[0:2] == "f:":
            encoder = ffmpeg(opts, mode[2:])  # Second argument is the codec
        else:
            return None
        if mode == "test":
            encoder = flac(opts['flacopts'])
            encf = encoder.flactest
        else:
            encf = encoder.convert
        return encf

    def encode(self, infile, mode, opts):
        # Return format:
        # [¬
        #   $infile,¬
        #   $outfile,¬
        #   $format,¬
        #   $error_status,¬
        #   $return_code,¬
        #   $execution_time¬
        # ]
        outfile = infile.replace(opts['dirpath'], os.path.join(opts['outdir'], mode))
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

        encf = self.modeswitch(mode, opts)
        if encf is None:
            return [
                infile,
                outfile,
                mode,
                "ERROR: Not understanding mode '%s' is mode valid?" % mode,
                1,
                -1
            ]

        outfile = outfile.replace('.flac', '')
        if opts['overwrite'] is False:
            if os.path.exists(outfile + "." + mode):
                # return code is 0 because an existing file is not an error
                return [infile, outfile, mode, "SUCCESS:EXISTS, skipping", 0, -1]
        print("Converting: \t %-40s  target: %8s " % (
            infile.split('/')[-1],
            mode
        ))
        return encf(infile, outfile)


class encode_worker(transcoder):
    def __init__(self):
        assert has_zmq is True, "No ZeroMQ module importable. Cannot use clustered mode"
        transcoder.__init__(self)
        # 1. Set up the zmq context to receive tasks
        self.zcontext = zmq.Context()
        signal.signal(signal.SIGINT, signal_handler)

    def run(self, host_target):
        global terminate

        # Task socket, recieves tasks
        tsock = self.zcontext.socket(zmq.PULL)
        tsock.connect("tcp://%s:2019" % host_target)

        # Comm socket, for communicating with task server
        csock = self.zcontext.socket(zmq.PUSH)
        csock.connect("tcp://%s:2020" % host_target)

        # Send ONLINE command indicating we are ready
        csock.send_json(["ONLINE"])

        # So, this implementation is driven by the workers. They request
        # work when ready, and we sit and wait until they are ready to
        # send tasks

        # Process tasks until EOL received
        while True:
            csock.send_json(["READY"])
            try:
                message = tsock.recv_json(flags=zmq.NOBLOCK)
                infile, mode, opts = message
            except zmq.error.Again as e:
                # If we get nothing in 5 seconds, retry sending READY
                time.sleep(5)
                continue
            except ValueError as e:
                print("ERROR, invalid message: %s (%s)" % (message, e))
                continue

            if infile == "EOL":
                time.sleep(0.1)
                csock.send_json(["EOLACK"])
                tsock.close()
                csock.close()
                return 0

            try:
                if refuse_tasks is True:
                    result = ["NACK"]
                    # Send the task back, to be done by another
                    # worker
                    result.extend([infile, mode, opts])
                elif terminate is True:
                    result = ["NACK"]
                    # Send the task back, to be done by another
                    # worker
                    result.extend([infile, mode, opts])
                    csock.send_json(result)
                    # tell flac2all master that this node is offline
                    csock.send_json(["OFFLINE"])
                    csock.close()
                    tsock.close()
                    # Exit
                    raise(SystemExit(0))
                else:
                    result = self.encode(infile, mode, opts)
            except Exception as e:
                # Perhaps move this to a "cleanup" function, we have repeated the logic above
                result = ["NACK", infile, "", mode, "ERROR:GLOBAL EXCEPTION:%s" % str(e).encode("utf-8"), -1, -1]
                csock.send_json(result)
                csock.send_json(["OFFLINE"])
                csock.close()
                tsock.close()
                # Finally, raise exception
                raise(e)
            # We send the result back up the chain
            csock.send_json(result)


class encode_thread(mt.Thread, transcoder):
    def __init__(self, threadID, name, taskq, opts, logq):
        mt.Thread.__init__(self)
        transcoder.__init__(self)
        self.threadID = threadID
        self.name = name
        self.taskq = taskq
        self.opts = opts
        self.logq = logq

    def run(self):
        while not self.taskq.empty():
            try:
                # Get the task, with one minute timeout
                task = self.taskq.get(timeout=60)
            except queue.Empty:
                # No more tasks after 60 seconds, we can quit
                return True

            infile = task[0]
            mode = task[3].lower()
            self.logq.put(self.encode(infile, mode, self.opts), timeout=10)
