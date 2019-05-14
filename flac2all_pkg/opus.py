# vim: ts=4 ai expandtab

import os
import re

from time import time
from flac import flacdecode
from config import ipath
import subprocess as sp

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
            ])
        except sp.CalledProcessError:
            data = sp.check_output([
                os.path.join(ipath.opusencpath, "opusenc"), "-v"
            ])

        data = re.search("\d+\.\d+\.\d+", data).group(0)
        (release, major, minor) = map(lambda x: int(x), data.split('.'))
        self.version = (release, major, minor)
        self.opts = opusencopts

    def opusConvert(self, infile, outfile, logq):
        # As the new versions of opus support flac natively, I think that the
        # best option is to
        # use >0.1.7 by default, but support earlier ones without tagging.
        startTime = time()

        if self.version is None:
            print "ERROR! Could not discover opus version, assuming version >=\
                0.1.7. THIS MAY NOT WORK!"
            version = (9, 9, 9)
        else:
            version = self.version

        # If we are a release prior to 0.1.7, use non-tagging type conversion,
        # with warning
        result = None
        if (version[0] == 0) and (version[1] <= 1) and (version[2] <= 6):
            print "WARNING: Opus version prior to 0.1.7 detected,\
                NO TAGGING SUPPORT"
            decoder = flacdecode(infile)()
            encoder = sp.Popen([
                "%sopusenc" % ipath.opusencpath,
                "%s" % self.opts,
                "-",
                "%s.opus" % outfile,
            ],
                bufsize=8192,
                stdin=sp.PIPE
            ).stdin

            # while data exists in the decoders buffer
            for line in decoder.readlines():
                encoder.write(line)  # write it to the encoders buffer

                # if there is any data left in the buffer, clear it
                decoder.flush()
                decoder.close()  # somewhat self explanetory

                encoder.flush()  # as above
                encoder.close()
            result = "SUCCESS_NOTAGGING"
        else:
            # Later versions support direct conversion from flac->opus, so no
            # need for the above.
            cmd = [
                "%sopusenc" % ipath.opusencpath,
                "--quiet",
            ]
            if self.opts.strip() != "":
                cmd.extend(filter(
                    lambda x: x.strip() != "", self.opts.split(' '))
                )

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
