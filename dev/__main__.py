#!/bin/python2.6
# vim: ts=4 si expandtab

from aac import aacplusNero
from vorbis import vorbis
from flac import flac
from mp3 import lameMp3 as mp3
from shell import shell

import multiprocessing as mp
from optparse import OptionParser
from config import *
import sys, os, time

sh = shell()

# process Queue, the queue that will hold all the flac files we want to convert. 
# format: [ $infile, $target_format ]
pQ = mp.Queue() 

#copy Queue (for copying non flac files if requested)
# format: [ $infile, $outfile ]
cQ = mp.Queue()

# logging Queue, the encoders log progress to this 
# fomat: [ $infile, $outfile, $error_status, $return_code ]
lQ = mp.Queue()

# output Queue (this is where we write the following):
# [ $infile, $outfile, $format, $execution_time ]
oQ = mp.Queue()


#This area deals with checking the command line options,

def prog_usage():
    return """
Flac2all python script, version 4. Copyright 2006-2013 ziva-vatra
Licensed under the GPLv2 or later (http://www.ziva-vatra.com).
Please see http://www.gnu.org/licenses/gpl.txt for the full licence.
Main project website: http://code.google.com/p/flac2all/
"""

# I've decided that the encoder options should just be long options.
# quite frankly, because we are running out of letters that make sense.
# plus it makes a distinction between encoder opts, and program opts
# (which will continue to use single letters)
parser = OptionParser(usage=prog_usage())
parser.add_option("-c","--copy",action="store_true",dest="copy",
      default=False,help="Copy non flac files across (default=False)")

parser.add_option("","--opus-options",dest="opusencopts",
      default="quality=2",help="Colon delimited options to pass to opusenc. Any oggenc long option (one with two '--' in front) can be specified in the above format.")

parser.add_option("","--vorbis-options",dest="oggencopts",
      default="quality=2",help="Colon delimited options to pass to oggenc,for example:" +
      " 'quality=5:resample 32000:downmix:bitrate_average=96'." +
      " Any oggenc long option (one with two '--' in front) can be specified in the above format.")

parser.add_option("","--lame-options",dest="lameopts",
      default="-preset standard:q 0",help="Options to pass to lame, for example:           '-preset extreme:q 0:h:-abr'. "+
      "Any lame option can be specified here, if you want a short option (e.g. -h), then just do 'h'. "+
      "If you want a long option (e.g. '--abr'), then you need a dash: '-abr'")

parser.add_option("","--aacplus-options",dest="aacplusopts",
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
#lame is stupid, it is not consistent, sometimes using long opts, sometimes not
#so we need to specify on command line with dashes whether it is a long op or short
opts['lameopts'] = ' -'+' -'.join(opts['lameopts'].split(':'))

print prog_usage()

#pdb.set_trace()
try:
    opts['mode'] = args[0]

except(IndexError): #if no arguments specified
    print "No mode specified! Run with '-h' for help"
    sys.exit(1) #quit the program with non-zero status

try:
    opts['dirpath'] = os.path.abspath(args[1])

except(IndexError):
    print "No directory specified! Run with '-h' for help"
    sys.exit(2) #quit the program with non-zero status

#end command line checking

if os.path.exists(opts['outdir']) == False:
    print "Creating output directory"
    os.mkdir(opts['outdir'])

# In this version, we can convert multiple format at once, so for e.g.
# mode = mp3,vorbis will create both in parrallel
for mode in opts['mode'].split(','):
    if mode != "":
        try:
            os.mkdir(os.path.join(opts['outdir'],mode))
        except OSError as e:
            if e.errno == 17:
                print "Folder %s already exists, reusing..." % mode
            elif e.errno == 2:
                print "Parent path %s does not exist! quitting..." % (
                    opts['outdir']
                    )
            else:
                #everything else, raise error
                raise e
                    
# Magic goes here :)

# 1. populate the queue with flac files
files = sh.getfiles(opts['dirpath'])
for infile in files:
    for mode in opts['mode'].split(','):
#        outfile = os.path.join( 
#            opts['outdir'], 
#            infile.replace(opts['dirpath'],'')
#        )
        outfile = infile.replace(opts['dirpath'], opts['outdir'])
        if infile.endswith(".flac"):
            pQ.put([infile, outfile, opts['mode']])        
        else:
            if opts['copy'] == True:
                cQ.put([infile,outfile]) 

time.sleep(1) #Delay to resolve queue "broken pipe" errors
#for testing, we timeout after 5 seconds (normally we block until 
#processing is done
count = 0
while True:
    try:
        print pQ.get(timeout=5)
    except: break
    count += 1

print "We have %d flac filesi to convert" % count
print "We have %d non-flac files to copy across" % cQ.qsize()

print cQ.get()

sys.exit()
