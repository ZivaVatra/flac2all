# -*- coding: utf-8 -*-

import datetime
import sys

from termcolor import cprint


class console():
	def __init__(self, stderr=True):
		if stderr:
			self.foutput = sys.stderr
		else:
			self.foutput = sys.stdout

	def _genmsg(self, msg):
		msg = msg.encode("utf-8", "replace").decode()
		return "%s: %s" % (
			datetime.datetime.utcnow().strftime("UTC~%H:%M:%S"),
			msg
		)

	def print(self, msg):
		print(msg, file=self.foutput)

	def status(self, msg):
		cprint(self._genmsg(msg), "cyan", file=self.foutput)

	def info(self, msg):
		cprint(self._genmsg(msg))

	def ok(self, msg):
		cprint(self._genmsg(msg), "green", file=self.foutput)

	def warn(self, msg):
		cprint(self._genmsg(msg), "yellow", file=self.foutput)

	def crit(self, msg):
		cprint(self._genmsg(msg), "red", file=self.foutput)
