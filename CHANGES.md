## News / Changes

### 12/08/2019
* Lame mp3: Removed logic that sets genre automatically to "other", as lame now does the right thing with id3v(1|2) tags. With this change, the last of the original flac2all code is now gone.

### 19/06/2019
* README was getting too unwieldly, so split into multiple files: README.md, CHANGES.md, etc....

### 23/05/2019
* Changed clustering process. System is now dynamic
* Changed summary generation so that it is independent of process method
* More Unicode (En|De)coding py3 issues fixed
* Added ability for workers to refuse tasks

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



