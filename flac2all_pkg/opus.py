# vim: ts=4 ai expandtab

import os
import re

from time import time
from flac import flacdecode
from config import ipath
import subprocess as sp
import uuid

# Class that deals with the opus codec


class opus:
    def __init__(self, opusencopts):
        # Work out what version of opus we have
        self.version = None  # Undefined by default

        # Opus is really all over the place, each version has different
        # switches. I guess that is what happens with new stuff
        try:
            data = sp.check_output([
                os.path.join(ipath.opusencpath, "opusenc"), "-V"
            ]).decode("utf-8")
        except sp.CalledProcessError:
            data = sp.check_output([
                os.path.join(ipath.opusencpath, "opusenc"), "-v"
            ]).decode("utf-8")

        data = re.search("\d\.\d\.\d", data).group(0)
        (release, major, minor) = [int(x) for x in data.split('.')]
        self.version = (release, major, minor)
        self.opts = opusencopts

    def opusConvert(self, infile, outfile, logq):
        # As the new versions of opus support flac natively, I think that the
        # best option is to
        # use >0.1.7 by default, but support earlier ones without tagging.
        startTime = time()

        if self.version is None:
            print("ERROR! Could not discover opus version, assuming version >=\
                0.1.7. THIS MAY NOT WORK!")
            version = (9, 9, 9)
        else:
            version = self.version

        # If we are a release prior to 0.1.7, use non-tagging type conversion,
        # with warning
        result = None
        if (version[0] == 0) and (version[1] <= 1) and (version[2] <= 6):
            print("WARNING: Opus version prior to 0.1.7 detected,\
                NO TAGGING SUPPORT")
            pipe = "/tmp/flac2all_%s" % str(uuid.uuid4()).strip()
            (_, decode_stderr) = flacdecode(infile, pipe)()
            try:
                proc = sp.Popen([
                    "%sopusenc" % ipath.opusencpath,
                    "%s" % self.opts,
                    pipe,
                    "%s.opus" % outfile,
                ], stdout=sp.PIPE, stderr=sp.PIPE)
            except sp.CalledProcessError as e:
                rc = -1  # This triggers the error function below

            enc_stdout, enc_stderr = proc.communicate()
            rc = proc.wait()  # wait for encoding to finish
            os.unlink(pipe)
            decode_errline = decode_stderr.read().decode('utf-8')
            decode_errline = decode_errline.upper()
            encode_errline = enc_stderr.decode('utf-8')
            if decode_errline.strip() != '':
                print("ERRORLINE: %s" % decode_errline)
            if decode_errline.find("ERROR") != -1 or rc != 0:
                logq.put([
                    infile,
                    "mp3",
                    "ERROR: decoder error: '%s', encoder error: '%s'" % (
                        decode_errline,
                        encode_errline
                    ),
                    -1,
                    str(time() - startTime),
                ], timeout=10)
                return False

            result = "SUCCESS_NOTAGGING"
        else:
            # Later versions support direct conversion from flac->opus, so no
            # need for the above.
            cmd = [
                "%sopusenc" % ipath.opusencpath,
                "--quiet",
            ]
            if self.opts.strip() != "":
                cmd.extend([x for x in self.opts.split(' ') if x.strip() != ""])

            cmd.extend([infile, "%s.opus" % (outfile)])

            try:
                rc = sp.check_call(cmd)
                result = "SUCCESS"
            except sp.CalledProcessError as e:
                    rc = e.returncode
                    result = "ERROR: opusenc error '%s'. Could not convert" % (
                        e.message
                    )
        logq.put([
            infile,
            outfile,
            "opus",
            result,
            rc,
            time() - startTime
        ])
