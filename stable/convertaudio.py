#!/usr/bin/python
# vim: ts=4 autoindent expandtab

version="1.2.625"
"""
============================================================================================

Python script for conversion of flac files to flac/mp3/ogg.

Copyright 2006, Belgrade (www.ziva-vatra.com, mail: ziva_vatra@mailshack.com)

Licensed under the GPLv2. Do not remove any information from this header (or the header itself). If you have modified this code, feel free to add your details below this (and by all means, mail me, I like to see what other people have done)

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

============================================================================================



	
	
"""

import sys
import os
import string

#Variables are here

#***NOTE***
#if the *path variables below are left blank, then the script will try to find the programs automatically. only change these if the script does not work (or add the programs to your system $PATH variable)
 
flacpath="" #path to flac binary, blank by default
metaflacpath="" #path to metaflac, blank be default
oggencpath="" #path to oggenc binary, blank by default
lamepath="" #path to lame binary, blank by default

lameopts="--preset medium -q 2 " #your settings for the lame mp3 encoder
flacopts="-q 8" #your settings for the flac encoder
oggencopts= "-q 1" #your setting for the ogg vorbis encoder here

outdir="./" #the directory we output to, defaults to current directory
overwrite=False #do we overwrite existing files
nodirs=False #do not create directories (dump all files into single dir)
threads=2 #How many encoding threads to run simultaniously.
	
#CODE


#Class that deals with vorbis
class vorbis:
    def oggconvert(self,oggencopts,infile,outdir):
        outfile = os.path.join(outdir,os.path.split(infile)[1])
        outfile = string.split(outfile, "flac")[0] #return the name on its own, without the extension
        outfile = outfile[:-1] #after the previous code, we end up with a "." left, which we remove here

        #oggenc automatically parses the flac file + metadata, quite wonderful really, we don't need to do anything here
        os.system("oggenc " + oggencopts + " -Q -o " + shell().parseEscapechars(outfile + ".ogg") + " " + shell().parseEscapechars(infile))
        
        #Uncomment the line below if you want the file currently being converted to be displayed
        #print parseEscapechars(infile)

#Class that deals with FLAC

class flac:
    def flacconvert(lameopts, infile, outdir):
        print "converting flac"

    def getflacmeta(self,flacfile):
        flacdata = os.popen(metaflacpath + "metaflac --list --block-number 2 " + flacfile)# the FLAC file format states that song info will be stored in block 2, so we do not look at the other blocks
    
        datalist = [] #init a list for storing all the data in this block
        commentlist = {} #this dictionary (note different brackets) will store only the comments for the music file
    
        for data in flacdata.readlines():
            data = string.strip(data) #get rid of any whitespace from the left to the right 
            if(data[:8] == "comment["): #check if the tag is a comment field (shown by the first 7 chars spelling out "comment")
                datalist.append(string.split(data,":"))

        for data in datalist:
            comment = string.split(data[1],"=") #split according to [NAME]=[VALUE] structure
            comment[0] = string.strip(comment[0])
            comment[1] = string.strip(comment[1])
        #convert to upper case
            comment[0] = string.upper(comment[0]) # we want the key values to always be the same case, we decided on uppercase (whether the string is upper or lowercase, is dependent on the tagger used)
            commentlist[comment[0]] = comment[1] #assign key:value pair, comment[0] will be the key, and comment[1] the value
        return commentlist

    def flactest(self,file,outfile):
        test = os.popen(flacpath + "flac -s -t \"" + file + "\"",'r')
        #filepath = generateoutdir(file,outfile) + "results.log"
    
    #if (os.path.exists(filepath)):
    #	os.remove(filepath)

		#os.mknod(filepath,0775)
		#out = os.popen(filepath,'w')
	
		#results = ""
	
		#for line in test.readlines():
#			print "++++++++++++" + line
#			results = line
		
#		out.write(results)
	
#	print "==============" + results
#	test.flush()
        test.close()

#	out.flush()
#	out.close()





#Class dealing with shell/output related things:
	
class shell:	
	def generateoutdir(self,indir, outdir):
		if (string.find(os.path.split(indir)[0], dirpath) != -1): #if we find the dirpath in the current output path, we replace it with the new output path. (so that we don't get /mnt/convertedfromflac/mnt/flac/[file].mp3, in this case "/mnt/" exist in both)
			return  string.replace(os.path.split(indir)[0], dirpath, outdir)
		else: #if we do not find an instance of dir path in output path (this shows that they are the same), just return the output
			return outdir

	def parseEscapechars(self,file,quoteonly=False):

		if(quoteonly == False):			
			escChars = ["\"","*",";"," ","'","(",")","&",] #characters which must be escaped in the shell, note "[" and "]" seems to be automatically escaped (strange, look into this)
		
			for char in escChars:
				file = string.replace(file, char, '\\' + char) #add an escape character to the character
	
		else:
			file = string.replace(file, "\"", "\\\"")
	
		return file
		
		
	def getfiles(self,path):
		infiles = os.listdir(path) #the files going in for reading
		outfiles = [] #the files going out in a list
		
		for file in infiles:
			if(os.path.isdir(os.path.join(path,file))):
				outfiles = outfiles + self.getfiles(os.path.join(path,file)) #recursive call
			else:
				outfiles.append(os.path.join(path,file))
		
		return outfiles



#mp3 class:
	
class mp3:
    def __init__(self):
        pass #keep the constructor empty for now

    def generateLameMeta(self,metastring):	
        tagstring = ""
        parseEscapechars = shell().parseEscapechars #pointer to the parseEscapechars method in the shell class
        
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
            #print string.strip(metastring['GENRE']) + " ==> " + string.strip(genre)
            try:
                current_genre = string.upper(string.strip(metastring['GENRE']))
            except(KeyError):
                current_genre = "NO GENRE TAG" 
            
            if current_genre == string.upper(string.strip(genre)):  #case-insesitive comparison
                    genre_is_acceptable = 1   #we can use the genre


        if genre_is_acceptable == 0:  #if genre cannot be used
            print "The Genre \"" + current_genre + "\" cannot be used with lame, setting to \"Other\" "
            metastring['GENRE'] = "Other"	#set GENRE to Other
            
        else:
            metastring['GENRE'] = string.capitalize(metastring['GENRE']) #Capitalise the Genre, as per lame requirements 
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
        
    #COMMENTS AND CDDB ARE PLACED TOGETHER, as there exists no seperate "CDDB Field" option for mp3. this is only if we have a comment to begin with
        try:
            tagstring = tagstring + " --tc " + "\"" + parseEscapechars(metastring['COMMENT'],True) 

            try:
                tagstring = tagstring + "  || CDDB:" + parseEscapechars(metastring['CDDB'],True) + "\"" 
            except(KeyError):
                tagstring = tagstring + "\"" 	#close the final "comment field, without CDDB info

        except(KeyError):
        #this is for if we have a CDDB value
            try:
                tagstring = tagstring + " --tc  \"CDDB:" + parseEscapechars(metastring['CDDB'],True) + "\""
            except(KeyError):
                pass

        #Metadata population complete
        return tagstring
        
    def mp3convert(self,lameopts,infile,outdir):

        outfile = os.path.join(outdir,os.path.split(infile)[1])
        outfile = string.split(outfile, "flac")[0] #return the name on its own, without the extension
        outfile = outfile[:-1] #after the previous code, we end up with a "." left, which we remove here
            
        try:
            metastring = generateLameMeta(infile)
        except(UnboundLocalError):
            metastring = "" #If we do not get meta information. leave blank


        #Uncomment the line below if you want the file currently being converted to be displayed
        #print parseEscapechars(infile)

        decoder = os.popen(flacpath + "flac -d -s -c " + shell().parseEscapechars(infile),'rb',1024) #rb stands for read-binary, which is what we are doing, with a 1024 byte buffer
        encoder = os.popen(lamepath + "lame --silent " + lameopts + " - -o " +  shell().parseEscapechars(outfile) + ".mp3 " + metastring,'wb',1024) #wb stands for write-binary



        for line in decoder.readlines():  #while data exists in the decoders buffer
            encoder.write(line)	  #write it to the encoders buffer

        decoder.flush() #if there is any data left in the buffer, clear it
        decoder.close() #somewhat self explanetory

        encoder.flush() #as above
        encoder.close()


#END OF CLASSES, Main body of code follows:


#Functions defined here
	
def infohelp():
	sys.stdout.write("Convert Audio python script, version "+version+". Copyright 2006 Z.V . Licensed under the GPLv2 (http://www.ziva-vatra.com) \n \n usage: convertaudio.py [convert type] [input dir] \n where \'convert type\' is one of: \n \t [mp3]: convert file to mp3 \n \t [vorbis]: convert file to vorbis \n \t [flac]: convert file to flac \n")
			

def init():
	rlimit = sys.getrecursionlimit() #get the recursion limit of the os, this dictates how far into a directory tree we can go
	print "your OS supports a directory depth of " + str(rlimit) + " folders"
	#The above currently not used for anything useful		
	#binpath = os.path.defpath #get the $PATH variable from the os
	
def encode_thread(current_file,nodirs,x,lameopts,flacopts,oggencopts,mode):

#Recursive directory creation script, if selected
    if (nodirs == False):	 
        current_file_local = current_file.replace(dirpath,'') #remove the dirpath placed in parameters, so that we work from that directory
        outdirFinal = outdir + os.path.split(current_file_local)[0]
        outdirFinal = outdir + dirpath + outdirFinal


        if (os.path.exists(outdirFinal) == False): #if the path does not exist, then make it
            #the try/catch here is to deal with race condition, sometimes one thread creates the path before the other, causing errors
            try:
                os.makedirs(outdirFinal) #recursive, will make the entire path if required
            except(OSError):
                print "Directory already exists! Reusing..."
		
#this chunk of code provides us with the full path sans extension
    outfile = os.path.join(outdirFinal,os.path.split(current_file_local)[1])
    outfile = string.split(outfile, ".flac")[0] #return the name on its own, without the extension
    if mode == "vorbis":
        mode = "ogg" #internally "vorbis" is referred to as "ogg", this is a quick hack to fix it until we redo those chunks properly
        
    if(overwrite == False): #if we said not to overwrite files
        if not (os.path.exists(outfile + "." + mode)): #if a file with the same filname/path does not already exist		
            if (string.lower(current_file [-4:]) == "flac"): #[case insensitive] check if the last 4 characters say flac (as in flac extension, if it doesn't, then we assume it is not a flac file and skip it

                if (mode != "test"):
                    print "converting file #" + str(x) + " to " + mode
                else:
                    print "testing file #" + str(x)	

                if(mode == "mp3"):
                    mp3Class.mp3convert(lameopts,current_file,outdirFinal)
                elif(mode == "flac"):
                    flacClass.flacconvert(flacopts,current_file,outdirFinal)
                elif(mode == "ogg"):
                    vorbisClass.oggconvert(oggencopts,current_file,outdirFinal)
                elif(mode == "test"):
                    flacClass.flactest(current_file, outdirFinal)			

        else:
            print "file #" + str(x) + " exists, skipping"
    else:
        if (string.lower(current_file [-4:]) == "flac"): #[case insensitive] check if the last 4 characters say flac (as in flac extension, if it doesn't, then we assume it is not a flac file and skip it
                
                if (mode != "test"):
                    print "converting file #" + str(x) + " to " + mode
                else:
                    print "testing file #" + str(x)	
                    
                if(mode == "mp3"):
                    mp3Class.mp3convert(lameopts,current_file,outdirFinal)
                elif(mode == "flac"):
                    flacClass.flacconvert(flacopts,current_file,outdirFinal)
                elif(mode == "ogg"):
                    vorbisClass.oggconvert(oggencopts,current_file,outdirFinal)
                elif(mode == "test"):
                    flacClass.flactest(current_file, outdirFinal)		
                    

    return x + 1 #increment the file we are doing


		

	
def generateLameMeta(mp3file):	
	metastring  = flac().getflacmeta("\"" + mp3file + "\"")	
	return mp3Class.generateLameMeta(metastring)
	#Metadata population complete

#END Functions



#Code starts here


#This area deals with checking the command line options, TODO: replace with proper command switches
try:
	mode = sys.argv[1]

except(IndexError): #if no arguments specified
	print "No mode specified!"
	print ""
	infohelp()
	sys.exit(-1) #quit the program with non-zero status

try:
	dirpath = sys.argv[2]
	
except(IndexError):
	print "No directory specified!"
	print ""
	infohelp()
	sys.exit(-1) #quit the program with non-zero status
	

#end command line checking


#start main code
init()

#create instances of classes
mp3Class = mp3()
shellClass = shell()
flacClass = flac()
vorbisClass = vorbis()

filelist=shellClass.getfiles(dirpath)

flacnum = 0 #tells us number of flac media files
filenum = 0 #tells us number of files

for files in filelist:
	filenum = filenum + 1
	if (string.lower(files [-4:]) == "flac"): #make sure both flac and FLAC are read
		flacnum = flacnum + 1
	
print "there are " + str(filenum) + " files, of which " + str(flacnum) +  " are convertable flac files"


x = 0 #temporary variable, only to keep track of number of files we have done

#Why did we not use "for file in filelist" for the code below? Because this is more flexible. As an example for multiple file encoding simultaniously, we can do filelist.pop() multiple times (well, along with some threading, but its good to plan for the future.

import threading,time
threads = threads + 1 #one thread is always for the main program, so if we want two encoding threads, we need three threads in total

while len(filelist) != 0: #while the length of the list is not 0 (i.e. not empty) 
	current_file = filelist.pop() #remove and return the first element in the list	
	threading.Thread(target=encode_thread,args=(current_file,nodirs,x,lameopts,flacopts,oggencopts,mode)).start()

        #Don't use threads, single process, used for debugging
	#x = encode_thread(filelist,nodirs,x,lameopts,flacopts)
	while threading.activeCount() == threads:
		time.sleep(0.1) #just sit and wait. we check every tenth second to see if it has finished
	x = x + 1

#END	
