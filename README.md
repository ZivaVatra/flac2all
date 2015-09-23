## What is it
Flac2All is a multi-threaded script that will convert your collection of FLAC files into either Ogg Vorbis, MP3 (with the Lame encoder), or FLAC, complete with any tags that the source file had. Utility for people with with large FLAC collections who also want a lossy version for portable media players.

## Dependencies
* Python >2.7
* Flac

## Optional dependencies
* Lame: for mp3 support
* Opus-tools: for opus support
* Vorbis-tools: for ogg support

## Usage
flac2all [convert type] [input dir]

[convert type] may be [mp3] or [vorbis] or [flac]
