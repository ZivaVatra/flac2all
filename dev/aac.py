# vim: ts=4 ai expandtabi list

#Class that deals with AAC+ 

#For the binary-only Nero AAC encoder
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


