# vim ts=4 expandtab si 

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


