#!/usr/bin/python2
import os,shutil
from sys import exit
import subprocess as sp
from time import sleep

infolder = "testinput"
outfolder = "testoutput"

if not os.path.exists(infolder):
	print "Error, %s does not exist. Please create it and stick some FLAC files in there for testing" % infolder
	exit(1)

files = os.listdir(infolder)
flacfiles = filter(lambda x: x.endswith(".flac"), files)
if len(flacfiles) == 0:
	print "No flac files found in %s. Please put some in there for testing (no subfolders please)"
	exit(2)

if not os.path.exists(outfolder): os.mkdir(outfolder)

testypes = ["mp3,vorbis","mp3","vorbis","flac","aacplusnero"];

for test in testypes:
	sleep(10)
	args = [
	 "--lame-options='-preset standard' ",
	 "--aacplus-options 'br 64'",
	 "--vorbis-options='quality=5:resample 32000:downmix'",
	 "--opus-options='music:vbr'"
	 ]

	for opt in ('-c','-f','-t 4','-n'):
		cmd = "python2 ./__main__.py %s %s %s -o %s %s" % (test,' '.join(args),opt,outfolder,infolder)
		print '-'*80
		print "Executing: %s" % cmd
		print '-'*80
		rc = sp.call(cmd,shell=True)
		if (rc != 0) :
			print "ERROR Executing command: \"%s\"\n" % cmd
			exit(rc)
		
	
#print "All successful! Deleting output folder"
#shutil.rmtree(outfolder)
print "Done!"
