#!/usr/bin/python
#Version 1.3
# vim: ts=4 autoindent expandtab
"""
===============================================================================

Python script for conversion of flac files to flac/mp3/ogg.

Copyright 2006-2012 Ziva-Vatra, Belgrade
(www.ziva-vatra.com, mail: ziva_vatra@mailshack.com)

Project website: http://code.google.com/p/flac2all/

Licensed under the GNU GPL. Do not remove any information from this header
(or the header itself). If you have modified this code, feel free to add your
details below this (and by all means, mail me, I like to see what other people
have done)

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License (version 2)
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

===============================================================================
"""

import sys
import os
import string,re
import pdb

#CODE

#Class that deals with AAC+
class aacplusNero:
    def __init__(self):
        pass #keep the constructor empty for now

    def AACPconvert(self,aacopts,infile,outfile): 
        #Uncomment the line below if you want the file currently being
        #converted to be displayed
        #print parseEscapechars(infile)

        #rb stands for read-binary, which is what we are doing, with a 1024 byte buffer
        decoder = os.popen(flacpath + "flac -d -s -c " + shell().parseEscapechars(infile),'rb',1024)
        #wb stands for write-binary
        encoder = os.popen("%sneroAacEnc %s -if - -of %s.aac  > /tmp/aacplusLog" % (
            aacpath,
            aacopts,
            shell().parseEscapechars(outfile),
            ) ,'wb',8192) 


        for line in decoder.readlines(): #while data exists in the decoders buffer
            encoder.write(line) #write it to the encoders buffer

        decoder.flush() #if there is any data left in the buffer, clear it
        decoder.close() #somewhat self explanetory

        encoder.flush() #as above
        encoder.close()


#Class that deals with vorbis
class vorbis:
    def oggconvert(self,oggencopts,infile,outfile):
        #oggenc automatically parses the flac file + metadata, quite wonderful
        #really, we don't need to do anything here
        #The binary itself deals with the tag conversion etc
        #Which makes our life rather easy
        os.system("%soggenc %s -Q -o %s.ogg %s" %
            (
            oggencpath,
            oggencopts,
            shell().parseEscapechars(outfile),
            shell().parseEscapechars(infile)
            )
        )


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
        flacdata = os.popen("%smetaflac --list --block-number 2 %s" %
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
            data = string.strip(data)

            #check if the tag is a comment field (shown by the first 7 chars
            #spelling out "comment")
            if(data[:8] == "comment["):
                datalist.append(string.split(data,":"))

        for data in datalist:
            #split according to [NAME]=[VALUE] structure
            comment = string.split(data[1],"=")
            comment[0] = string.strip(comment[0])
            comment[1] = string.strip(comment[1])
            #convert to upper case
            #we want the key values to always be the same case, we decided on
            #uppercase (whether the string is upper or lowercase, is dependent
            # on the tagger used)
            comment[0] = string.upper(comment[0])

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





#Class dealing with shell/output related things:

class shell:
    def generateoutdir(self,indir, outdir,dirpath):
                #if we find the dirpath in the current output path, we replace
                #it with the new output path. (so that we don't get
                #/mnt/convertedfromflac/mnt/flac/[file].mp3, in this case
                #"/mnt/" exist in both)
        if (string.find(os.path.split(indir)[0], dirpath) != -1):
            return string.replace(os.path.split(indir)[0], dirpath, outdir)
        else:
            #if we do not find an instance of dir path in output
            #path (this shows that they are the same), just
            #return the output
            return outdir

    def parseEscapechars(self,file,quoteonly=False):

        if(quoteonly == False):
            #characters which must be escaped in the shell, note
            #"[" and "]" seems to be automatically escaped
            #(strange, look into this)
            escChars = ["\"","*",";"," ","'","(",")","&","`"]

            for char in escChars:
                #add an escape character to the character
                file = string.replace(file, char, '\\' + char)
        else:
            file = string.replace(file, "\"", "\\\"")

        return file


    def getfiles(self,path):
        infiles = os.listdir(path) #the files going in for reading
        outfiles = [] #the files going out in a list

        for file in infiles:
            if(os.path.isdir(os.path.join(path,file))):
                #recursive call
                outfiles = outfiles + self.getfiles(os.path.join(path,file))
            else:
                outfiles.append(os.path.join(path,file))

        return outfiles



#mp3 class:

class mp3:
    def __init__(self):
        pass #keep the constructor empty for now

    def generateLameMeta(self,metastring):
        tagstring = ""

        #pointer to the parseEscapechars method in the shell class
        parseEscapechars = shell().parseEscapechars

        #Dealing with genres defined within lame
        acceptable_genres=[\
        "A Cappella",\
        "Acid",\
        "Acid Jazz",\
        "Acid Punk",\
        "Acoustic",\
        "Alternative",\
        "Alt. Rock",\
        "Ambient",\
        "Anime",\
        "Avantgarde",\
        "Ballad",\
        "Bass",\
        "Beat",\
        "Bebob",\
        "Big Band",\
        "Black Metal",\
        "Bluegrass",\
        "Blues",\
        "Booty Bass",\
        "BritPop",\
        "Cabaret",\
        "Celtic",\
        "Chamber Music",\
        "Chanson",\
        "Chorus",\
        "Christian Gangsta Rap",\
        "Christian Rap",\
        "Christian Rock",\
        "Classical",\
        "Classic Rock",\
        "Club",\
        "Club-House",\
        "Comedy",\
        "Contemporary Christian",\
        "Country",\
        "Crossover",\
        "Cult",\
        "Dance",\
        "Dance Hall",\
        "Darkwave",\
        "Death Metal",\
        "Disco",\
        "Dream",\
        "Drum & Bass",\
        "Drum Solo",\
        "Duet",\
        "Easy Listening",\
        "Electronic",\
        "Ethnic",\
        "Eurodance",\
        "Euro-House",\
        "Euro-Techno",\
        "Fast-Fusion",\
        "Folk",\
        "Folklore",\
        "Folk/Rock",\
        "Freestyle",\
        "Funk",\
        "Fusion",\
        "Game",\
        "Gangsta Rap",\
        "Goa",\
        "Gospel",\
        "Gothic",\
        "Gothic Rock",\
        "Grunge",\
        "Hardcore",\
        "Hard Rock",\
        "Heavy Metal",\
        "Hip-Hop",\
        "House",\
        "Humour",\
        "Indie",\
        "Industrial",\
        "Instrumental",\
        "Instrumental Pop",\
        "Instrumental Rock",\
        "Jazz",\
        "Jazz+Funk",\
        "JPop",\
        "Jungle",\
        "Latin", \
        "Lo-Fi", \
        "Meditative", \
        "Merengue", \
        "Metal", \
        "Musical", \
        "National Folk", \
        "Native American", \
        "Negerpunk", \
        "New Age", \
        "New Wave", \
        "Noise", \
        "Oldies", \
        "Opera", \
        "Other", \
        "Polka", \
        "Polsk Punk", \
        "Pop", \
        "Pop-Folk", \
        "Pop/Funk", \
        "Porn Groove", \
        "Power Ballad", \
        "Pranks", \
        "Primus", \
        "Progressive Rock", \
        "Psychedelic", \
        "Psychedelic Rock", \
        "Punk", \
        "Punk Rock", \
        "Rap", \
        "Rave", \
        "R&B", \
        "Reggae", \
        "Retro", \
        "Revival", \
        "Rhythmic Soul", \
        "Rock", \
        "Rock & Roll", \
        "Salsa", \
        "Samba", \
        "Satire", \
        "Showtunes", \
        "Ska", \
        "Slow Jam", \
        "Slow Rock", \
        "Sonata", \
        "Soul", \
        "Sound Clip", \
        "Soundtrack", \
        "Southern Rock", \
        "Space", \
        "Speech", \
        "Swing", \
        "Symphonic Rock", \
        "Symphony", \
        "Synthpop", \
        "Tango", \
        "Techno", \
        "Techno-Industrial", \
        "Terror", \
        "Thrash Metal", \
        "Top 40", \
        "Trailer", \
        "Trance", \
        "Tribal", \
        "Trip-Hop", \
        "Vocal"]

        genre_is_acceptable = 0 #By default the genre is not acceptable
        current_genre = "" #variable stores current genre tag

        for genre in acceptable_genres:
            #print string.strip(metastring['GENRE'])+" ==> "+string.strip(genre)
            try:
                current_genre = string.upper(metastring['GENRE'].strip())
            except(KeyError):
                current_genre = "NO GENRE TAG"

            #case-insesitive comparison
            if current_genre == string.upper(genre.strip()):
                genre_is_acceptable = 1   #we can use the genre


        if genre_is_acceptable == 0:  #if genre cannot be used
            print "The Genre \"" + current_genre + "\" cannot be used with lame, setting to \"Other\" "
            metastring['GENRE'] = "Other"       #set GENRE to Other

        else:
            #Capitalise the Genre, as per lame requirements
            metastring['GENRE'] = string.capitalize(metastring['GENRE'])
            genre_is_acceptable = 0 #reset the boolean value for the next time


        try:
            tagstring = "--tt " + "\"" +  parseEscapechars(metastring["TITLE"],True) + "\""

        except(KeyError):
            pass #well we skip the comment field if is doesn't exist

        try:
            tagstring = tagstring + " --ta " + "\"" + parseEscapechars(metastring['ARTIST'],True) + "\""
        except(KeyError):
            pass

        try:
            tagstring = tagstring + " --tl " + "\"" + parseEscapechars(metastring['ALBUM'],True) + "\""
        except(KeyError):
            pass

        try:
            tagstring = tagstring + " --ty " + "\"" + parseEscapechars(metastring['DATE'],True) + "\""
        except(KeyError):
            pass
        try:
            tagstring = tagstring + " --tg " + "\"" + parseEscapechars(metastring['GENRE'],True) + "\""
        except(KeyError):
            pass

        try:
            tagstring = tagstring + " --tn " + "\"" + parseEscapechars(metastring['TRACKNUMBER'],True) + "\""
        except(KeyError):
            pass

        #COMMENTS AND CDDB ARE PLACED TOGETHER, as there exists no seperate
        #"CDDB Field" option for mp3. this is only if we have a comment to begin with
        try:
            tagstring = tagstring + " --tc " + "\"" + parseEscapechars(metastring['COMMENT'],True)

            try:
                tagstring = tagstring + "  || CDDB:" + parseEscapechars(metastring['CDDB'],True) + "\""
            except(KeyError):
                tagstring = tagstring + "\""    #close the final "comment field, without CDDB info

        except(KeyError):
        #this is for if we have a CDDB value
            try:
                tagstring = tagstring + " --tc  \"CDDB:" + parseEscapechars(metastring['CDDB'],True) + "\""
            except(KeyError):
                pass

        #Metadata population complete
        return tagstring

    def mp3convert(self,lameopts,infile,outfile):

        #give us an output file, full path, which is the same as the infile 
        #(minus the working directory path) and with the extension stripped
        #outfile = os.path.join(outdir+"/",os.path.split(infile)[-1]).strip(".flac")


	#pdb.set_trace()
        try:
            metastring = generateLameMeta(infile)
        except(UnboundLocalError):
            metastring = "" #If we do not get meta information. leave blank


        #Uncomment the line below if you want the file currently being
        #converted to be displayed
        #print parseEscapechars(infile)

        #rb stands for read-binary, which is what we are doing, with a 1024 byte buffer
        decoder = os.popen(flacpath + "flac -d -s -c " + shell().parseEscapechars(infile),'rb',1024)
        #wb stands for write-binary
        encoder = os.popen("%slame --silent %s - -o %s.mp3 %s" % (
            lamepath,
            lameopts,
            shell().parseEscapechars(outfile),
            metastring
            ) ,'wb',8192) 
#        encoder = os.popen(lamepath + "lame --silent " + lameopts + " - -o " +  shell().parseEscapechars(outfile) + ".mp3 " + metastring,'wb',8192) 


        for line in decoder.readlines(): #while data exists in the decoders buffer
            encoder.write(line) #write it to the encoders buffer

        decoder.flush() #if there is any data left in the buffer, clear it
        decoder.close() #somewhat self explanetory

        encoder.flush() #as above
        encoder.close()


#END OF CLASSES, Main body of code follows:


#Functions defined here
def header():
    return """
Flac2all python script, v1.3 . Copyright 2006-2012 Ziva-Vatra.com.
Licensed under the GPLv2 (http://www.ziva-vatra.com).
Project website: http://code.google.com/p/flac2all/

    """
def infohelp():
    return """
flac2all [convert type] [input dir] <options>
where \'convert type\' is one of:
\t [mp3]: convert file to mp3
\t [vorbis]: convert file to ogg vorbis
\t [flac]: convert file to flac
\t [aacplusNero]: convert file to aacplus using the proprietery (but excellent) Nero AAC encoder."""

def init():
    pass #do nothing, prolly remove this function
    #The above currently not used for anything useful
    #binpath = os.path.defpath #get the $PATH variable from the os

def encode_thread(current_file,filecounter,opts):

    #Recursive directory creation script, if selected
    if (opts['nodirs'] == False):
    #remove the dirpath placed in parameters, so that we work from that
    #directory
        current_file_local = current_file.replace(opts['dirpath'],'')
        outdirFinal = opts['outdir'] + os.path.split(current_file_local)[0]
	
        #if the path does not exist, then make it
        if (os.path.exists(outdirFinal) == False):
            #the try/catch here is to deal with race condition, sometimes one
            #thread creates the path before the other, causing errors
            try:
                #recursive, will make the entire path if required
                os.makedirs(outdirFinal)
            except(OSError):
                print "Directory already exists! Reusing..."

#this chunk of code provides us with the full path sans extension
    outfile = os.path.join(outdirFinal,os.path.split(current_file_local)[1])
    #return the name on its own, without the extension
    outfile = string.split(outfile, ".flac")[0]
    #This part deals with copying non-music data over (so everything that isn't
    #a flac file)
    if (string.lower(current_file [-4:]) != "flac"):
        if (opts['copy'] == True):
            print "Copying file #%d (%s) to destination" % (filecounter,current_file.split('/')[-1])
            os.system("cp \"%s\" \"%s\"" % (current_file,outdirFinal) )
            filecounter += 1

    if(opts['overwrite'] == False): #if we said not to overwrite files
        #if a file with the same filname/path does not already exist

        #the below is because "vorbis" is "ogg" extension, so we need the right extension
        #if we are to correctly check for existing files.
        if opts['mode'] == "vorbis":
            ext = "ogg"
        else:
            ext = opts['mode']

        if not (os.path.exists(outfile + "." + ext)):
            #[case insensitive] check if the last 4 characters say flac (as in
            #flac extension, if it doesn't, then we assume it is not a flac
            #file and skip it
            if (string.lower(current_file [-4:]) == "flac"):
                if (opts['mode'] != "test"):
                    print "converting file #%d to %s" % (filecounter,opts['mode'])
                else:
                    print "testing file #" + str(filecounter)

                if(opts['mode'] == "mp3"):
                    mp3Class.mp3convert(opts['lameopts'],current_file,outfile)
                elif(opts['mode'] == "flac"):
                    flacClass.flacconvert(opts['flacopts'],current_file,outfile)
                elif(opts['mode'] == "vorbis"):
                    vorbisClass.oggconvert(opts['oggencopts'],current_file,outfile)
                elif(opts['mode'] == "aacplusNero"):
                    aacpClass.AACPconvert(opts['aacplusopts'],current_file,outfile)
                elif(opts['mode'] == "test"):
                    flacClass.flactest(current_file, outfile)
                else:
                    print "Error, Mode %s not recognised. Thread dying" % opts['mode']
                    sys.exit(-2)
        else:
            print "file #%d exists, skipping" % filecounter 
    else:
        #[case insensitive] check if the last 4 characters say flac (as in flac
        #extension, if it doesn't, then we assume it is not a flac file and
        #skip it
        if (string.lower(current_file [-4:]) == "flac"):
            if (opts['mode'] != "test"):
                print "Converting file %d to %s" % (filecounter,opts['mode'])
            else:
                print "Testing file %d" % filecounter

            if(opts['mode'] == "mp3"):
                mp3Class.mp3convert(opts['lameopts'],current_file,outfile)
            elif(opts['mode'] == "flac"):
                flacClass.flacconvert(opts['flacopts'],current_file,outfile)
            elif(opts['mode'] == "vorbis"):
                vorbisClass.oggconvert(opts['oggencopts'],current_file,outfile)
            elif(opts['mode'] == "aacplusNero"):
                aacpClass.AACPconvert(opts['aacplusopts'],current_file,outfile)
            elif(opts['mode'] == "test"):
                flacClass.flactest(current_file, outfile)
            else:
                print "Error, Mode %s not recognised. Thread dying" % opts['mode']
                sys.exit(-2)

    return filecounter + 1 #increment the file we are doing

def generateLameMeta(mp3file):
    metastring  = flac().getflacmeta("\"" + mp3file + "\"")
    return mp3Class.generateLameMeta(metastring)
    #Metadata population complete

#END Functions


#Code starts here

#Variables are here

#***NOTE***
#if the *path variables below are left blank, then the script will try to find
#the programs automatically. only change these if the script does not work
#(or add the programs to your system $PATH variable)

flacpath="" #path to flac binary, blank by default
metaflacpath="" #path to metaflac, blank be default
oggencpath="" #path to oggenc binary, blank by default
lamepath="" #path to lame binary, blank by default
aacpath="" #path to aacplus binary, blank by default

opts = {
"outdir":"./", #the directory we output to, defaults to current directory
"overwrite":False, #do we overwrite existing files
"nodirs":False, #do not create directories (dump all files into single dir)
"threads":4, #How many encoding threads to run simultaniously.
"copy":False, #Copy non flac files (default is to ignore)
"buffer":2048, #How much to read in at a time
"lameopts":"--preset standard -q 0", #your mp3 encoding settings
"oggencopts":"quality=2", # your vorbis encoder settings
"flacopts":"-q 8", #your flac encoder settings
"aacplusopts":"-q 0.3 " 
}

#This area deals with checking the command line options,

from optparse import OptionParser

parser = OptionParser(usage=infohelp())
parser.add_option("-c","--copy",action="store_true",dest="copy",
      default=True,help="Copy non flac files across (default=False)")

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
parser.add_option("-t","--threads",dest="threads",default=2,
      help="How many encoding threads to run in parallel (default 2)")
parser.add_option("-n","--nodirs",dest="nodirs",action="store_true",
      default=False,help="Don't create Directories, put everything together")
##The below isn't used anymore, so removed as an option (to re-add in future?)
#parser.add_option("-B","--buffer",dest="buffer",metavar="size", 
#      help="How much we should buffer before encoding to mp3 (in KB). The larger "+
#           "you set this too, the more of the song will be buffered before "+
#           "encoding. Set it high enough and it will buffer everything to RAM"+
#           "before encoding.")

(options,args) = parser.parse_args()

#update the opts dictionary with new values
opts.update(eval(options.__str__()))

#convert the formats in the args to valid formats for lame and oggenc
opts['oggencopts'] = ' --'+' --'.join(opts['oggencopts'].split(':'))
#lame is stupid, it is not consistent, somteims using long opts, sometimes not
#so we need to specify on command line with dashes whether it is a long op or short
opts['lameopts'] = ' -'+' -'.join(opts['lameopts'].split(':'))

print header()
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

#start main code

#create instances of classes
mp3Class = mp3()
shellClass = shell()
flacClass = flac()
vorbisClass = vorbis()
aacpClass = aacplusNero()

filelist=shellClass.getfiles(opts['dirpath'])

flacnum = 0 #tells us number of flac media files
filenum = 0 #tells us number of files

#pdb.set_trace()
for files in filelist:
    filenum += 1
    #make sure both flac and FLAC are read
    if (string.lower(files [-4:]) == "flac"):
        flacnum += 1


print "There are %d files, of which %d are convertable FLAC files" % \
(filenum,flacnum)
 
if flacnum == 0:
    print "Error, we got no flac files. Are you sure you put in the correct directory?"
    sys.exit(-1) 
x = 0 #temporary variable, only to keep track of number of files we have done

#Why did we not use "for file in filelist" for the code below? Because this is
#more flexible. As an example for multiple file encoding simultaniously, we
#can do filelist.pop() multiple times (well, along with some threading, but its
#good to plan for the future.

import threading,time
#one thread is always for the main program, so if we want two encoding threads,
#we need three threads in total
opts['threads'] = int(opts['threads']) + 1

while len(filelist) != 0: #while the length of the list is not 0 (i.e. not empty)
    #remove and return the first element in the list
    current_file = filelist.pop()

    #threaded process, used by default

    threading.Thread(target=encode_thread,args=(
        current_file,
        x,
        opts
        )
    ).start()

    #Don't use threads, single process, used for debugging
    #x = encode_thread(current_file,nodirs,x,lameopts,flacopts,oggencopts,mode)
    while threading.activeCount() == opts['threads']:
        #just sit and wait. we check every tenth second to see if it has
        #finished
        time.sleep(0.1)
    x += 1

#END
