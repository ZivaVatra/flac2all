## Usage - Original (non clustered)

Full information, including options and all current available conversion modes, can be found by running "flac2all -h".

Attempts were made to keep this version backwards compatible with prior versions. You should be able to run the exact same commands and it should still work as expected.

You can specify multiple codecs to be specified on the command line, and in the target folder it will create a subfolder for each codec. So for example:

```
flac2all vorbis,mp3,test --vorbis-options='quality=2' -o ./fromFlac/ /path/to/flac/Lossless/ 
```

will create the following structure:
```
./fromFlac/vorbis/.../file.ogg
./fromFlac/mp3/.../file.mp3
./fromFlac/test/.../file.ana
```

If you specify "-n d", it will create the following output:
```
./fromFlac/file.ogg
./fromFlac/file.mp3
./fromFlac/file.ana

```

And if you specify "-n m", it will create the following output:
```
./fromFlac/.../file.ogg
./fromFlac/.../file.mp3
./fromFlac/.../file.ana
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

