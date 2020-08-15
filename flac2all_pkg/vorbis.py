# vim: ts=4 autoindent expandtab
from time import time
import subprocess as sp

if __name__ == '__main__' and __package__ is None:
    from os import path, sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

try:
	from config import ipath
except ImportError:
	from .config import ipath


# Class that deals with vorbis
class vorbis:
    def __init__(self, opts):
        self.opts = [x for x in opts.split(' ') if x.strip() != ""]

    def convert(self, infile, outfile):
        # oggenc automatically parses the flac file + metadata, quite wonderful
        # really, we don't need to do anything here
        # The binary itself deals with the tag conversion etc
        # Which makes our life rather easy
        startTime = time()
        outfile = "%s.ogg" % outfile.strip()

        cmd = [
            "%soggenc" % ipath.oggencpath,
            "-Q",
            "-o",
            outfile,
        ]
        if len(self.opts) != 0:
            cmd.extend(self.opts)

        cmd.append(infile)
        rc = -1
        codec = sp.Popen(cmd, stderr=sp.PIPE, stdout.sp.PIPE)
        stdout, stderr = codec.communicate()
        errline = stderr.read().decode('utf-8')
        errline = errline.upper()
        rc = codec.returncode

        if rc != 0:
            return [
                infile,
                outfile,
                "vorbis",
                "ERROR: %s" % errline,
                -1,
                time() - startTime
            ]

        return [
            infile,
            outfile,
            "vorbis",
            "SUCCESS",
            rc,
            time() - startTime
        ]
