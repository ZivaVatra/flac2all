## What is it
Flac2All is a multi-threaded script that will convert your collection of FLAC files into either Ogg Vorbis, MP3 (with the Lame encoder), or FLAC, complete with any tags that the source file had. Utility for people with with large FLAC collections who also want a lossy version for portable media players.

## Details

This is the development branch, for the new version of flac2all. At the moment it is alpha status, and revision to revision may break.


## Dependencies
* Python >2.7
* Flac

## Optional dependencies
* Lame: for mp3 support
* Opus-tools: for opus support
* Vorbis-tools: for ogg support
* neroAAC and/or fdk-aac  for AAC support


## Packages for Distros
At the moment, the development version does not have any packages.


## Usage
Unlike the 3.x version, this one allows multiple codecs to be specified on the command line, and in the target folder it will create a subfolder for each codec. So for example:

python ./\_\_main\_\_.py vorbis,mp3 --vorbis-options='quality=2' -o ./fromFlac/ /path/to/flacc/Lossless/

will create the following structure:

./fromFlac/vorbis
./fromFlac/mp3

and will encode to both formats simulatniously. 

## Developing

Main goal of version 4 was to split the codecs into their own modules, which should allow developers to easily add new codecs. The internal function tables stay the same, meaning that as long as you follow the structure of the main functions, you can add any codec you want. 

The structure is not formalised yet, so may change, but I think there will be no radical changes, more incremental improvements as time goes on. 


## Packaging/Distribution

Unlike the previous versions up to 3.x, version 4 is not a single file, but multiple files. As such a way of packaging and distributing the program is needed. 

There are two python systems, easy_install (setuptools) and pip (PyPi). Not sure which to use atm, but apparently pip is the default package index for the Python community, so once we start making releases, we will probably use pip (unless there are any strong objections to it). 



