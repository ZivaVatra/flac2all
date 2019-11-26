# -*- coding: utf-8 -*-
# vim ts=4 expandtab si
import os
import string

from shutil import copyfile


class filecopy:
	def __init__(self, opts):
		self.opts = opts

	def convert(self, infile, outfile):
		# The outfile will contain "_copy" as a folder, we
		# use that as a placeholder which we replace with the
		# current given mode here
		outfile = outfile.replace("_copy", self.opts['copymode'])
		try:
			copyfile(infile, outfile)
		except Exception as e:
			return [
				infile,
				outfile,
				"_copy",
				"Error: %s" % str(e),
				-1,
				-1
			]
		return [
			infile,
			outfile,
			"_copy",
			"SUCCESS",
			0,
			-1
		]


class shell:
	def generateoutdir(self, indir, outdir, dirpath):
		# if we find the dirpath in the current output path, we replace
		# it with the new output path. (so that we don't get
		# /mnt/convertedfromflac/mnt/flac/[file].mp3, in this case
		# "/mnt/" exist in both)
		if (string.find(os.path.split(indir)[0], dirpath) != -1):
			return os.path.split(indir)[0].replace(dirpath, outdir)
		else:
			# if we do not find an instance of dir path in output
			# path (this shows that they are the same), just
			# return the output
			return outdir

	def parse_escape_chars(self, input_file, quoteonly=False):
		if quoteonly:
			# characters which must be escaped in the shell, note
			# "[" and "]" seems to be automatically escaped
			# (strange, look into this)
			escChars = ["\"", "*", ";", " ", "'", "(", ")", "&", "`"]

			for char in escChars:
				# add an escape character to the character
				input_file = input_file.replace(char, '\\' + char)
		else:
			input_file = input_file.replace("\"", "\\\"")

		return input_file

	def getfiles(self, path):
		outfiles = []
		for root, dirs, files in os.walk(path):
			for infile in files:
				outfiles.append(
					os.path.abspath(
						os.path.join(root, infile)
					)
				)
		return outfiles
