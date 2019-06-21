## Usage - Clustered

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

The mounts are set up so that the paths are identical on both machines.

With the old flac2all, one of these machines would sit idle while the other would be churning away, however now both can be used simultaniously, like so:

First, I run the master node on Mnemosyne. This is the exact same syntax as flac2all is normally, except that the added option "-m" is specified:

```
mnemosyne:~$ flac2all vorbis,mp3,test -m --vorbis-options="quality=9"  -o /storage/muzika/Lossy/FromFlac/ /storage/muzika/Lossless/
Waiting for worker(s) to connect. We need at least one worker to continue
```

At this point, the master will sit and wait for at least one worker to join. As soon as a worker joins it will start issuing tasks. Any workers that join afterwards will automatically get tasks.

You launch the worker program on every node you want to use, with the syntax "flac2all_worker $master_hostname":
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
mnemosyne:~$ flac2all vorbis,mp3,test -m --vorbis-options="quality=9"  -o /storage/muzika/Lossy/FromFlac/ /storage/muzika/Lossless/
Waiting for worker(s) to connect. We need at least one worker to continue
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

As you can see, we effectively bind the two machines into an 18 core system. There is no upper bound to the number of worker threads you can attach to a master program, although if you use a central storage system (like I am doing), you will eventually hit IO limits of the storage (in my example, when I added more machines to make it a 26 thread system, the file server was unable to supply data fast enough to feed all the encoding threads).

As a rule, the number of workers printed by the master should match the total number spawned on the nodes. If it doesn't then something went wrong. This system needs a reliable network to function well.

At the end the master program will collate all the results, check that the number of conversion tasks issued matches the results, and report back to the end user.

The system is dynamic, you can add and remove worker during the process. Note that you must do a clean exit of the flac2all_worker, otherwise you may lose some tasks.


## Output ##

In the example above, we specified multiple codecs at once "vorbis,mp3,test", which means flac2all will convert to mp3 and vorbis at the same time, while also doing a test on each and every flac file (outputting ".ana" files). 

The output structure would create a subfolder for each codec. In the case of our example, it would look like this:
```
./fromFlac/vorbis
./fromFlac/mp3
./fromFlac/test
```
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
Earth Wind & Fire - Boogie Wonderland (12'' Version).flac,./fromFlac/opus/Earth Wind & Fire - Boogie Wonderland (12''Version),opus,ERROR: opusenc error ''. Could not convert,1,0.00583696365356
/storage/muzika/Lossless/test_flac/08_-_Seal_-_Knock_On_Wood.flac,./fromFlac/vorbis/08_-_Seal_-_Knock_On_Wood,vorbis,ERROR:oggenc ,-1,0.0239849090576
```

The first line shows what each field refers to, and the other lines are a sample of failed FLAC files, with their full paths.



