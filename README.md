## What is it
Started in 2003 as a flac to vorbis script, flac2All has grown into a parallel processing script that will convert your collection of FLAC files into various other formats (currently mp3,ogg vorbis,opus,flac and acc), complete with any tags that the source file had. Designed to be extended with new formats easily as time goes on, it is a utility for people with with large FLAC collections who also want a way to convert multiple files in parallel."
## Details

This is the new version, replacing V3. Its been in "Beta" for a few years now, and now I feel ready to release it to the public. Please test and raise any issues you find. 

version3 is still available, in the "version3" branch of this git repo. The older v3 releases are also still available in the downloads repo if v4 isn't working for you. 

## Dependencies
* Python >2.7
* Flac

## Optional dependencies
* Lame: for mp3 support
* Opus-tools: for opus support
* Vorbis-tools: for ogg support
* neroAAC and/or fdk-aac  for AAC support


## Packages for Distros
There is a pip package available. You can install flac2all by running  "pip install flac2all".


## Usage
Unlike the 3.x version, this one allows multiple codecs to be specified on the command line, and in the target folder it will create a subfolder for each codec. So for example:

python ./\_\_main\_\_.py vorbis,mp3 --vorbis-options='quality=2' -o ./fromFlac/ /path/to/flac/Lossless/

will create the following structure:

./fromFlac/vorbis
./fromFlac/mp3

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
/storage/muzika/Lossless/random_flac/Earth Wind & Fire - Boogie Wonderland (12'' Version).flac,/fromFlac/vorbis/Earth Wind & Fire - Boogie Wonderland (12'' Version),vorbis,ERROR:oggenc ,-1,0.0104818344116
Earth Wind & Fire - Boogie Wonderland (12'' Version).flac,./fromFlac/opus/Earth Wind & Fire - Boogie Wonderland (12'' Version),opus,ERROR: opusenc error ''. Could not convert,1,0.00583696365356
/storage/muzika/Lossless/random_flac/08_-_Seal_-_Knock_On_Wood.flac,./fromFlac/vorbis/08_-_Seal_-_Knock_On_Wood,vorbis,ERROR:oggenc ,-1,0.0239849090576


 ```

The first line shows what each field refers to, and the other lines are a sample of failed FLAC files, with their full paths.

## Developing

Main goal of version 4 was to split the codecs into their own modules, which should allow developers to easily add new codecs. The internal function tables stay the same, meaning that as long as you follow the structure of the main functions, you can add any codec you want.

The structure is not formalised yet, so may change, but I think there will be no radical changes, more incremental improvements as time goes on.

The easiest way to get started writing a codec module is to look at an existing one. I would recommend "flac.py", as it shows both encoding and decoding, and flac is very simple to implement.

## Known bugs/issues

* using "ctrl-c" to terminate does not exit cleanly. Plus you have to hit ctrl-c multiple times to terminate flac2all.
