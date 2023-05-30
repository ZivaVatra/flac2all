# -*- coding: utf-8 -*-
# vim: ts=4 expandtab si

import os
from time import time
import uuid
import subprocess as sp

if __name__ == '__main__' and __package__ is None:
    from os import path, sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

try:
    from flac import flac, flacdecode
    from config import ipath
except ImportError:
    from .flac import flac, flacdecode
    from .config import ipath


class lameMp3(object):
    def __init__(self, opts):
        self.opts = opts

    def generate_lame_meta(self, metastring):
        tagstring = []

        def update_tagstring(items):
            tagstring.extend([items[0], "%s" % items[1]])

        for k, v in metastring.items():

            # Use match-case syntax here when Python 3.10 becomes the minimum build target.
            #
            # match k:
            #   case "foo":

                # id3v1.1 tags

                if  k == "ALBUM":
                    # --TALB
                    update_tagstring(["--tl", v])

                elif k == "ARTIST":
                    # --TPE1
                    update_tagstring(["--ta", v])

                elif k == "CDDB":
                    # This preserves legacy behavior for the non-standard CDDB tag.
                    if "COMMENT" not in metastring:
                        update_tagstring(["--tc", "CDDB:" + v])

                elif k == "COMMENT":
                    # --COMM
                    if "CDDB" not in metastring:
                        update_tagstring(["--tc", v])
                    else:
                        # This preserves legacy behavior for the non-standard CDDB tag.
                        update_tagstring(["--tc", v + " || CDDB:" + metastring['CDDB']])

                elif k == "DATE":
                    # Assert DATE is in the "YYYY-MM-DD HH:MM:SS" format.
                    #
                    # --TDRC is the id3v2.4 equivalent.
                    # update_tagstring(["--tv", "TDRC=" + v])

                    try:
                        # --TYER=YYYY
                        id3year = int(v[0:4])
                        if 1 <= id3year <= 9999:
                            update_tagstring(["--ty", str(id3year).zfill(4)])
                    except:
                        pass

                    try:
                        # --TDAT=DDMM
                        id3day = int(v[8:10])
                        id3month = int(v[5:7])
                        if ( 1 <= id3day <= 31 ) and ( 1 <= id3month <= 12 ):
                            update_tagstring(["--tv", "TDAT=" + str(id3day).zfill(2) + str(id3month).zfill(2)])
                    except:
                        pass

                    try:
                        # --TIME=HHMM
                        id3hour = int(v[11:13])
                        id3minute = int(v[14:16])
                        if ( 0 <= id3hour <= 23 ) and ( 0 <= id3minute <= 59 ):
                            update_tagstring(["--tv", "TIME=" + str(id3hour).zfill(2) + str(id3minute).zfill(2)])
                    except:
                        pass

                elif k == "GENRE":
                    # --TCON
                    update_tagstring(["--tg", v.capitalize()])

                elif k == "TITLE":
                    # --TIT2
                    update_tagstring(["--tt", v])

                elif k == "TRACKNUMBER":
                    # --TRCK
                    tracknumber = 0
                    tracktotal = 0

                    try:
                        tracknumber = int(v)
                    except:
                        pass

                    try:
                        tracktotal = int(metastring['TRACKTOTAL'])
                    except:
                        pass

                    if 1 <= tracknumber <= tracktotal <= 255:
                        update_tagstring(["--tn", str(tracknumber) + "/" + str(tracktotal)])

                    elif 1 <= tracknumber <= 255:
                        update_tagstring(["--tn", str(tracknumber)])


                # id3v2.3 tags

                elif k == 'ALBUMARTIST':
                    update_tagstring(["--tv", "TPE2=" + v])

                elif k == 'ALBUMARTISTSORT':
                    update_tagstring(["--tv", "TSO2=" + v])

                elif k == 'ALBUMSORT':
                    update_tagstring(["--tv", "TSOA=" + v])

                elif k == 'ARTISTSORT':
                    update_tagstring(["--tv", "TSOP=" + v])

                elif k == 'BPM':
                    update_tagstring(["--tv", "TBPM=" + v])

                elif k == 'COMPILATION':
                    update_tagstring(["--tv", "TCMP=" + v])

                elif k == 'COMPOSER':
                    update_tagstring(["--tv", "TCOM=" + v])

                elif k == 'COMPOSERSORT':
                    update_tagstring(["--tv", "TSOC=" + v])

                elif k == 'CONDUCTOR':
                    update_tagstring(["--tv", "TPE3=" + v])

                elif k == 'COPYRIGHT':
                    update_tagstring(["--tv", "TCOP=" + v])

                elif k == 'DISCNUMBER':
                    discnumber = 0
                    disctotal = 0

                    try:
                        discnumber = int(v)
                    except:
                        pass

                    try:
                        disctotal = int(metastring['DISCTOTAL'])
                    except:
                        pass

                    if 1 <= discnumber <= disctotal <= 255:
                        update_tagstring(["--tv", "TPOS=" + str(discnumber) + "/" + str(disctotal)])

                    elif 1 <= discnumber <= 255:
                        update_tagstring(["--tv", "TPOS=" + str(discnumber)])

                elif k == 'DISCSUBTITLE':
                    # Foobar2000 uses TXXX:DISCSUBTITLE instead.
                    update_tagstring(["--tv", "TSST=" + v])

                # Skip case 'ENCODEDBY' and override it later.

                # Skip case 'ENCODERSETTINGS' because LAME sets it automatically.

                elif k == 'GROUPING':
                    update_tagstring(["--tv", "TIT1=" + v])

                elif k == 'ISRC':
                    update_tagstring(["--tv", "TSRC=" + v])

                elif k == 'KEY':
                    update_tagstring(["--tv", "TKEY=" + v])

                elif k == 'LABEL':
                    # Foobar2000 uses TXXX:LABEL instead.
                    update_tagstring(["--tv", "TPUB=" + v])

                elif k == 'LANGUAGE':
                    update_tagstring(["--tv", "TLAN=" + v])

                elif k == 'LICENSE':
                    update_tagstring(["--tv", "WCOP=" + v])

                elif k == 'LYRICIST':
                    update_tagstring(["--tv", "TEXT=" + v])

                elif k == 'LYRICS':
                    update_tagstring(["--tv", "USLT=" + v])

                elif k == 'MEDIA':
                    # Foobar2000 uses TXXX:MEDIA instead.
                    update_tagstring(["--tv", "TMED=" + v])

                elif k == 'MOVEMENT':
                    movementnumber = 0
                    movementtotal = 0

                    try:
                        movementnumber = int(v)
                    except:
                        pass

                    try:
                        movementtotal = int(metastring['MOVEMENTTOTAL'])
                    except:
                        pass

                    if 1 <= movementnumber <= movementtotal <= 255:
                        update_tagstring(["--tv", "MVIN=" + str(movementnumber) + "/" + str(movementtotal)])

                    elif 1 <= movementnumber <= 255:
                        update_tagstring(["--tv", "MVIN=" + str(movementnumber)])

                elif k == 'MOVEMENTNAME':
                    update_tagstring(["--tv", "MVNM=" + v])

                elif k == 'ORIGINALALBUM':
                    # This fits the naming convention, but is not in the MusicBrainz specification.
                    update_tagstring(["--tv", "TOAL=" + v])

                elif k == 'ORIGINALARTIST':
                    # This fits the naming convention, but is not in the MusicBrainz specification.
                    update_tagstring(["--tv", "TOPE=" + v])

                elif k == 'ORIGINALDATE':
                    # --TDOR is an id3v2.4 tag.
                    # update_tagstring(["--tv", "TDOR=" + v])

                    if "ORIGINALYEAR" not in metastring:
                        # --TORY=YYYY is the id3v2.3 equivalent.
                        try:
                            id3year = int(v[0:4])
                            if 1 <= id3year <= 9999:
                                update_tagstring(["--tv", "TORY=" + str(id3year).zfill(4)])
                        except:
                            pass

                elif k == 'ORIGINALFILENAME':
                    update_tagstring(["--tv", "TOFN=" + v])

                elif k == 'ORIGINALYEAR':
                    # --TORY=YYYY
                    try:
                        id3year = int(v[0:4])
                        if 1 <= id3year <= 9999:
                            update_tagstring(["--tv", "TORY=" + str(id3year).zfill(4)])
                    except:
                        pass

                elif k == 'PUBLISHER':
                    # This is a non-spec synonym for LABEL.
                    # Foobar2000 uses TXXX:PUBLISHER instead.
                     if "LABEL" not in metastring:
                         update_tagstring(["--tv", "TPUB=" + v])

                elif k == 'RATING':
                    update_tagstring(["--tv", "POPM=" + v])

                elif k == 'REMIXER':
                    update_tagstring(["--tv", "TPE4=" + v])

                elif k == 'SUBTITLE':
                    update_tagstring(["--tv", "TIT3=" + v])

                elif k == 'TITLESORT':
                    update_tagstring(["--tv", "TSOT=" + v])

                elif k == 'WEBSITE':
                    update_tagstring(["--tv", "WOAR=" + v])


                # Appropriate translations for these id3v2.3 tags are not apparent.
                #
                # --AENC    Audio encryption
                # --COMR    Commercial frame
                # --ENCR    Encryption method registration
                # --EQUA    Equalization
                # --ETCO    Event timing codes
                # --GEOB    General encapsulated object
                # --GRID    Group identification registration
                # --LINK    Linked information
                # --MCDI    Music CD identifier
                # --MLLT    MPEG location lookup table
                # --OWNE    Ownership frame
                # --PRIV    Private frame
                # --PCNT    Play counter
                # --POSS    Position synchronisation frame
                # --RBUF    Recommended buffer size
                # --RVAD    Relative volume adjustment
                # --RVRB    Reverb
                # --SYLT    Synchronized lyric/text
                # --SYTC    Synchronized tempo codes
                # --TDLY    Playlist delay
                # --TOLY    Original lyricist(s)/text writer(s)
                # --TOWN    File owner/licensee
                # --TRDA    Recording dates
                # --TRSN    Internet radio station name
                # --TRSO    Internet radio station owner
                # --USER    Terms of use
                # --WCOM    Commercial information
                # --WOAF    Official audio file webpage
                # --WOAS    Official audio source webpage
                # --WORS    Official internet radio station homepage
                # --WPAY    Payment
                # --WPUB    Official publisher webpage
                # --WXXX    User defined URL link

                # Skip these id3v2.4 tags because LAME writes them out as
                # id3v2.3 frames in a way that confuses most parsers.
                #
                # --TIPL:arranger     ARRANGER
                # --TIPL:DJ-mix       DJMIXER
                # --TIPL:engineer     ENGINEER
                # --TIPL:mix          MIXER
                # --TMOO              MOOD
                # --TMCL:instrument   PERFORMER
                # --TIPL:producer     PRODUCER
                #
                # IPLS should be a substitute for TIPL and TCML here, but LAME
                # suppresses it on the command line.


                # VORBIS tags

                elif k == 'ACOUSTID_FINGERPRINT':
                    update_tagstring(["--tv", "TXXX=Acoustid Fingerprint=" + v])

                elif k == 'ACOUSTID_ID':
                    update_tagstring(["--tv", "TXXX=Acoustid Id=" + v])

                elif k == 'ARTISTS':
                    update_tagstring(["--tv", "TXXX=ARTISTS=" + v])

                elif k == 'ASIN':
                    update_tagstring(["--tv", "TXXX=ASIN=" + v])

                elif k == 'BARCODE':
                    update_tagstring(["--tv", "TXXX=BARCODE=" + v])

                elif k == 'CATALOGNUMBER':
                    update_tagstring(["--tv", "TXXX=CATALOGNUMBER=" + v])

                elif k == 'DIRECTOR':
                    update_tagstring(["--tv", "TXXX=DIRECTOR=" + v])

                elif k == 'FINGERPRINT':
                    update_tagstring(["--tv", "TXXX=MusicMagic Fingerprint=" + v])

                elif k == 'MUSICIP_PUID':
                    update_tagstring(["--tv", "TXXX=MusicIP PUID=" + v])

                elif k == 'SCRIPT':
                    update_tagstring(["--tv", "TXXX=SCRIPT=" + v])

                elif k == 'SHOWMOVEMENT':
                    update_tagstring(["--tv", "TXXX=SHOWMOVEMENT=" + v])

                elif k == 'WORK':
                    update_tagstring(["--tv", "TXXX=WORK=" + v])

                elif k == 'WRITER':
                    update_tagstring(["--tv", "TXXX=WRITER=" + v])


                # MusicBrainz Picard tags

                elif k == 'MUSICBRAINZ_ALBUMARTISTID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Album Artist Id=" + v])

                elif k == 'MUSICBRAINZ_ALBUMID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Album Id=" + v])

                elif k == 'RELEASECOUNTRY':
                    # Foobar2000 uses TXXX:RELEASECOUNTRY instead.
                    update_tagstring(["--tv", "TXXX=MusicBrainz Album Release Country=" + v])

                elif k == 'RELEASESTATUS':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Album Status=" + v])

                elif k == 'RELEASETYPE':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Album Type=" + v])

                elif k == 'MUSICBRAINZ_ARTISTID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Artist Id=" + v])

                elif k == 'MUSICBRAINZ_DISCID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Disc Id=" + v])

                elif k == 'MUSICBRAINZ_ORIGINALALBUMID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Original Album Id=" + v])

                elif k == 'MUSICBRAINZ_ORIGINALARTISTID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Original Artist Id=" + v])

                elif k == 'MUSICBRAINZ_RECORDINGID':
                    # MUSICBRAINZ_RECORDINGID is obsolesced by MUSICBRAINZ_TRACKID.
                    if 'MUSICBRAINZ_TRACKID' not in metastring:
                        update_tagstring(["--tv", "TXXX=MusicBrainz Track Id=" + v])
                        update_tagstring(["--tv", "UFID=" + v])

                elif k == 'MUSICBRAINZ_RELEASEGROUPID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Release Group Id=" + v])

                elif k == 'MUSICBRAINZ_RELEASETRACKID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Release Track Id=" + v])

                elif k == 'MUSICBRAINZ_TRACKID':
                    # This is not spec, but it fits the pattern.
                    update_tagstring(["--tv", "TXXX=MusicBrainz Track Id=" + v])

                    # Picard uses and expects the UFID tag, but the LAME CLI
                    # suppresses it. Regardless, try passing UFID because it
                    # does not cause an error and could work in the future.
                    update_tagstring(["--tv", "UFID=" + v])

                elif k == 'MUSICBRAINZ_TRMID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz TRM Id=" + v])

                elif k == 'MUSICBRAINZ_WORKID':
                    update_tagstring(["--tv", "TXXX=MusicBrainz Work Id=" + v])

                # Skip these tags because Replay Gain must be recalculated
                # after transcoding, and because LAME calculates the (fast)
                # track gain by default.
                #
                # --TXXX:REPLAYGAIN_ALBUM_GAIN
                # --TXXX:REPLAYGAIN_ALBUM_PEAK
                # --TXXX:REPLAYGAIN_ALBUM_RANGE
                # --TXXX:REPLAYGAIN_REFERENCE_LOUDNESS
                # --TXXX:REPLAYGAIN_TRACK_GAIN
                # --TXXX:REPLAYGAIN_TRACK_PEAK
                # --TXXX:REPLAYGAIN_TRACK_RANGE

        # Ignore the ENCODERSETTINGS tag and override the ENCODEDBY tag.
        # Link to GitHub because http://flac2all.witheredfire.com/ is offline.
        update_tagstring(["--tv", "TENC=flac2all (https://github.com/ZivaVatra/flac2all)"])

        # Metadata population complete
        return tagstring

    def convert(self, infile, outfile):
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

        rc = sp.call(cmd)
        errline = stderr.read().decode('utf-8')
        if os.path.exists(pipe):
            os.unlink(pipe)
        errline = stderr.read()
        errline = errline.upper()

        if rc != 0:
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
