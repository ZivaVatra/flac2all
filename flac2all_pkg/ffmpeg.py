# vim: ts=4 autoindent expandtab
from config import ipath
from time import time
import subprocess as sp
import re


# Class that deals with ffmpeg
class ffmpeg:
    def __init__(self, ffmpeg_options):
            self.opts = [x for x in ffmpeg_options.split(' ') if x.strip() != ""]

    def codeclist(self):
        """ Returns list of Audio codecs supported by ffmpeg """
        flist = sp.check_output([
            "%sffmpeg" % ipath.ffmpegpath,
            "-encoders"
        ])
        # Parse out codec details
        flist = [x.strip().split(' ', 1) for x in flist.decode("utf-8").split("\n")]
        flist = list(filter(lambda x: len(x) == 2, flist))
        # Now we filter out the audio codecs into their own list
        alist = list(filter(lambda x: x[0].find('A') != -1, flist))
        # Split further into name and description, and return
        return [re.split("  +", x[1]) for x in alist]

    def convert(self, infile, outfile, audio_codec):
        # Seems ffmpeg now automatically parses the flac file + metadata. This
        # make things really simple (like with vorbis)
        startTime = time()
        cmd = [
            "%sffmpeg" % ipath.ffmpegpath,
            "-i",
            infile,
            "-c:a",
            audio_codec,
            self.opts,
            outfile,
        ]
        if len(self.opts) != 0:
            cmd.extend(self.opts)
        cmd.append(infile)
        rc = -1
        try:
            rc = sp.check_call(cmd)
        except sp.CalledProcessError as e:
            result = "ERROR:ffmpeg:%s %s" % (audio_codec, e.message)
        else:
            result = "SUCCESS"

        return [
            infile,
            outfile,
            "ffmpeg:" + audio_codec,
            result,
            rc,
            time() - startTime
        ]
