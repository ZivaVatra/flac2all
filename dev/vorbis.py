# vim: ts=4 autoindent expandtab
from config import *
import os
from shell import shell

#Class that deals with vorbis
class vorbis:
    def __init__(self,vorbis_options):
            self.opts = vorbis_options

    def oggconvert(self,infile,outfile):
        #oggenc automatically parses the flac file + metadata, quite wonderful
        #really, we don't need to do anything here
        #The binary itself deals with the tag conversion etc
        #Which makes our life rather easy
        os.system("%soggenc %s -Q -o %s.ogg %s" %
            (
            oggencpath,
            self.opts,
            shell().parseEscapechars(outfile),
            shell().parseEscapechars(infile)
         
            )
        )

