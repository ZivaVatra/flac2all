# Requirements #

The current stable (v3) depends on the following:
  * Python 2.6+ (no 3.0 support)
  * FLAC command line program (including supplementary progs,e.g. metaflac)
  * LAME command line program (if you want mp3 encoding)
  * vorbis-tools (oggenc + friends, if you want vorbis encoding)
  * Nero's AAC+ encoder, cmdline version (if you want to AACplus encoding)

The depreciated version 2 of the script depends on the same as above, except:
  * Python 2.5+, but not 3.0.
  * No need for the AAC+ Encoder


These programs should ideally be available in your PATH variable, if they are not, then edit the script's path variables to point to the executables.

On v3, the following would need to be changed for non-PATH binaries:
```
   flacpath="" #path to flac binary, blank by default
   metaflacpath="" #path to metaflac, blank be default
   oggencpath="" #path to oggenc binary, blank by default
   lamepath="" #path to lame binary, blank by default
   aacpath="" #path to aacplus binary, blank by default
```

# Usage #

## Development version ##

By virtue of being in development, the usage for this keeps changing. Check out the dev trunk, and try "-h" for info. Otherwise dig through the code for some insignt, or email me :)

## version 3 - Current stable ##

Run flac2all.py with "-h" to get an overview, like so:
```
Usage: 
flac2all [convert type] [input dir] <options>
where 'convert type' is one of:
	 [mp3]: convert file to mp3
	 [vorbis]: convert file to ogg vorbis
	 [flac]: convert file to flac
	 [aacplusnero]: (NO TAGGING SUPPORT) convert file to aacplus using the proprietery (but excellent) Nero AAC encoder.

Options:
  -h, --help            show this help message and exit
  -c, --copy            Copy non flac files across (default=False)
  -v OGGENCOPTS, --vorbis-options=OGGENCOPTS
                        Colon delimited options to pass to oggenc,for example:
                        'quality=5:resample 32000:downmix:bitrate_average=96'.
                        Any oggenc long option (one with two '--' in front)
                        can be specified in the above format.
  -l LAMEOPTS, --lame-options=LAMEOPTS
                        Options to pass to lame, for example:
                        '-preset extreme:q 0:h:-abr'. Any lame option can be
                        specified here, if you want a short option (e.g. -h),
                        then just do 'h'. If you want a long option (e.g. '--
                        abr'), then you need a dash: '-abr'
  -a AACPLUSOPTS, --aacplus-options=AACPLUSOPTS
                        AACplus options, currently only bitrate supported.
                        e.g: " -a 64 "
  -o DIR, --outdir=DIR  Set custom output directory (default='./')
  -f, --force           Force overwrite of existing files (by default we skip)
  -t THREADS, --threads=THREADS
                        How many threads to run in parallel (default:
                        autodetect [found 2 cpu(s)] )
  -n, --nodirs          Don't create Directories, put everything together
```

  * As you can see, there far more options now, most are self explanatory, the OGGENCOPTS/LAMEOPTS bit takes some getting used to. Basically, the script is parsing what you give in colon delimited format, and expand it into arguments to pass to the encoders, you can pass anything you like here, which means you can break the encode chain if you pass incorrect parameters.

  * If you are getting failures/errors in your encode, try without custom opts, and see if it still fails.

  * The "-t" for specifying threads is no longer required. The script will automatically detect how many CPU's you have, and adjust accordingly. Only use this if the script got it wrong, or if you want to disable auto-detection and use whatever you want.

  * By default the script will create a mirror of your flac folder structure, with the lossy versions in there. If however you want to just stick every file in the output dir with no structure, select nodirs "-n".


## version 2 (was 1.2) - Depreciated ##

The original script, when ran, gives you the following output:
```
No mode specified!

Convert Audio python script, v1.0 alpha. Copyright 2006 Ziva-Vatra. Licensed under the GPLv2 (http://ziva-vatra.com) 
 
 usage: convertaudio.py [convert type] [input dir] 
 where 'convert type' is one of: 
 	 [mp3]: convert file to mp3 
 	 [ogg]: convert file to vorbis 
 	 [flac]: convert file to flac 
```

Pretty self explanatory, and that was all the options you could specify on the command line.

If you wanted to make any changes, you would have to edit the script yourself. Here is an example showing the variables you can tweak:
![http://www.ziva-vatra.com/imagecompatibility.php?render=c2NyMkAyMw==%22&forgoogle=itisa.png](http://www.ziva-vatra.com/imagecompatibility.php?render=c2NyMkAyMw==%22&forgoogle=itisa.png)

The script is pretty well commented, so you should be able to work out what needs to be set to get it exactly the way you want. If you have trouble, just email me to let me know (or you can create an issue on the tracker).