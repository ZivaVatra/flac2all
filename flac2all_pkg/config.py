# vim: ts=4 ai
# This file holds all the config details
# ***NOTE***
# if the *path variables below are left blank, then the script will try to find
# the programs automatically. only change these if the script does not work
# (or add the programs to your system $PATH variable)


class paths(object):
	def __init__(self):
		self.flacpath = ""  # path to flac binary, blank by default
		self.metaflacpath = ""  # path to metaflac, blank be default
		self.oggencpath = ""  # path to oggenc binary, blank by default
		self.lamepath = ""  # path to lame binary, blank by default
		self.aacpath = "/usr/bin/"  # path to aacplus binary, blank by default
		self.neropath = ""  # path to the Nero aacplus binary, blank by default
		self.opusencpath = ""
		self.ffmpegpath = ""
		self.path = ""


ipath = paths()

# These are global defaults, if you don't define a shell
# argument, the below will be used instead.
opts = {
	"outdir": "./",  # the directory we output to, defaults to current directory
	"overwrite": False,  # do we overwrite existing files
	"nodirs": False,  # do not create directories (dump all files into single dir)
	"copy": False,  # Copy non flac files (default is to ignore)
	"lameopts": "--preset standard -q 0",  # your mp3 encoding settings
	"oggencopts": "quality=2",  # your vorbis encoder settings
	"flacopts": "",  # your flac encoder settings
	"aacplusopts": "-a 1 -t 29",
	"opusencopts": "vbr",
}
