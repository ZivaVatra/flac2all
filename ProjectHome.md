# News #

## Monday Feb 16, 2015 ##
  * New stable release! v3.71.  I've broken with tradition for this release, and have included some new features as well as bug fixes. These features have been requested multiple times, and v4 isn't ready for prime time yet.

  * New features:
    * **Opus support!** -- flac2all now has support for the opus codec. Additional dependencies:
      * opusenc -  versions < 0.1.7 doesn't have tag support. Newer versions have full tagging support. flac2all will detect which version you have and act accordingly
      * opus options are enabled by a new switch "-p OPUSENCOPTS" or "--opus-options=OPUSENCOPTS"
    * **Input filtering support!** -- Now you can exclude certain files/patterns from copying or conversion using the "-x" or "--exclude=$PATTERN" switches. Full regular expressions are supported, for example:
      * ` -x ".*.(cue|m3u|log).*" ` will convert/copy all files except .cue/m3u/log files to destination.
      * ` -x "\.sync" ` will exclude the .sync folder and its contents (as used by btsync) from being copied to destination
  * Bug fixes:
    * metaflac parsing bug in flac->flac conversion
    * bug in general flac->flac conversion
    * bug in generation of flat output ( i.e. no directory structure, as used with "-n" switch)
    * resolutions of [issue 14](https://code.google.com/p/flac2all/issues/detail?id=14), [issue 2](https://code.google.com/p/flac2all/issues/detail?id=2) and [issue 9](https://code.google.com/p/flac2all/issues/detail?id=9).

Right, new version is available in the download section. I've run extensive tests, but bugs may have slipped by, so raise a ticket if something goes wrong :-)

Thanks!


## Tue Jan 13, 2015 ##
  * Another update today. I've created two mailing lists on Google groups, in order to help keep track of everything.
    * flac2all-dev :  Dev discussion, issue/commit alerts. This should help me keep on track when somebody posts/updates an issue. Generally only for devs, or package maintainers.
    * flac2all-discussion :  General discussion, also support. Stable releases will be announced here too.
  * You can find links to the lists in "Groups" under "External links".

Additionally if you are allowed to post, you can email the groups directly by $groupname@googlegroups.com. Unfortunately in order to prevent abuse, public posting is not allowed on either group. You will have to join the group to post, but the General discussion group will allow public viewing.

## Tue Jan 13, 2015 ##
  * Happy new year everyone! Well, exactly a year after Google disabled the "Downloads" section of google code, I've gotten round to doing my own third-party hosted area. It isn't as pretty or functional as the google one, but it works. Sorry it took so long :) With time I hope to improve on the download page, but it will do for now.

  * All new releases will be <a href='http://flac2all.witheredfire.com/cgi-bin/download.cgi'>downloadable from here</a>

  * Additionally I've added the Download link under "External Link", at the bottom left of the site.

  * With the release of the new download page, I'm now able to issue an official stable release. Version 3.48!  This fixes the bug that affects [issue 10](https://code.google.com/p/flac2all/issues/detail?id=10), [issue 12](https://code.google.com/p/flac2all/issues/detail?id=12) and [issue 17](https://code.google.com/p/flac2all/issues/detail?id=17). As usual, please let me know if there are any problems.


## Sat Jun 21, 2014 ##
  * Well, I didn't realise this, but Google have disabled the ability to upload new packages to the "Download" section (see http://google-opensource.blogspot.co.uk/2013/05/a-change-to-google-code-download-service.html for more info). As such, from now on I have to have third party download hosting. Google offers Google Drive, but I will not be using that. At this point I'm not sure if I should just move the Downloads off Google, or the entire project (who knows what feature they will remove next).
  * Just to let you all know, v3.48 is ready for release. Until I find a spot to host it, please check out [revision 48](https://code.google.com/p/flac2all/source/detail?r=48) of the stable branch (it fixes [issue 10](https://code.google.com/p/flac2all/issues/detail?id=10) and [issue 12](https://code.google.com/p/flac2all/issues/detail?id=12)).
## Wed Jan 15, 2014 ##
  * New stable version is available. v3.38 encompasses all the known bugs that have been resolved since v3.28.
  * Apart from that, no new features. I tested it on my collection and it works, but please raise a ticket if you see any errors.

## Wed Oct 24 2012 ##
  * New stable version is out! After months of development I'm confident that the dev version is ready for publishing to stable. v3.28 is now on the Download page.
  * Please see the [Usage](Usage.md) page on info on how to use the new script.
    * New features:
      * New option system. No longer do you need to edit the script to set common variables. Now you can do it on the command line, like a real program! :P
      * Ability to set custom oggenc/lame parameters from command line.
      * CPU/Core detection, for automatic selection of # of threads.
      * Support for Nero's AAC+ Converter, for flac2aacplus conversion (No tagging support)
      * Allows copying of non-flac file across (album art, txt files, etc...)
      * Support for output directory redirection (before was only "./" )
      * Lots of little bugfixes/tweaks/performance improvements

  * **NOTE**: There has been a change in how I number releases. Before they would be v1.$x.$x, but I've realised I do not release often enough to warrant that. As so, I've gotten rid of the major release number. So now v1.2.19 is v2.19, v1.3 is v3, etc...
  * The new dev version will be v4, ideas for the next generation of flac2all will be posted on the [Development\_Status](Development_Status.md) page. Feel free to raise tickets if you have any ideas.

## Sat Mar 10 2012 ##
  * Archlinux package now available! (Many thanks to archlinux's graysky for the packages)
    * dev version: https://aur.archlinux.org/packages.php?ID=57418
    * stable version: https://aur.archlinux.org/packages.php?ID=57270
  * Some bug fixes, new features being added to the development version! Feel free to go test it out from the svn repo dev trunk.
  * Script tested and happily saturates a 16 core machine! Check out the video: <a href='http://www.youtube.com/watch?feature=player_embedded&v=pXSpPjWtSJc' target='_blank'><img src='http://img.youtube.com/vi/pXSpPjWtSJc/0.jpg' width='425' height=344 /></a>
# Background #

Flac2All is a multi-threaded script that will convert your collection of FLAC files into either Ogg Vorbis, MP3 (with the Lame encoder), or FLAC, complete with any tags that the source file had. This project was started back in 2004/5, and it has been constantly refined since then.

Known to saturate 8-core machines with parallel conversions, this program is useful for people with with large FLAC collections who also want a lossy version for portable media players. Especially as more and more machines nowadays come with 4/8 or more cores (and the trend is only up!).

If wanted, the script can perform updates by skipping already converted files, it can copy across non-flac files (like album art) and will keep the same directory structure as the source (unless you specify otherwise).

There are two branches, stable and dev. Stable is only for bugfixes, and if you want to contribute, work on the dev branch.

Any help with this project is much appreciated. Especially with regards to documentation. The program is pretty much self-documenting (run with "-h" for info) but some wiki pages would not go amiss.

Likewise, if you'd like to add a feature, fix a bug or generally help the project come along, feel free to drop me a line :)

Flac2all is hosted at googlecode now, and there is also a [freshmeat](http://freecode.com/projects/flac2all) page.

The [old](http://www.ziva-vatra.com/index.php?aid=23&id=U29mdHdhcmU=) site is no longer being updated, as I'm trying to cut down on having multiple places to post the same information to.
