# -*- coding: utf-8 -*-
#vim ts=4 expandtab si 

import os

from config import *

#Class that deals with FLAC

class flac:
    def flacconvert(self,flacopts, infile, outfile):
        #TODO: see about tag copying across as well
        print "converting flac"
        os.system("%sflac -d %s -o - | %sflac %s -o %s.flac -" %
            (flacpath, infile, flacpath, flacopts, outfile)
        )


    def getflacmeta(self,flacfile):
        #The FLAC file format states that song info will be stored in block 2, so
        #we do not look at the other blocks
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



