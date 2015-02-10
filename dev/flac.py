# -*- coding: utf-8 -*-
# vim: ts=4 expandtab si 

import os

from config import *
from shell import shell

#This class is called by every other conversion function, to return a "decode" object
class flacdecode:
    def __init__(self,infile):
        self.infile = infile
        self.shell = shell
    def __call__(self):
        return os.popen(flacpath + "flac -d -s -c " + self.shell().parseEscapechars(self.infile),'rb',1024)

#Class that deals with FLAC

class flac:
    def __init__(self,flacopts=""):
        self.opts = flacopts

    def flacConvert(self, infile, outfile,logq):
        #TODO: see about tag copying across as well
        print "converting flac to flac"
        decoder = flacdecode(infile)()
        encoder = os.popen("%sflac %s -o %s.flac -" % (
            flacpath,
            self.opts,
            shell().parseEscapechars(outfile),
            ) ,'wb',8192)
            
        for line in decoder.readlines(): #while data exists in the decoders buffer
            encoder.write(line) #write it to the encoders buffer
            
        decoder.flush() 
        decoder.close()
        encoder.flush() 
        encoder.close()


        #To straight up meta copy
        rc = os.system("%smetaflac --export-tags-to=- %s | %smetaflac --import-tags-from=- %s" %
            metaflacpath,
            self.shell().parseEscapechars(infile),
            metaflacpath,
            shell().parseEscapechars(outfile)
        )
        if (rc == 0):
            logq.put([infile,outfile,"flac","SUCCESS",rc, time() - startTime])
        else:
            print "WARNING: Could not transfer tags to new flac file!"
            logq.put([infile,outfile,"flac","WARNING: Unable to transfer tag to new flac file",0, time() - startTime])


    def getflacmeta(self,flacfile):
        flacdata = os.popen("%smetaflac --list --block-type VORBIS_COMMENT  %s" %
            (
            metaflacpath,
            flacfile
            )
        )

        datalist = [] #init a list for storing all the data in this block

        #this dictionary (note different brackets) will store only the comments
        #for the music file
        commentlist = {}

        for data in flacdata.readlines():
            #get rid of any whitespace from the left to the right
            data = data.strip()

            #check if the tag is a comment field (shown by the first 7 chars
            #spelling out "comment")
            if(data[:8] == "comment["):
                datalist.append( data.split(':') )

        for data in datalist:
            #split according to [NAME]=[VALUE] structure
            comment = data[1].split('=')
            comment[0] = comment[0].strip()
            comment[1] = comment[1].strip()

            #convert to upper case
            #we want the key values to always be the same case, we decided on
            #uppercase (whether the string is upper or lowercase, is dependent
            # on the tagger used)
            comment[0] = comment[0].upper()

            #assign key:value pair, comment[0] will be the key, and comment[1]
            #the value
            commentlist[comment[0]] = comment[1]
        return commentlist

    def flactest(self,file,outfile):
        test = os.popen(flacpath + "flac -s -t \"" + file + "\"",'r')
        #filepath = generateoutdir(file,outfile) + "results.log"

    #if (os.path.exists(filepath)):
    #   os.remove(filepath)

                #os.mknod(filepath,0775)
                #out = os.popen(filepath,'w')

                #results = ""

                #for line in test.readlines():
#                       print "++++++++++++" + line
#                       results = line

#               out.write(results)

#       print "==============" + results
#       test.flush()
        test.close()

#       out.flush()
#       out.close()



