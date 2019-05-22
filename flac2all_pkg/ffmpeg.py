# vim: ts=4 autoindent expandtab
from config import ipath
from time import time
import subprocess as sp
import re
import os


# Class that deals with ffmpeg
class ffmpeg:
    def __init__(self, opts, codec):
        if opts is not None:
            self.opts = opts['ffmpegopts']
            self.audio_codec = codec
            self.overwrite = opts['overwrite']

    def codeclist(self):
        """ Returns list of Audio codecs supported by ffmpeg """
        try:
            flist = sp.check_output([
                "%sffmpeg" % ipath.ffmpegpath,
                "-encoders"
            ], stderr=sp.PIPE)
        except FileNotFoundError:
            # No ffmpeg, no codeclist
            return []
        # Parse out codec details
        flist = [x.strip().split(' ', 1) for x in flist.decode("utf-8").split("\n")]
        flist = list(filter(lambda x: len(x) == 2, flist))
        # Now we filter out the audio codecs into their own list
        alist = list(filter(lambda x: x[0].find('A') != -1, flist))
        # Split further into name and description, and return
        alist = [re.split("  +", x[1]) for x in alist]
        alist = list(filter(lambda x: len(x) == 2, alist))
        return alist

    def convert(self, infile, outfile):
        # Seems ffmpeg now automatically parses the flac file + metadata. This
        # make things really simple (like with vorbis)

        # However it also makes some things really complex. Namely it does not automatically
        # append the extension to the codec you are encoding to. Also, if you don't specify
        # valid extension, it fails, because ffmpeg uses the extension to decide which
        # container you want to mux to. So we have to keep a manual list of self.audio_codecs and
        # what extensions are used for it. That is what the codectable below does.
        # If a codec is not in the table, we assume the codec name is the extension
        # (eg: audio codec "aac" has "aac" extension).
        codectable = {
            "wmav1": "wma",
            "wmav2": "wma",
            "mp2fixed": "mp2",
            "ac3_fixed": "ac3",
        }
        if self.audio_codec in codectable:
            extension = codectable[self.audio_codec]
        else:
            extension = self.audio_codec
        outfile = outfile.strip() + "." + extension
        if os.path.exists(outfile) and self.overwrite is False:
            return [
                infile,
                outfile,
                "ffmpeg:" + self.audio_codec,
                "SUCCESS:EXISTS, skipping",
                0,
                -1
            ]

        startTime = time()
        cmd = [
            "%sffmpeg" % ipath.ffmpegpath,
            "-i",
            infile,
            "-c:a",
            self.audio_codec,
        ]
        cmd.extend(self.opts)
        cmd.append(outfile)
        rc = -1
        try:
            rc = sp.check_call(cmd)
        except sp.CalledProcessError as e:
            result = "ERROR:ffmpeg:%s %s" % (self.audio_codec, e)
        else:
            result = "SUCCESS"

        return [
            infile,
            outfile,
            "ffmpeg:" + self.audio_codec,
            result,
            rc,
            time() - startTime
        ]
