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
import time

try:
    import zmq
except ImportError:
    has_zmq = False
else:
    has_zmq = True

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

    def run(self, host_target):
        # Task socket, recieves tasks
        tsock = self.zcontext.socket(zmq.PULL)
        tsock.connect("tcp://%s:2019" % host_target)

        # Comm socket, for communicating with task server
        csock = self.zcontext.socket(zmq.PUSH)
        csock.connect("tcp://%s:2020" % host_target)

        # Send EHLO command indicating we are ready
        csock.send_json(["EHLO"])

        # Process tasks until EOL received
        while True:
            infile, mode, opts = tsock.recv_json()
            if infile == "EOL":
                time.sleep(0.1)
                csock.send_json(["EOLACK"])
                tsock.close()
                csock.close()
                return 0

            # We send the result back up the chain
            try:
                result = self.encode(infile, mode, opts)
            except Exception as e:
                result = [infile, "", mode, "ERROR:GLOBAL EXCEPTION:%s" % str(e).encode("utf-8"), -1, -1]
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
