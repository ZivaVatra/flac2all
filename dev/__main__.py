#!/bin/python2.6
# vim: ts=4 si expandtab

from aac import aacplusNero
from vorbis import vorbis
from flac import flac
from mp3 import lameMp3 as mp3

import multiprocessing as mp
from optparse import OptionParser
import sys

pQ = mp.Queue #process Queue, the queue that will hold all the flac files we want to convert. 
lQ = mp.Queue #logging Queue, the encoders log progress to this 

# These are global defaults, if you don't define a shell
# argument, the below will be used instead.
opts = {
"outdir":"./", #the directory we output to, defaults to current directory
"overwrite":False, #do we overwrite existing files
"nodirs":False, #do not create directories (dump all files into single dir)
"copy":False, #Copy non flac files (default is to ignore)
"lameopts":"--preset standard -q 0", #your mp3 encoding settings
"oggencopts":"quality=2", # your vorbis encoder settings
"flacopts":"-q 8", #your flac encoder settings
"aacplusopts":"-q 0.3 " 
}

#This area deals with checking the command line options,

def prog_usage():
    return """
Flac2all python script, version 4. Copyright 2006-2012 ziva-vatra
Licensed under the GPLv2 or later (http://www.ziva-vatra.com).
Please see http://www.gnu.org/licenses/gpl.txt for the full licence.
Main project website: http://code.google.com/p/flac2all/
"""

parser = OptionParser(usage=prog_usage())
parser.add_option("-c","--copy",action="store_true",dest="copy",
      default=False,help="Copy non flac files across (default=False)")

parser.add_option("-v","--vorbis-options",dest="oggencopts",
      default="quality=2",help="Colon delimited options to pass to oggenc,for example:" +
      " 'quality=5:resample 32000:downmix:bitrate_average=96'." +
      " Any oggenc long option (one with two '--' in front) can be specified in the above format.")
parser.add_option("-l","--lame-options",dest="lameopts",
      default="-preset standard:q 0",help="Options to pass to lame, for example:           '-preset extreme:q 0:h:-abr'. "+
      "Any lame option can be specified here, if you want a short option (e.g. -h), then just do 'h'. "+
      "If you want a long option (e.g. '--abr'), then you need a dash: '-abr'")
parser.add_option("-a","--aacplus-options",dest="aacplusopts",
      default="-q 0.3", help="AACplus options, currently only bitrate supported. e.g: \" -a 64 \""),
parser.add_option("-o","--outdir",dest="outdir",metavar="DIR", 
      help="Set custom output directory (default='./')",
      default="./"),
parser.add_option("-f","--force",dest="overwrite",action="store_true",
      help="Force overwrite of existing files (by default we skip)",
      default=False),
parser.add_option("-t","--threads",dest="threads",default=mp.cpu_count(),
      help="How many threads to run in parallel (default: autodetect [found %d cpu(s)] )" % mp.cpu_count()) 
parser.add_option("-n","--nodirs",dest="nodirs",action="store_true",
      default=False,help="Don't create Directories, put everything together")

(options,args) = parser.parse_args()

#update the opts dictionary with new values
opts.update(eval(options.__str__()))

#convert the formats in the args to valid formats for lame and oggenc
opts['oggencopts'] = ' --'+' --'.join(opts['oggencopts'].split(':'))
#lame is stupid, it is not consistent, somteims using long opts, sometimes not
#so we need to specify on command line with dashes whether it is a long op or short
opts['lameopts'] = ' -'+' -'.join(opts['lameopts'].split(':'))

print prog_usage()

#pdb.set_trace()
try:
    opts['mode'] = args[0]

except(IndexError): #if no arguments specified
    print "No mode specified! Run with '-h' for help"
    sys.exit(-1) #quit the program with non-zero status

try:
    opts['dirpath'] = os.path.realpath(args[1])

except(IndexError):
    print "No directory specified! Run with '-h' for help"
    sys.exit(-1) #quit the program with non-zero status

#end command line checking


