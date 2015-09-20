# Introduction #

Flac2All is a multi-threaded script that will convert your collection of FLAC files into either Ogg Vorbis, AAC+ (No tagging support), MP3 (with the Lame encoder), Opus (with or without tag support, depending on your opus codec) or FLAC, complete with any tags and identical file/folder structure. The script has been stable for about a year now, and it has been known to saturate 16-core machines with parallel conversions. It is useful for people with with large FLAC collections who also want a lossy version for portable media players. If wanted, the script can perform updates by skipping already converted files.

This program has been around in some form or another since 2005, with constant refinement.

The project has a freshmeat page at http://freshmeat.net/projects/flac2all

Originally it was hosted on this page: [Flac2All](http://www.ziva-vatra.com/index.php?aid=23&id=U29mdHdhcmU=) but is now hosted on this google code page.

# Details #

  * Python based
  * Can convert from FLAC to mp3,ogg vorbis, aac+, opus or FLAC
  * Multiprocess support, for parallel conversion (excellent for multi CPU setups)
  * Tags are transferred along with the conversion (except AAC+)
  * Optionally non-flac file (like cue,jpg etc...) can be copied over (with input filtering)
  * Tested on Linux, should work on other systems with Python + required dependencies
