# -*- coding: utf-8 -*-
# vim: ts=4 expandtab si

import os

from config import ipath
from flac import flac, flacdecode
from time import time
import uuid
import subprocess as sp


class lameMp3(object):
    def __init__(self, lame_options):
        self.opts = lame_options

    def generate_lame_meta(self, metastring):
        tagstring = []

        # Dealing with genres defined within lame
        acceptable_genres = [
            "A Cappella",
            "Acid",
            "Acid Jazz",
            "Acid Punk",
            "Acoustic",
            "Alternative",
            "Alt. Rock",
            "Ambient",
            "Anime",
            "Avantgarde",
            "Ballad",
            "Bass",
            "Beat",
            "Bebob",
            "Big Band",
            "Black Metal",
            "Bluegrass",
            "Blues",
            "Booty Bass",
            "BritPop",
            "Cabaret",
            "Celtic",
            "Chamber Music",
            "Chanson",
            "Chorus",
            "Christian Gangsta Rap",
            "Christian Rap",
            "Christian Rock",
            "Classical",
            "Classic Rock",
            "Club",
            "Club-House",
            "Comedy",
            "Contemporary Christian",
            "Country",
            "Crossover",
            "Cult",
            "Dance",
            "Dance Hall",
            "Darkwave",
            "Death Metal",
            "Disco",
            "Dream",
            "Drum & Bass",
            "Drum Solo",
            "Duet",
            "Easy Listening",
            "Electronic",
            "Ethnic",
            "Eurodance",
            "Euro-House",
            "Euro-Techno",
            "Fast-Fusion",
            "Folk",
            "Folklore",
            "Folk/Rock",
            "Freestyle",
            "Funk",
            "Fusion",
            "Game",
            "Gangsta Rap",
            "Goa",
            "Gospel",
            "Gothic",
            "Gothic Rock",
            "Grunge",
            "Hardcore",
            "Hard Rock",
            "Heavy Metal",
            "Hip-Hop",
            "House",
            "Humour",
            "Indie",
            "Industrial",
            "Instrumental",
            "InstrumentalPop",
            "InstrumentalRock",
            "Jazz",
            "Jazz+Funk",
            "JPop",
            "Jungle",
            "Latin",
            "Lo-Fi",
            "Meditative",
            "Merengue",
            "Metal",
            "Musical",
            "NationalFolk",
            "NativeAmerican",
            "Negerpunk",
            "NewAge",
            "NewWave",
            "Noise",
            "Oldies",
            "Opera",
            "Other",
            "Polka",
            "PolskPunk",
            "Pop",
            "Pop-Folk",
            "Pop/Funk",
            "PornGroove",
            "PowerBallad",
            "Pranks",
            "Primus",
            "ProgressiveRock",
            "Psychedelic",
            "PsychedelicRock",
            "Punk",
            "PunkRock",
            "Rap",
            "Rave",
            "R&B",
            "Reggae",
            "Retro",
            "Revival",
            "RhythmicSoul",
            "Rock",
            "Rock&Roll",
            "Salsa",
            "Samba",
            "Satire",
            "Showtunes",
            "Ska",
            "SlowJam",
            "SlowRock",
            "Sonata",
            "Soul",
            "SoundClip",
            "Soundtrack",
            "SouthernRock",
            "Space",
            "Speech",
            "Swing",
            "SymphonicRock",
            "Symphony",
            "Synthpop",
            "Tango",
            "Techno",
            "Techno-Industrial",
            "Terror",
            "ThrashMetal",
            "Top40",
            "Trailer",
            "Trance",
            "Tribal",
            "Trip-Hop",
            "Vocal"
        ]

        genre_is_acceptable = 0  # By default the genre is not acceptable
        current_genre = ""  # variable stores current genre tag

        def update_tagstring(items):
            tagstring.extend([items[0], "%s" % items[1]])

        for genre in acceptable_genres:
            try:
                current_genre = metastring['GENRE'].strip().upper()
            except(KeyError):
                current_genre = "NO GENRE TAG"

            # case-insesitive comparison
            if current_genre == genre.strip().upper():
                genre_is_acceptable = 1  # we can use the genre

        if genre_is_acceptable == 0:  # if genre cannot be used
            print "The Genre \"%s\" cannot be used with lame,\
                setting to \"Other\" " % current_genre
            metastring['GENRE'] = "Other"

        else:
            # Capitalise the Genre, as per lame requirements
            metastring['GENRE'] = metastring['GENRE'].capitalize()
            genre_is_acceptable = 0  # reset the value for the next time

        try:
            update_tagstring(["--tt", metastring["TITLE"]])
            update_tagstring(["--ta", metastring['ARTIST']])
            update_tagstring(["--tl", metastring['ALBUM']])
            update_tagstring(["--ty", metastring['DATE']])
            update_tagstring(["--tg", metastring['GENRE']])
            update_tagstring(["--tn", metastring['TRACKNUMBER']])
        except KeyError:
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
        if comment_tag.strip() != "":
            update_tagstring(['--tc', "'%s'" % comment_tag])

        # Metadata population complete
        return tagstring

    def mp3convert(self, infile, outfile, logq):
        pipe = "/tmp/flac2all_%s" % str(uuid.uuid4()).strip()
        startTime = time()
        inmetadata = flac().getflacmeta(infile)
        os.mkfifo(pipe)

        try:
            metastring = self.generate_lame_meta(inmetadata)
        except(UnboundLocalError):
            metastring = []  # If we do not get meta information. leave blank

        (decoder, stderr) = flacdecode(infile, pipe)()
        cmd = [
            "%slame" % ipath.lamepath,
            "--silent",
        ]
        cmd.extend(metastring)
        cmd.extend(self.opts.split(' '))
        cmd.extend([pipe, "%s.mp3" % outfile])

        rc = sp.check_call(cmd)
        if os.path.exists(pipe):
            os.unlink(pipe)
        errline = stderr.read()
        errline = errline.upper()
        if errline.strip() != '':
            print "ERRORLINE: %s" % errline
        if errline.find("ERROR") != -1 or rc != 0:
            logq.put([
                infile,
                "mp3",
                "ERROR: decoder error: %s" % (
                    errline, -1,
                    time() - startTime
                )],
                timeout=10)
            return False

        logq.put([
            infile,
            outfile,
            "mp3",
            "SUCCESS",
            0,
            time() - startTime
        ])
