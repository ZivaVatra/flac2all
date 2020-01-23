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
        try:
            rc = sp.check_call(cmd)
        except sp.CalledProcessError as e:
            result = "ERROR:oggenc %s" % str(e)
        else:
            result = "SUCCESS"

        return [
            infile,
            outfile,
            "vorbis",
            result,
            rc,
            time() - startTime
        ]
