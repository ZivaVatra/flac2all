# vim: ts=4 autoindent expandtab
from config import ipath
from time import time
import subprocess as sp


# Class that deals with vorbis
class vorbis:
    def __init__(self, vorbis_options):
            self.opts = [x for x in vorbis_options.split(' ') if x.strip() != ""]

    def convert(self, infile, outfile):
        # oggenc automatically parses the flac file + metadata, quite wonderful
        # really, we don't need to do anything here
        # The binary itself deals with the tag conversion etc
        # Which makes our life rather easy
        startTime = time()
        cmd = [
            "%soggenc" % ipath.oggencpath,
            "-Q",
            "-o",
            "%s.ogg" % outfile,
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
