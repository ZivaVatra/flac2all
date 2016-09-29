## What is it
Flac2All is a multi-threaded script that will convert your collection of FLAC files into either Ogg Vorbis, MP3 (with the Lame encoder), or FLAC, complete with any tags that the source file had. Utility for people with with large FLAC collections who also want a lossy version for portable media players.

## Dependencies
* Python >2.7
* Flac

## Optional dependencies
* Lame: for mp3 support
* Opus-tools: for opus support
* Vorbis-tools: for ogg support
* neroAAC and/or fdk-aac for AAC support

## Packages for Distros
* ![logo](http://www.monitorix.org/imgs/archlinux.png "arch logo")Arch Linux: in the [AUR](https://aur.archlinux.org/packages/flac2all).

## Usage
flac2all [convert type] [input dir]

[convert type] may be [mp3] or [vorbis] or [flac]

## Development

There is no active development on the 3.x version. Only bug fixes. If you want to help with development, please checkout the "unstable" branch and help out with version 4.


## Video of Flac2all in action
Here is a video of flac2all running on a dual quad system (2 CPUs with 8 physical cores and 8 HT cores = 16 threads totally).  It happily saturates all 16 cores:

[![screenshot](http://s27.postimg.org/7r1wrz3sz/synapse_16_threads.png)](https://www.youtube.com/watch?v=pXSpPjWtSJc)
