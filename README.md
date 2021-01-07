## News / Changes

### 05/01/2020 - v5.3 released

Happy new year everyone! I found out flac2all works on Apple Mac's as well, which was a nice development :-)

Changes in this version:

* Fixed issue 53
* Fixed issue 54
* Removed non ZMQ multiprocessing. Flac2all is now depedendent on ZMQ to work in clustered or non clustered mode. I discovered keeping two complete multiprocessing systems was causing more problems than it was solving, and a lot of bugs being raised by people were already fixed by virtue of the new structure. (issue #45)
* Multi-process copying now much faster (issue #45)
* Fixed multiple bugs (issue #45)
* As part of the work on issue #50, I've added two different modes for modified directories ("m", and "d"). "d" works exactly as before (puts all files in the output dir, no dir structure at all), while "m" does not create the mode dirs after the codec name. So you get the full dir structure, with a mix of codecs in each folder. Please note that this does change existing behaviour (If you just specify "-n" as before, you will get an error).

### 28/02/2020 - v5.2 released

* Fixed issue #44
* Fixed issue #45

### 23/01/2020 - v5.1 released

* Fixed issues caused by Python3 altering how it handles relative/absolute imports.

### 06/01/2020

Happy new year everyone! With the new year comes some big changes. Python2 was officially retired, and python3 is now the default for the forseeable future. With that, flac2all has been ported to Python3 (along with some new features/codecs). For details of what is new, please see "Details" below. The program has been tested over the last few months by me and seems good, but if come across any problems please raise a bug report.

### Older News/Changes
For older news/changes, please see [CHANGES.md](CHANGES.md)

## What is it
Started in 2003 as a simple flac to ogg vorbis script (written in bash), flac2all has grown into a python based, clustered parallel processing program that will convert your collection of FLAC files into various other formats (70+ formats if you meet all dependencies), complete with any tags that the source file had. Designed to be extended with new formats easily as time goes on, it is a utility for people with with large FLAC collections who also want a way to convert multiple files in parallel.

## Details

Version5 is the new release of flac2all. The decision to bump up a version number was primarily driven by the move to python3. Python2 is scheduled to be EOL after the 1st January 2020, and a lot of distros are already defaulting to python3 as the system Python interpreter. Rather than hold two versions of "version4", one for py2 and one for py3, it made more sense to bump the version number (thats what they are there for, after all).

Following on from my tradition of adding at least one major feature in major version upgrades. Version5 has the following new features:
* Support for ~72 new codecs via ffmpeg. Actual number of codecs subject to change based on what version of ffmpeg you have installed, and what options it is compiled with
* support for network distributed transcoding via ZeroMQ. This allows you to launch a single flac2all "master" on a machine, and then have flac2all "workers" running on other machines connect to it over a TCP connection. In other words, you can delegrate encoding tasks to multiple computers, each with multiple cores. For more details see the [Usage->Clustered](#clustered) section.
* An optional curses frontend when in clustered mode (selected with '-C' on command line), showing percentage complete, workers running and some other stats. Example can be seen here: ![Curses example](/resources/curses_example.png?raw=true "Curses Example").

## Dependencies
* Python >= 3.6
* Flac
* ZeroMQ (pyzmq)

## Optional dependencies
* Lame: for mp3 support
* Opus-tools: for opus support
* Vorbis-tools: for ogg support
* aac-enc for AAC support
* ffmpeg for supporting all the audio encoders it supports
* python-curses for the curses interface

## Packages for Distros

### Stable:

* ![logo](http://www.monitorix.org/imgs/archlinux.png "arch logo") For users of Arch Linux, flac2all is in the [AUR](https://aur.archlinux.org/packages/flac2all). Big Thanks to [Graysky](https://github.com/graysky2) for the AUR effort over the years!

* For the rest of you, there is a pip3 package available. You can install flac2all by running `pip3 install flac2all` as root, or `pip3 install flac2all --user` for a non root local install.
To upgrade to a new release you run the same commands as installation, but with `--upgrade` option set.

* If anyone has packaged flac2all for their OS/distro, feel free to get in touch and we can add it here

### Dev

At the moment there are no packages for the development branch.

There are however testing packages that I deploy to to the "test" pypi. These package versions have "test" prepended to their version number, and don't track the official version numbers. These versions may or may not work, as they are beta. You can install the test package to your home directory using `pip install -U --index-url https://test.pypi.org/simple/ flac2all`

If you want the bleeding edge, including to test different branches, follow the instructions under [Development](#development)

## Usage

Full information, including options and all current available conversion modes, can be found by running "flac2all -h".

### Non clustered (original) ###

Please see [USAGE.md](USAGE.md)

### <a name="clustered"> Clustered ###

Please see [README-CLUSTERED.md](USAGE-CLUSTERED.md)

### Use as a library ###

You can in fact make use of flac2all as a library, if you so desire. Each module can be used independently if you want to integrate flac2all into your own system. You just have to make sure the flac2all path is in your PYTHONPATH variable.

For example, to convert a flac to ogg vorbis:

```
from vorbis import vorbis

codec = vorbis(opts={"oggencopts":"quality=2", "overwrite=False"})
codec.convert("infile.flac", "outfile")

```

or to convert to mp3 (using lame):

```
from mp3 import lameMp3

codec = lameMp3(opts={"lameopts":"-preset standard:q 0", "overwrite=False"})
codec.convert("infile.flac", "outfile")

```

Notice you don't specify the outfile extension, that is added automatically.
.
## <a name="development">Development:</a>
If you want the bleeding edge version, best to check out the latest "version5" branch from git.
Generally development work will be done in branches then merged, so master should be functional.

Tu run the version straight from the git repo, cd to "flac2all_pkg", and then run "python ./\_\_init\_\_.py -h". The rest should work as normal.

Since version 4, all codecs are split into their own modules, which allows developers to easily add new codecs. The internal function tables stay the same, meaning that as long as you follow the structure of the main functions, you can add any codec you want.

The easiest way to get started writing a codec module is to look at an existing one. I would recommend "flac.py", as it shows both encoding and decoding, and flac to flac conversion was very simple to implement. A more complex example is the mp3 module, which shows how complex things can get.

### Fixed branches
There are some branches that are considered "fixed". This means that they tend to be self contained, and they need not track any other branch. A list of these branches as as follows:

* master: Main branch, where final merges and tests are done prior to tagging and deployment. From here we generate the releases.
* version5: The current development branch, where changes are made, pulls merged and tested, prior to merge with master for release.
* version4: The old stable branch. No active development, but kept for historic/archival purposes.
* version3: The old stable branch. No active development, but kept for historic/archival purposes.
* version2: The old stable branch. No active development, but kept for historic/archival purposes.


### Dev etiquette
If you wish to contribute to flac2all, I ask that you keep to the following guidelines:

* If you want to extend/modify flac2all, checkout the latest copy of the repo, switch to the development branch, and then make your own branch, develop/test/debug until ready, then issue a pull request. Do not start hacking away on the master branch directly.

* The goal of the master branch is to be the final stage before a tagged release. As such, any code merged into master should not break things badly. All testing and debugging should be done on your branch prior to merge.

* If you want to add a new codec to flac2all, please keep it all in one single file. This is how the rest of flac2all is written. Some codecs (like AAC) actually have two implementations in one module (Both NeroAAC and fdk-aac). It keeps things easier to manage if each conversion codec is its own module.

* Keep to the same internal API as the other modules. If you strongly feel that the API is missing some functionality critical to making your module work, raise an issue on this project page and we can discuss the situation.

* Please raise an issue if you intend to place a hard dependency on a third party package (that isn't a codec). If you want to make use of a third party library it would be best to discuss before time is put into development.


## Raising a bug report

Before you raise a bug report, please test with the latest version from git. Sometimes distro packages lag the latest stable by a couple of versions, so you may hit bugs that have already been fixed.

## Examples in use

* Here is a video of flac2all (v3) saturating a 16 core machine with conversions: [[synapse-16_threads](https://www.youtube.com/watch?v=pXSpPjWtSJc)]
