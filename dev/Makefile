.SHELL=/bin/bash
#.SHELL=/usr/bin/perl
#.SHELLFLAGS = -e
fulltest::
	@perl -e 'system("make clean") unless (0 != system("ls *.pyc 2>/dev/null"));'
	@echo "Commencing tests"
	python2 ./run_tests.py
opustest:
	python2 -m pdb  ./__main__.py opus -o ./testoutput/ ./testinput/

mp3test:
	python2 -m pdb  ./__main__.py mp3 -o ./testoutput/ ./testinput/


convert:
	python2 ./__main__.py mp3 -t 8 --vorbis-options 'quality=3'  --lame-options '-preset standard' -o /storage/muzika/Lossy/fromFlac/ /storage/muzika/Lossless/

debug:
	python2 -m pdb ./__main__.py mp3 --lame-options '-preset standard' -o /storage/flac2mp3 /mnt/muzika/Lossless/

kill:
	if [ `uname` == Linux ]; then ps -ef | grep __main__ | awk '{ print $$2 }' | xargs kill; else 		ps -aux | grep __main__ | awk '{ print $$2 }' | xargs kill; fi
	killall lame
	killall lame
	killall oggenc
	killall oggenc

clean:
	rm -v *.pyc
