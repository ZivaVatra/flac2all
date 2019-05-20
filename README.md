## News

### 19/05/2019
* Push tag 4.3, with release to pypy

### 14/05/2019
* Fixed flac testing. It now outputs a "test" folder with flac "ana" files, along with the usual conversion log.

### 13/05/2019
* Fixed version detection for opus
* Fixed DivbyZero error in summary calculations
* Commencing migration to python3. As python2 is scheduled to be EOL 1st Jan 2020, development has shifted to python3.
As such, a new branch, version5, has been created to deal with future development.

As of this release, version4 of flac2all will be in "maintenance mode". No new features will be added, and only bugfixes will be released. New developments, features and major refactors will be on the version5 branch. At the moment flac2all is working on python3, IMO better than on python2, just because in the course of refactoring I have improved things.

Unlike the previous transition (v3 to v4), there is no major rewrite or restructure of the code base. The main reason I am thinking to move to version5 is to make a clear cut between python2 and python3, due to the lack of backwards compatibility. Easier than trying to deal with which version4 a bug is being triggered on, and generally keeping track of two versions of "version4".


### 05/03/2019

* Version 4.2 pushed to pypi
* Changes:
  - Fix for issue #38: Skipping does not work if mode name does not equal file extension

### 18/02/2019

* Version 4.1 pushed to pypi.
* AUR (Arch Linux) package updated (thanks to Graysky)


## What is it
Started in 2003 as a single-threaded flac to ogg vorbis script, flac2all has grown into a parallel processing program that will convert your collection of FLAC files into various other formats (currently mp3,ogg vorbis,opus,flac and aac), complete with any tags that the source file had. Designed to be extended with new formats easily as time goes on, it is a utility for people with with large FLAC collections who also want a way to convert multiple files in parallel.
## Details

After many years of (admittadly slow) development, version 4 is finally ready for general release.

This is the new stable version, replacing V3. Its been in "Beta" for a few years now, and now I feel ready to release it to the public. Please test and raise any issues you find.

The older v3 releases are also still available in the downloads area, as well as the "version3" branch of git, if v4 isn't working for you.

Biggest changes for this version are:
* A rewrite of the multi process core
* The ability to encode multiple codecs in parallel (e.g. mp3 and vorbis at once)
* Logging support, plus statistical capture and summary at the end
* Break up of code from one monolithic file into smaller core files, and files for codecs, for easier maintenance and development/extension
* Proper packaging, with future releases going via PyPi

## Dependencies
* Python >2.7
* Flac

## Optional dependencies
* Lame: for mp3 support
* Opus-tools: for opus support
* Vorbis-tools: for ogg support
* neroAAC and/or fdk-aac for AAC support


## Packages for Distros

### Stable:
There is a pip package available. You can install flac2all by running  "pip install flac2all" as root, or "pip install flac2all --user" for a non root local install.

To upgrade to a new release you run the same commands as installation, but with "--upgrade" option set.

## Development:
If you want the bleeding edge version, best to check out the latest "version4" branch from git.
Generally development work will be done in branches then merged, so master should be functional.

Tu run the version straight from the git repo, cd to "flac2all_pkg", and then run "python ./\_\_init\_\_.py -h". The rest should work as normal.

The main goal of version 4 was to split the codecs into their own modules, which should allow developers to easily add new codecs. The internal function tables stay the same, meaning that as long as you follow the structure of the main functions, you can add any codec you want.

The easiest way to get started writing a codec module is to look at an existing one. I would recommend "flac.py", as it shows both encoding and decoding, and flac to flac conversion was very simple to implement. A more complex example is the mp3 module, which shows how complex things can get.

### Fixed branches
There are some branches that are considered "fixed". This means that they tend to be self contained, and they need not track any other branch. A list of these branches as as follows:

* master: Main branch, where final merges and tests are done prior to tagging and deployment. From here we generate the releases.
* version5: The new development branch, where the next generation of flac2all is being made. Check out the README on this branch for the full details, but one core goal with this version is the migration to python3
* version4: The current stable branch. No new features, only bugfixes here.
* version3: The old stable branch. No active development, but kept in case someone needs/wants access to the old version

### Dev etiquette
If you wish to contribute to flac2all, I ask that you keep to the following guidelines:

* Only do new development on version5 branch. Python2 is EOL at the end of 2019, and we are migrating to python3 for all future development.

* If you want to extend/modify flac2all, checkout the latest copy of the repo, switch to the development branch (currently "version5"), and then make your own branch, develop/test/debug until ready, then issue a pull request. Do not start hacking away on the master branch directly.

* The goal of the master branch is to be the final stage before a tagged release. As such, any code merged into master should not break things badly. All testing and debugging should be done on your branch prior to merge.

* If you want to add a new codec to flac2all, please keep it all in one single file. This is how the rest of flac2all is written. Some codecs (like AAC) actually have two implementations in one module (Both NeroAAC and fdk-aac). It keeps things easier to manage if each conversion codec is its own module.

* Keep to the same internal API as the other modules. If you strongly feel that the API is missing some functionality critical to making your module work, raise an issue on this project page and we can discuss the situation.

* Please raise an issue if you intend to place a hard dependency on a third party package (that isn't a codec). If you want to make use of a third party library it would be best to discuss before time is put into development.

## Known bugs/issues and TODOs

* using "ctrl-c" to terminate does not exit cleanly. Plus you have to hit ctrl-c multiple times to terminate flac2all.
* following on from above, when terminated the script leaves a bunch of tmpfiles. We need to clean up properly
* "test" mode is not implemented yet.

## Raising a bug report

Before you raise a bug report, please test with the latest version from git. Sometimes distro packages lag the latest stable by a couple of versions, so you may hit bugs that have already been fixed.

## Examples in use

* Here is a video of flac2all (v3) saturating a 16 core machine with conversions: [[synapse-16_threads](https://www.youtube.com/watch?v=pXSpPjWtSJc)]

## Usage

Full information, including options and all current available conversion modes, can be found by running "flac2all -h".

Attempts were made to keep version4 backwards compatible with the options from version3. In theory you should be able to run the exact same commands and flac2all v4 should still work as expected.

There are some differences though. Unlike the 3.x version, version 4 allows multiple codecs to be specified on the command line, and in the target folder it will create a subfolder for each codec. So for example:

``` flac2all vorbis,mp3 --vorbis-options='quality=2' -o ./fromFlac/ /path/to/flac/Lossless/ ```

will create the following structure:

```
./fromFlac/vorbis
./fromFlac/mp3
```
and will encode to both formats simultaniously.

In addition, a conversion log is created, and a summary is printed out when completed. An example (with partial failures) looks like this:

```
================================================================================
| Summary
--------------------------------------------------------------------------------

Total files on input: 152
Total files actually processed: 114
--
Execution rate: 75.00 %


Files we managed to convert successfully: 108
Files we failed to convert due to errors: 6
--
Conversion error rate: 5.26 %


For mode: mp3
Total execution time: 515.2738 seconds
Per file conversion:
	Mean execution time: 13.5598 seconds
	Median execution time: 12.3224 seconds


For mode: vorbis
Total execution time: 434.2878 seconds
Per file conversion:
	Mean execution time: 11.4286 seconds
	Median execution time: 10.8245 seconds


For mode: opus
Total execution time: 373.4832 seconds
Per file conversion:
	Mean execution time: 9.8285 seconds
	Median execution time: 9.9392 seconds

For mode: aacplus
No data (no files converted)

Writing log file (./fromFlac/conversion_results.log)
Done!
We had some failures in encoding :-(
Writing out error log to file ./conversion_results.log
Done! Returning non-zero exit status!

```

The "conversion_results.log" file is a simple CSV, with details of each file processed. Every successful process is marked "SUCCESS", so if you want to see the unsuccessful list, you can just grep it out, like so:

```
~$grep -v SUCCESS ./conversion_results.log

infile,outfile,format,conversion_status,return_code,execution_time
/storage/muzika/Lossless/test_flac/Earth Wind & Fire - Boogie Wonderland (12'' Version).flac,./fromFlac/vorbis/Earth Wind & Fire - Boogie Wonderland (12'' Version),vorbis,ERROR:oggenc ,-1,0.0104818344116
Earth Wind & Fire - Boogie Wonderland (12'' Version).flac,./fromFlac/opus/Earth Wind & Fire - Boogie Wonderland (12'' Version),opus,ERROR: opusenc error ''. Could not convert,1,0.00583696365356
/storage/muzika/Lossless/test_flac/08_-_Seal_-_Knock_On_Wood.flac,./fromFlac/vorbis/08_-_Seal_-_Knock_On_Wood,vorbis,ERROR:oggenc ,-1,0.0239849090576


 ```

The first line shows what each field refers to, and the other lines are a sample of failed FLAC files, with their full paths.


