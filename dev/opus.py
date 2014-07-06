# vim: ts=4 ai expandtab

#Class that deals with the opus codec
class opus:
    def opusconvert(self,opusencopts,infile,outfile):
        #Placeholder until we work out how opus actually works
        #and what is needed before we can write it
        return None

        os.system("%sopusenc %s -Q -o %s.opus %s" %
            (
            opusencpath,
            opusencopts,
            shell().parseEscapechars(outfile),
            shell().parseEscapechars(infile)
         
            )
        )

