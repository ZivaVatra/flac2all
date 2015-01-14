fulltest::
	make clean
	python ./run_tests.py

mp3convert:
	python ./__main__.py mp3 --lame-options '-preset standard' -o /storage/flac2mp3 /mnt/muzika/Lossless/

debug:
	python -m pdb ./__main__.py mp3 --lame-options '-preset standard' -o /storage/flac2mp3 /mnt/muzika/Lossless/

clean:
	rm -v *.pyc
