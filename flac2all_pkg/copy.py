# vim: ts=4 autoindent expandtab
from shutil import copyfile

from time import time


# Class that deals with copying files
class copy:
    def __init__(self):
        pass

    def convert(self, infile, outfile):
        startTime = time()
        outfile = outfile.strip()

        try:
            copyfile(infile, outfile)
        except Exception as e:
            result = "ERROR:copy %s" % str(e)
            rc = -1
        else:
            result = "SUCCESS"
            rc = 0

        return [
            infile,
            outfile,
            "copy",
            result,
            rc,
            time() - startTime
        ]
