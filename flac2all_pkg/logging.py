# -*- coding: utf-8 -*-

import datetime
import sys
from ccons import cursecons

from termcolor import cprint


class cconsole(cursecons):
	def __init__(self):
		cursecons.__init__(self)
		self.messagelines = []
		self.workers = None
		self.complete = 0
		self.error = 0
		self.tasks = 0

	def _msg_display(self, status, msg):
		msg = msg.encode("utf-8", "replace").decode()
		msg = "%s: %s" % (
			datetime.datetime.utcnow().strftime("UTC~%H:%M:%S"),
			msg
		)
		self.messagelines.append([status, msg])
		self.message_box(self.messagelines)

	def status(self, msg):
		self._msg_display(["status", msg])

	def info(self, msg):
		self._msg_display(["info", msg])

	def ok(self, msg):
		self._msg_display(["ok", msg])

	def warn(self, msg):
		self._msg_display(["warn", msg])

	def crit(self, msg):
		self._msg_display(["crit", msg])


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
