# -*- coding: utf-8 -*-

import datetime

from termcolor import cprint


class console():
	def __init__(self, stderr=True):
		self.stderr = stderr

	def _genmsg(self, msg):
		msg = msg.encode("utf-8", "replace")
		return "%s: %s" % (
			datetime.datetime.utcnow().strftime("UTC~%H:%M:%S"),
			msg
		)

	def status(self, msg):
		if self.stderr:
			cprint(self._genmsg(msg), "cyan")

	def info(self, msg):
		if self.stderr:
			cprint(self._genmsg(msg))

	def ok(self, msg):
		if self.stderr:
			cprint(self._genmsg(msg), "green")

	def warn(self, msg):
		if self.stderr:
			cprint(self._genmsg(msg), "yellow")

	def crit(self, msg):
		if self.stderr:
			cprint(self._genmsg(msg), "red")
