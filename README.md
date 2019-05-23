## News

### 22/05/2019

* Minor internal API changes
* Refinement of clustering mode
* Lots of small bugfixes (mostly to do with handling Unicode/byte type errors)
* Started removal of NeroAAC. We have aac-enc, and two ffmpeg provided aac encoders (f:aac and f:libfdk_aac), so we are well sorted for AAC options.

### 20/05/2019
* Code refactoring
* Added ffmpeg support. Now flac2all supports all the audio encoders ffmpeg does. These modes are prefixed with "f:" to indicate underlying library, and the --ffmpeg-options switch lets you set codec parameters.

### 13/05/2019
* Deprecation of NeroAAC codec, prior to removal. It is no longer maintained, and the binaries are 32-bit only
* Creation of a python3 master branch, to hold the future python3 stable release. At some point we will switch completely to python3

### 07/05/2019

* Flac Testing now refactored to generate analysis files in "test" output directory (with .ana suffix).
* Migration of code to python3
* Removal of old (pre 0.1.7) opus codec support. The logic is broken, and most people use newer codecs, so not worth converting the logic to python3


## What is it
Started in 2003 as a simple flac to ogg vorbis script, flac2all has grown into a clustered parallel processing program that will convert your collection of FLAC files into various other formats (see "Formats" section for list), complete with any tags that the source file had. Designed to be extended with new formats easily as time goes on, it is a utility for people with with large FLAC collections who also want a way to convert multiple files in parallel.

## Details

Version5 is the new release of flac2all. The decision to bump up a version number was primarily driven by the move to python3. Python2 is scheduled to be EOL after the 1st January 2020, and a lot of distros are already defaulting to python3 as the system Python interpreter. Rather than hold two versions of "version4", one for py2 and one for py3, it made more sense to bump the version number (thats what they are there for, after all).

Following on from my tradition of adding at least one major feature in major version upgrades. Version5 has the following new features:
* Support for ~72 new codecs via ffmpeg. Actual number of codecs subject to change based on what version of ffmpeg you have installed, and what options it is compiled with
* support for network distributed transcoding via ZeroMQ. This allows you to launch a single flac2all "master" on a machine, and then have flac2all "workers" running on other machines connect to it over a TCP connection. In other words, you can delegrate encoding tasks to multiple computers, each with multiple cores. For more details see the Usage->clustering section.

Note that the clustering function is optional, and flac2all will still work in the original way if ZeroMQ (and its python bindings) are not installed. As such we have not placed a hard dependency on ZeroMQ. This may change in future (e.g. if we decide to abandon the old logic and make everything ZeroMQ based internally).

## Dependencies
* Python >= 3.6
* Flac

## Optional dependencies
* ZeroMQ (for clustering)
* Lame: for mp3 support
* Opus-tools: for opus support
* Vorbis-tools: for ogg support
* aac-enc for AAC support
* ffmpeg for supporting all the audio encoders it supports

## Packages for Distros

### Stable:
There is a pip package available. You can install flac2all by running  "pip install flac2all" as root, or "pip install flac2all --user" for a non root local install.

To upgrade to a new release you run the same commands as installation, but with "--upgrade" option set.

## Development:
If you want the bleeding edge version, best to check out the latest "version5" branch from git.
Generally development work will be done in branches then merged, so master should be functional.

Tu run the version straight from the git repo, cd to "flac2all_pkg", and then run "python ./\_\_init\_\_.py -h". The rest should work as normal.

Since version 4, all codecs are split into their own modules, which allows developers to easily add new codecs. The internal function tables stay the same, meaning that as long as you follow the structure of the main functions, you can add any codec you want.

The easiest way to get started writing a codec module is to look at an existing one. I would recommend "flac.py", as it shows both encoding and decoding, and flac to flac conversion was very simple to implement. A more complex example is the mp3 module, which shows how complex things can get.

### Fixed branches
There are some branches that are considered "fixed". This means that they tend to be self contained, and they need not track any other branch. A list of these branches as as follows:

* master: Main branch, where final merges and tests are done prior to tagging and deployment. From here we generate the releases.
* version5: The current development branch, where changes are made, pulls merged and tested, prior to merge with master for release.
* version4: The current stable branch. No active development, but general maintenance and bugfixes are being handled.
* version3: The old stable branch. No active development, but kept in case someone needs/wants access to the old version3


### Dev etiquette
If you wish to contribute to flac2all, I ask that you keep to the following guidelines:

* If you want to extend/modify flac2all, checkout the latest copy of the repo, switch to the development branch, and then make your own branch, develop/test/debug until ready, then issue a pull request. Do not start hacking away on the master branch directly.

* The goal of the master branch is to be the final stage before a tagged release. As such, any code merged into master should not break things badly. All testing and debugging should be done on your branch prior to merge.

* If you want to add a new codec to flac2all, please keep it all in one single file. This is how the rest of flac2all is written. Some codecs (like AAC) actually have two implementations in one module (Both NeroAAC and fdk-aac). It keeps things easier to manage if each conversion codec is its own module.

* Keep to the same internal API as the other modules. If you strongly feel that the API is missing some functionality critical to making your module work, raise an issue on this project page and we can discuss the situation.

* Please raise an issue if you intend to place a hard dependency on a third party package (that isn't a codec). If you want to make use of a third party library it would be best to discuss before time is put into development.

## Known bugs/issues and TODOs

* using "ctrl-c" to terminate does not exit cleanly. Plus you have to hit ctrl-c multiple times to terminate flac2all.

* following on from above, when terminated the script leaves a bunch of tmpfiles. We need to clean up properly.

## Raising a bug report

Before you raise a bug report, please test with the latest version from git. Sometimes distro packages lag the latest stable by a couple of versions, so you may hit bugs that have already been fixed.

## Examples in use

* Here is a video of flac2all (v3) saturating a 16 core machine with conversions: [[synapse-16_threads](https://www.youtube.com/watch?v=pXSpPjWtSJc)]

## Usage

Full information, including options and all current available conversion modes, can be found by running "flac2all -h".

### Non clustered (original) ###

Attempts were made to keep this version backwards compatible with prior versions. In theory you should be able to run the exact same commands and it should still work as expected.

You can specify multiple codecs to be specified on the command line, and in the target folder it will create a subfolder for each codec. So for example:

```
flac2all vorbis,mp3,test --vorbis-options='quality=2' -o ./fromFlac/ /path/to/flac/Lossless/ 
```

will create the following structure:

```
./fromFlac/vorbis
./fromFlac/mp3
./fromFlac/test
```
This example will encode both to ogg vorbis and mp3 formats, while generating per file test logs, simultaniously.

In addition, a summary conversion log is created. This is printed to stdout after a run. An example (with partial failures) looks like this:

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

### Clustered ###

In clustered mode flac2all works a bit differently. There is a "master" program, which generates the conversion list, delegates tasks to workers and collates the results into one place. It does no encoding of its own.

Then there are the "worker" programs. They launch one worker per CPU, and all connect to the master via ZeroMQ sockets. These workers can be on the same computer as the master progam, or they can be on another computer. Using an IP network the workers are agnostic to the physical machine the master is on.

This means you can attach multiple multi-core computers to a single master program, and they will all work together as a cluster to convert your files.

N.B: flac2all does not transfer raw audio data. It just instructs the workers what files to process. This means that all your worker nodes must have the same paths with the same flac files in them in order to work. This was done deliberately. It gives the end user more flexibility in choice of what underlying data transfer technology they want to use. From NFS mounts to a central server, to shared ISCSI nodes, to batch runs on local disks then rsync together, the choice is yours.

Fundementally, there is a large body of storage and remote data access technology out there, with many man-years invested in their development by specialists in the field, and of varying types, features and maturity. and it seems unwise for me to ignore all that and reinvent yet another one (poorly).

#### An example setup ####

This is the setup I am using:
```
 ---------------------                                         -------------------------
| Athena (Node 1)     |                                       | Mnemosyne (Node 2)      |
|                     | ----------- 1Gb/s Ethernet ---------- |                         |
| Linux               |                                       | FreeBSD                 |
| 12 core, 32GB RAM   |                                       | 6 core, 32GB RAM        |
| Runs:               |                                       | Runs:                   |
|    - 12 workers     |                                       |   - 6 workers           |
| Path: NFS_mounted   |                                       |   - master program      |
 ---------------------                                        | Path: Local ZFS         |
                                                               -------------------------
```

Athena is just a processing machine. It has no local storage (apart from the OS). The path to both the flac source and converted destination (/storage/muzika) is a NFS mount, which resides on Mnemosyne (which is my file server). As the file server, Mnemosyne has the local path access, and needs not to go through NFS.

The mounts are set up so that the paths are indential on both machines.

With the old flac2all, one of these machines would sit idle while the other would be churning away, however now both can be used simultaniously, like so:

First, I run the master node on Mnemosyne. This is the exact same syntax as flac2all is normally, except that the added option "-m" is specified:

```
mnemosyne:~$ flac2all vorbis -m --vorbis-options="quality=9"  -o /storage/muzika/Lossy/FromFlac/ /storage/muzika/Lossless/
Waiting 15 seconds for worker(s) to connect. We need at least one worker to continue
```

At this point, you launch the worker program on every node you want to use, with the syntax "flac2all_worker $master_hostname":
```
mnemosyne:~$ flac2all_worker mnemosyne
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
```

```
athena:~$ flac2all_worker mnemosyne
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
Spawned worker process
```
If all goes as planned, you should see the following printed on the master programs stdout:
```
mnemosyne:~$ flac2all vorbis -m --vorbis-options="quality=9"  -o /storage/muzika/Lossy/FromFlac/ /storage/muzika/Lossless/
Waiting 15 seconds for worker(s) to connect. We need at least one worker to continue
Got 1 worker(s)
Got 2 worker(s)
Got 3 worker(s)
Got 4 worker(s)
Got 5 worker(s)
Got 6 worker(s)
Got 7 worker(s)
Got 8 worker(s)
Got 9 worker(s)
Got 10 worker(s)
Got 11 worker(s)
Got 12 worker(s)
Got 13 worker(s)
Got 14 worker(s)
Got 15 worker(s)
Got 15 worker(s)
Got 16 worker(s)
Got 17 worker(s)
Got 18 worker(s)
Commencing run...
```
At this point encoding will start, and both the worker and master program will output data indicating the current progress. The worker programs will output only what they have processed, and the master will output an aggregate of the nodes.

As you can see, we effectively bound the two machines into an 18 core system. There is no upper bound to the number of worker threads you can attach to a master program, although if you use a central storage system (like I am doing), you will eventuall hit IO limits of the storage (in my example, when I added more machines to make it a 26 thread system, the file server was unable to supply data fast enough to feed all the encoding threads).

As a rule, the number of workers printed by the master should match the total number spawned on the nodes. If it doesn't then something went wrong. This system needs a reliable network to function well.

At the end the master program will collate all the results, check that the number of conversion tasks issued matches the results, and report back to the end user.

At the moment there is no way to dynamically add/remove workers from the cluster during a conversion. Once the workers are registered at the start, the configuration cannot be changed. Any nodes that go down will lose the tasks that were assigned to that worker by the master, and any nodes added after will not get any tasks assigned to them.
