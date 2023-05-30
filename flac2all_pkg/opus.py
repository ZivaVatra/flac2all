# vim: ts=4 ai expandtab

import os
import re
from time import time
import subprocess as sp

if __name__ == '__main__' and __package__ is None:
    from os import path, sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

try:
	from config import ipath
except ImportError:
	from .config import ipath

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

        # Opus has stabalised, on versioning, and most distros have the stable
        # version, so we got rid of the logic that deals wit opeus version testing.

        data = re.search("\d+\.\d+\.\d+", data).group(0)
        (release, major, minor) = map(lambda x: int(x), data.split('.'))
        self.version = (release, major, minor)
        self.opts = opusencopts

    def convert(self, infile, outfile):
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

        # We no longer support 0.1.7. Seems the logic has been broken for ages
        # and nobody noticed. That tells me all those who convert to opus, are using
        # newer versions.
        result = None
        if (version[0] == 0) and (version[1] <= 1) and (version[2] <= 6):
            raise(NotImplementedError("Opus versions <= 0.1.7 no longer supported"))
        else:
            # Later versions support direct conversion from flac->opus, so no
            # need for anything fancy
            cmd = [
                "%sopusenc" % ipath.opusencpath,
                "--quiet",
            ]
            if self.opts.strip() != "":
                cmd.extend([x for x in self.opts.split(' ') if x.strip() != ""])

            outfile = "%s.opus" % (outfile)
            cmd.extend([infile, outfile])

            try:
                rc = sp.check_call(cmd)
                result = "SUCCESS"
            except sp.CalledProcessError as e:
                    rc = e.returncode
                    result = "ERROR: opusenc error '%s'. Could not convert" % (
                        str(e)
                    )
        return [
            infile,
            outfile,
            "opus",
            result,
            rc,
            time() - startTime
        ]
