# -*- coding: utf-8 -*-
# vim: ts=4 noexpandtab si

import os
from config import ipath, opts
from shell import shell
from time import time
import subprocess as sp


# This class is called by every other conversion function, to return a "decode"
# object
class flacdecode(object):
	def __init__(self, infile, pipefile):
		self.infile = infile
		self.pipe = pipefile

	def __call__(self):
		fd = sp.Popen([
			ipath.flacpath + "flac", '-d', '-s', '-f', '-o', self.pipe, "%s" % self.infile
		], stderr=sp.PIPE
		)
		return (None, fd.stderr)  # None because we have moved to using named pipes


class flac(object):
	def __init__(self, flacopts=""):
		self.opts = flacopts
		self.shell = shell()
		self.qEscape = \
			lambda x: self.shell.parse_escape_chars(x, True)

	def flacConvert(self, infile, outfile, logq):
		# Seems newer versions of flac actually support flac -> flac
		# recompression natively. Which is nice. This is now very
		# simple to implement, hence removed the old code
		startTime = time()
		if opts['overwrite']:
			self.opts += " -f "
		else:
			if os.path.exists(outfile):
				logq.put([
					infile,
					outfile,
					"flac",
					"SUCCESS:skipped due to existing file",
					0,
					time() - startTime
				])
				return 0
		cmd = [
			"%sflac" % ipath.flacpath,
			"-s",
			"-o",
			'%s.flac' % self.shell.parse_escape_chars(outfile),
			self.shell.parse_escape_chars(infile)
		]
		if len(self.opts) > 0:
			cmd.extend(self.opts)

		rc = sp.check_call(cmd)

		if (rc == 0):
			logq.put([
				infile,
				outfile,
				"flac",
				"SUCCESS",
				rc,
				time() - startTime
			])
		else:
			logq.put([
				infile,
				outfile,
				"flac",
				"ERROR:flac ",
				rc,
				time() - startTime
			])

	def getflacmeta(self, flacfile):
		flacdata = sp.check_output([
			"%smetaflac" % ipath.metaflacpath,
			"--list",
			"--block-type", "VORBIS_COMMENT",
			flacfile
		]).decode('utf-8')

		datalist = []  # init a list for storing all the data in this block

		# this dictionary will store only the comments
		# for the music file
		commentlist = {}

		for data in flacdata.split('\n'):
			# get rid of any whitespace from the left to the right
			data = data.strip()

			# check if the tag is a comment field (shown by the first 7 chars
			# spelling out "comment")
			if(data[:8] == "comment["):
				datalist.append(data.split(':'))

		for data in datalist:
			# split according to [NAME]=[VALUE] structure
			comment = data[1].split('=')
			comment[0] = comment[0].strip()
			comment[1] = comment[1].strip()

			# convert to upper case
			# we want the key values to always be the same case, we decided on
			# uppercase (whether the string is upper or lowercase, is dependent
			# on the tagger used)
			comment[0] = comment[0].upper()

			# assign key:value pair, comment[0] will be the key, and comment[1]
			# the value
			commentlist[comment[0]] = comment[1]
		return commentlist

	def flactest(self, infile, outfile, logq):
		startTime = time()
		try:
			sp.check_call([
				"%sflac" % ipath.flacpath,
				"-s",
				"-a",
				"-o",
				"%s.ana" % outfile,
				infile
			], stderr=sp.STDOUT)
		except sp.CalledProcessError as e:
			results = str(e.output)
			rc = str(e.returncode)
		else:
			results = "SUCCESS"
			rc = 0

		logq.put([
			infile,
			outfile,
			"flactest",
			results,
			rc,
			time() - startTime
		])
