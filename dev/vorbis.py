# vim: ts=4 autoindent expandtab

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

