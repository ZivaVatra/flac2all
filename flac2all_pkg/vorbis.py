# vim: ts=4 autoindent expandtab
from config import ipath
from time import time
import subprocess as sp
import os


# Class that deals with vorbis
class vorbis:
    def __init__(self, opts):
            self.opts = [x for x in opts['oggencopts'].split(' ') if x.strip() != ""]
            self.overwrite = opts['overwrite']

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
        if self.overwrite is False:
            if os.path.exists(outfile) is True:
                # return code is 0 because an existing file is not an error
                return [infile, outfile, "vorbis", "SUCCESS:EXISTS, skipping", 0, -1]
        else:
            if os.path.exists(outfile) is True:
                os.unlink(outfile)

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
