# -*- coding: utf-8 -*-
# vim: ts=4 expandtab si

import os

from config import ipath
from flac import flac, flacdecode
from time import time
import uuid
import subprocess as sp


class lameMp3(object):
    def __init__(self, opts):
        self.opts = opts["lameopts"]
        self.overwrite = opts['overwrite']

    def generate_lame_meta(self, metastring):
        tagstring = []

        def update_tagstring(items):
            tagstring.extend([items[0], "%s" % items[1]])

        # Capitalise the Genre, as per lame requirements
        if "GENRE" in metastring:
            metastring['GENRE'] = metastring['GENRE'].capitalize()
        else:
            print("Warning: No Genre detected, setting to \"Unknown\"")
            metastring.update({"GENRE": "Unknown"})

        try:
            update_tagstring(["--tt", metastring["TITLE"]])
            update_tagstring(["--ta", metastring['ARTIST']])
            update_tagstring(["--tl", metastring['ALBUM']])
            update_tagstring(["--ty", metastring['DATE']])
            update_tagstring(["--tg", metastring['GENRE']])
            update_tagstring(["--tn", metastring['TRACKNUMBER']])
        except KeyError:
            # If the source file does not have the metadata set, we just
            # silently continue
            pass

        # COMMENTS AND CDDB ARE PLACED TOGETHER, as there exists no seperate
        # "CDDB Field" option for mp3. this is only if we have a comment to
        # begin with
        comment_tag = ""
        try:
            comment_tag += metastring['COMMENT']

            try:
                comment_tag += "  || CDDB:%s" % (
                    metastring['CDDB']
                )
            except(KeyError):
                pass

        except(KeyError):
            # this is for if we have a CDDB value
            try:
                comment_tag += "CDDB:%s" % (
                    metastring['CDDB']
                )
            except(KeyError):
                pass
        comment_tag += " || Converted with flac2all (http://flac2all.witheredfire.com/)"

        update_tagstring(['--tc', "'%s'" % comment_tag])

        # Metadata population complete
        return tagstring

    def convert(self, infile, outfile):
        if self.overwrite is True:
            if os.path.exists(outfile) is True:
                os.unlink(outfile)
        else:
            return [infile, outfile, "mp3", "Outfile exists, skipping", 0, -1]

        pipe = "/tmp/flac2all_%s-%s" % (uuid.uuid4(), uuid.uuid4())
        os.mkfifo(pipe)
        startTime = time()
        inmetadata = flac().getflacmeta(infile)

        try:
            metastring = self.generate_lame_meta(inmetadata)
        except(UnboundLocalError):
            metastring = []  # If we do not get meta information. leave blank

        stderr = flacdecode(infile, pipe)()
        cmd = [
            "%slame" % ipath.lamepath,
            "--silent",
        ]
        cmd.extend(metastring)
        cmd.extend(self.opts.split(' '))
        cmd.extend([pipe, "%s.mp3" % outfile])

        rc = sp.check_call(cmd)
        errline = stderr.read().decode('utf-8')
        errline = errline.upper()
        os.unlink(pipe)
        if errline.strip() != '':
            print("ERRORLINE: %s" % errline)
        if errline.find("ERROR") != -1 or rc != 0:
            return [
                infile,
                outfile,
                "mp3",
                "ERROR: %s" % errline,
                -1,
                time() - startTime
            ]

        return [
            infile,
            outfile,
            "mp3",
            "SUCCESS",
            0,
            time() - startTime
        ]
