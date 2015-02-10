# vim: ts=4 ai expandtab 

#Class that deals with AAC+ 
import os
from shell import shell
from flac import flac
from config import *

#For the binary-only Nero AAC encoder
class aacplusNero:
    def __init__(self, aacopts):
        self.opts = aacopts
        if os.path.exists("%sneroAacEnc" % neroaacpath) == False:
            print "ERROR: NeroAacEnc not found! Cannot convert."
            sys.exit(-1)

    def generateNeroTags(self,indata):
        ''' The new versions of nero AAC encoder for Linux provides neroAacTag '''
        tags = ""

        #NeroTag format (for 'standard Nero Digital') along with 'indata' keys
            #  title = TITLE
            #  artist = ARTIST
            #  year = DATE
            #  album = ALBUM
            #  genre = GENERE
            #  track = TRACKNUMBER
            #  totaltracks = 
            #  disc
            #  totaldiscs
            #  url = URL
            #  copyright = PUBLISHER
            #  comment = COMMENT (if blank, put in something like 'converted by flac2all ($url)' )
            #  lyrics
            #  credits = ENCODEDBY
            #  rating
            #  label = PUBLISHER
            #  composer = COMPOSER
            #  isrc
            #  mood
            #  tempo
        #  In format: -meta:<name>=<value> 
        #  User-defined fields are -meta-user:<name>=<value> 

        validnerotags = {
            'title':'TITLE',
            'artist':'ARTIST',
            'year':'DATE',
            'album':'ALBUM',
            'genre':'GENRE',
            'track':'TRACKNUMBER',
            'copyright':'PUBLISHER',
            'comment':'COMMENT',
            'credits':'ENCODEDBY',
            'label':'PUBLISHER',
            'composer':'COMPOSER',
            'url':'URL',
        }

        for nerokey in validnerotags:
            try:
                tag = indata[ validnerotags[nerokey] ] 
            except KeyError as e:
                if e.message == 'COMMENT':
                    tag = " converted by flac2all  - http://code.google.com/p/flac2all/ "
                else:
                    continue
            tags += " -meta:\"%s\"=\"%s\" " % (nerokey.strip(), tag.strip() )

        return tags

    def AACPconvert(self,infile,outfile,logq):

        inmetadata = flac().getflacmeta("\"" + infile + "\"")

        tagcmd = "%sneroAacTag " % neroaacpath
        try:
            metastring = self.generateNeroTags(inmetadata)
        except(UnboundLocalError):
            metastring = ""



        #rb stands for read-binary, which is what we are doing, with a 1024 byte buffer
        decoder = os.popen(flacpath + "flac -d -s -c " + shell().parseEscapechars(infile),'rb',1024)
        #wb stands for write-binary
        encoder = os.popen("%sneroAacEnc %s -if - -of %s.mp4 > /tmp/aacplusLog" % (
            neroaacpath,
            self.opts,
            shell().parseEscapechars(outfile),
            ) ,'wb',8192)

        for line in decoder.readlines(): #while data exists in the decoders buffer
            encoder.write(line) #write it to the encoders buffer

        decoder.flush() #if there is any data left in the buffer, clear it
        decoder.close() #somewhat self explanetory

        encoder.flush() #as above
        encoder.close()

        #Now as the final event, load up the tags
        rc = os.system("%s \"%s.mp4\" %s" % (tagcmd, outfile, metastring))
#        print "%s %s.mp4 %s" % (tagcmd, outfile, metastring)
        if rc != 0:
            logq.put([infile,outfile,"aacNero","WARNING: Could not tag AAC file",rc, time() - startTime])
        else:
            logq.put([infile,outfile,"aacNero","SUCCESS",0, time() - startTime])
