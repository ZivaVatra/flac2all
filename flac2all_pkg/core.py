# -*- coding: utf-8 -*-
# vim: ts=4 ai expandtab

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

try:
	from aac import aacplus
	from vorbis import vorbis
	from flac import flac
	from mp3 import lameMp3 as mp3
	from opus import opus
	from ffmpeg import ffmpeg
	from shell import filecopy
	from logging import console
except ImportError:
	from .aac import aacplus
	from .vorbis import vorbis
	from .flac import flac
	from .mp3 import lameMp3 as mp3
	from .opus import opus
	from .ffmpeg import ffmpeg
	from .shell import filecopy
	from .logging import console

import threading as mt

import os
import queue
import signal
import time


import uuid

# Todo, make this something we can pass from __init__
log = console(stderr=True)


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
    ["_copy", "Copy non flac files across"]
]
# Add the ffmpeg codecs to the modetable, we prefix "f:", so end user knows to use the ffmpeg
# options
modetable.extend([["f:" + x[0], x[1]] for x in ffmpeg(None, None).codeclist()])


# functions
def signal_handler(signal, frame):
    global terminate, log
    log.info("Caught signal: %s" % signal)
    terminate = True


def print_summary(count, total, percentage_execution_rate, successes, failures, percentage_fail, modes):
    out = "\n\n"
    out += ("=" * 80)
    out += "| Summary "
    out += ("-" * 80)
    out += """
Total files on input: %d
Total files actually processed: %d
--
Execution rate: %.2f%%
Files we managed to convert successfully: %d
Files we failed to convert due to errors: %d
--
Conversion error rate: %.2f%%
""" % (count, total, (
        percentage_execution_rate,
        successes,
        failures,
        (percentage_fail)
    ))
    for mode in modes:
        execT, esum, emean, emedian = modes[mode]
        log.print("For mode: " + mode)
        etime = ""
        if esum < 600:
            etime += "%.4f seconds" % esum
        elif esum > 600 < 3600:
            etime += "%.4f minutes" % (esum / 60)
        else:
            etime += "%.4f hours" % (esum / 60 / 60)
        out += "\tTotal execution time: %s" % etime
    out += """
Per file conversion:
\tMean execution time: %.4f seconds
\tMedian execution time: %.4f seconds
""" % (emean, emedian)

    return out


def generate_summary(start_time, end_time, count, results):
    total = len(results)
    successes = len([x for x in results if int(x[4]) == 0])
    failures = total - successes
    if total != 0:
        percentage_fail = (failures / float(total)) * 100
    else:
        percentage_fail = 0

    percentage_execution_rate = (float(total) / count) * 100

    # Each result provides the mode, so we can build a set of modes
    # from this
    modes = set([x[2] for x in results])
    moderesult = {}

    for mode in list(modes):
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
            esum = 0
            emean = 0
        execT.sort()
        if len(execT) % 2 != 0:
            # Odd number, so median is middle
            emedian = execT[int((len(execT) - 1) / 2)]
        else:
            # Even set. So median is average of two middle numbers
            num1 = execT[int((len(execT) - 1) / 2) - 1]
            num2 = execT[int(((len(execT) - 1) / 2))]
            emedian = (sum([num1, num2]) / 2.0)
        moderesult.update({mode: [execT, esum, emean, emedian]})

    total_execution_time = (end_time - start_time)
    return (
        total,
        successes,
        failures,
        moderesult,
        percentage_fail,
        total_execution_time,
        percentage_execution_rate
    )


def write_logfile(outdir, results):
    errout_file = outdir + "/conversion_results.log"
    log.info("Writing log file (%s)" % errout_file)
    fd = open(errout_file, "w")
    fd.write(
        "infile,outfile,format,conversion_status,return_code,execution_time\n"
    )
    for item in results:
        item = [str(x) for x in item]
        line = ','.join(item)
        fd.write("%s\n" % line.encode("utf-8", "backslashreplace"))
    fd.close()
    log.print("Done!")


# Classes

class ModeException(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        msg = "ERROR: Not understanding mode '%s' is mode valid?" % msg
        print(msg)


class transcoder():
    def __init__(self):
        pass

    def modeswitch(self, mode, opts):
        if mode == "mp3":
            encoder = mp3(opts['lameopts'])
        elif mode == "ogg" or mode == "vorbis":
            encoder = vorbis(opts['oggencopts'])
        elif mode == "aacplus":
            encoder = aacplus(opts['aacplusopts'])
        elif mode == "opus":
            encoder = opus(opts['opusencopts'])
        elif mode == "flac":
            encoder = flac(opts['flacopts'])
        elif mode == "test":
            pass  # 'test' is special as it isn't a converter, it is handled below
        elif mode == "_copy":
            encoder = filecopy(opts)
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
            raise(ModeException(mode))
#            return [
#                infile,
#                outfile,
#                mode,
#                1,
#                -1
#            ]

        outfile = outfile.replace('.flac', '')
        # We are moving to a global handler for overwrite, so this is being moved
        # out of the modules (which will from now only deal with the encode)
        # and put here

        # Some codec names do not match its extension, so we have to have extra logic for it
        if mode == "vorbis":
            extension = "ogg"
        elif mode == "aacplus":
            extension = "aac"
        else:
            extension = mode

        test_outfile = outfile + "." + extension.lower()

        if os.path.exists(test_outfile):
            if opts['overwrite'] is False:
                # return code is 0 because an existing file is not an error
                return [infile, outfile, mode, "Outfile exists, skipping", 0, -1]
            else:
                # If the file exists and overwrite is true, unlink it here
                os.unlink(test_outfile)

        log.info("Processing: \t%-40s  target: %-8s " % (
            infile.split('/')[-1],
            mode
        ))
        return encf(infile, outfile)


class encode_worker(transcoder):
    def __init__(self, host_target):
        assert has_zmq is True, "No ZeroMQ module importable. Cannot use clustered mode"
        transcoder.__init__(self)

        # We need a worker ID
        self.worker_id = str(uuid.uuid4())
        # 1. Set up the zmq context to receive tasks
        self.zcontext = zmq.Context()
        signal.signal(signal.SIGINT, signal_handler)

        # Task socket, recieves tasks
        self.tsock = self.zcontext.socket(zmq.PULL)
        self.tsock.connect("tcp://%s:2019" % host_target)

        # Comm socket, for communicating with task server
        self.csock = self.zcontext.socket(zmq.PUSH)
        self.csock.connect("tcp://%s:2020" % host_target)

    def send_json(self, message):
        message[0] = message[0] + '~' + self.worker_id
        self.csock.send_json(message)
        pass

    def run(self):
        global terminate

        # Send ONLINE command indicating we are ready
        self.send_json(["ONLINE"])

        # So, this implementation is driven by the workers. They request
        # work when ready, and we sit and wait until they are ready to
        # send tasks

        # Process tasks until EOL received
        self.send_json(["READY"])
        while True:
            try:
                message = self.tsock.recv_json(flags=zmq.NOBLOCK)
                infile, mode, opts = message
            except zmq.error.Again as e:
                # If we get nothing in 5 seconds, retry sending READY
                time.sleep(5)
                continue
            except ValueError as e:
                log.crit("ERROR, Discarding invalid message: %s (%s)" % (message, e))
                continue

            if infile == "EOL":
                time.sleep(0.1)
                self.send_json(["EOLACK"])
                self.tsock.close()
                self.csock.close()
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
                    self.send_json(result)
                    # tell flac2all master that this node is offline
                    self.send_json(["OFFLINE"])
                    self.csock.close()
                    self.tsock.close()
                    # Exit the loop
                    break
                else:
                    result = self.encode(infile, mode, opts)
            except Exception as e:
                # Perhaps move this to a "cleanup" function, we have repeated the logic above
                # Send NACK, so the job gets sent to another worker (who may be able to do it)
                self.send_json(["NACK", infile, mode, opts])
                # Then send message taking this worker offline
                result = ["OFFLINE", infile, "", mode, "ERROR:GLOBAL EXCEPTION:%s" % str(e).encode("utf-8"), -1, -1]
                self.send_json(result)
                self.csock.close()
                self.tsock.close()
                raise(e)
            # We send the result back up the chain
            self.send_json(result)
            # If we reach this point, means nothing messed up, and we can send READY command
            self.send_json(["READY"])


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
