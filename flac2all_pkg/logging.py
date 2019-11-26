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
		self.errors = 0
		self.tasks = 0

	def _msg_display(self, status, msg):
		msg = msg.encode("utf-8", "replace").decode()
		msg = "%s: %s" % (
			datetime.datetime.utcnow().strftime("UTC~%H:%M:%S"),
			msg
		)
		self.messagelines.append([status, msg])
		self.message_box(self.messagelines)

	def update(self):
		self.stats_window(self.workers, self.tasks, self.complete, self.errors)
		# Get percentage done from complete and total
		self.percent_progress_bar((self.complete / self.tasks) * 100)

	def status(self, msg):
		self._msg_display(0, msg)

	def info(self, msg):
		self._msg_display(1, msg)

	def ok(self, msg):
		self._msg_display(2, msg)

	def warn(self, msg):
		self._msg_display(3, msg)

	def crit(self, msg):
		self._msg_display(4, msg)

	def active_workers(self, workers):
		self.workers = workers
		self.update()

	def tasks(self, total, success, failures):
		self.complete = success
		self.errors = failures
		self.tasks = total
		self.update()


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

	def tasks(self, incount, success, failures):
		pass  # We do not implement this in console, too noisy

	def active_workers(self, workers):
		pass  # We do not implement this in console, too noisy
