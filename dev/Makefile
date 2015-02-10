.SHELL=/bin/bash
#.SHELL=/usr/bin/perl
#.SHELLFLAGS = -e
fulltest::
	@perl -e 'system("make clean") unless (0 != system("ls *.pyc 2>/dev/null"));'
	@echo "Commencing tests"
	python2 ./run_tests.py

mp3convert:
	python2 ./__main__.py mp3 --lame-options '-preset standard' -o /storage/flac2mp3 /mnt/muzika/Lossless/

debug:
	python2 -m pdb ./__main__.py mp3 --lame-options '-preset standard' -o /storage/flac2mp3 /mnt/muzika/Lossless/

clean:
	rm -v *.pyc
