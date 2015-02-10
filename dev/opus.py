# vim: ts=4 ai expandtab
import os,re
from shell import shell
from time import time
from flac import flacdecode
from config import opusencpath
#Class that deals with the opus codec
class opus:
    def __init__(self,opusencopts):
        #Work out what version of opus we have
        self.version=None #Unknown by default
        fd = os.popen("%sopusenc -V" % opusencpath)
        data = fd.read(256)
        fd.close()
        data = re.search("\d\.\d\.\d",data).group(0)
        (release,major,minor) =  map(lambda x: int(x), data.split('.'))
        self.version=(release,major,minor)
        self.opts = opusencopts

    def opusConvert(self,infile,outfile,logq):
        # As the new versions of opus support flac natively, I think that the best option is to 
        # use >0.1.7 by default, but support earlier ones without tagging.
        startTime = time()

        if self.version == None:
            print "ERROR! Could not discover opus version, assuming version >= 0.1.7. THIS MAY NOT WORK!"
            version = (9,9,9)
        else: version=self.version

        #If we are a release prior to 0.1.7, use non-tagging type conversion, with warning
        if (version[0] == 0) and (version[1] <= 1) and (version[2] <= 6):
            print "WARNING: Opus version prior to 0.1.7 detected, NO TAGGING SUPPORT"
            decoder = flacdecode(infile)()
            encoder = os.popen("%sopusenc %s - %s.opus  2> /tmp/opusLog" % (
                opusencpath,
                self.opts,
                shell().parseEscapechars(outfile),
                ) ,'wb',8192)
            
            for line in decoder.readlines(): #while data exists in the decoders buffer
                encoder.write(line) #write it to the encoders buffer
            
            decoder.flush() #if there is any data left in the buffer, clear it
            decoder.close() #somewhat self explanetory
            
            encoder.flush() #as above
            encoder.close()
            logq.put([infile,outfile,"opus","SUCCESS_NOTAGGING",0, time() - startTime])
        else:
            rc = os.system("%sopusenc %s --quiet %s %s.opus" %
                (
                opusencpath,
                self.opts,
                shell().parseEscapechars(infile),
                shell().parseEscapechars(outfile)
                )
            )
            if ( rc != 0 ):
                logq.put([infile,outfile,"opus","ERROR: error executing opusenc. Could not convert",rc, time() - startTime])
            else:
                logq.put([infile,outfile,"opus","SUCCESS",rc, time() - startTime])

