#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4 ai
#
# File Created: Thu 21 Nov 15:05:49 GMT 2019
# Copyright 2019
#
# All rights reserved
#
# ============================================================|

import curses
import time


class cursecons:
	def __init__(self):
		self.screen = curses.initscr()
		curses.start_color()
		self._set_colours()
		curses.noecho()
		curses.cbreak()
		curses.curs_set(False)  # Disable cursor, we don't need it here
		self.screen.keypad(True)
		self.winheight = curses.LINES
		self.winwidth = curses.COLS

	def __enter__(self):
		pass

	def __exit__(self, etype, value, traceback):
		self.__del__()

	def __del__(self):
		curses.nocbreak()
		self.screen.keypad(False)
		curses.echo()
		curses.endwin()

	def _set_colours(self):
		curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

	def window(self, height, width, y, x, title=None, box=False, colour_pair=None):
		win = curses.newwin(height, width, y, x)
		attrs = curses.A_REVERSE
		if colour_pair is not None:
			attrs |= curses.color_pair(colour_pair)
		if box is True:
			win.box()
			if title:
				win.addstr(0, 2, " %s " % title.strip(), attrs)
		win.refresh()
		return win

	def percent_progress_bar(self, value):
		# Create the percentage window. Not generic
		assert value <= 100, "Percent value > 100"
		width = self.winwidth - 20
		offset = 6
		line = 4
		Pwin = self.window(8, width, 0, 0, "Progress", True)
		# So tricky here, we have to make the 100% value scale by number of columns.
		# the 6 is the extra right offset for the percentage value
		pcols = (width - (2 * offset) - 6) / 100
		Pwin.addstr(line, offset, "|" + '\u2588' * int(pcols * value), curses.color_pair(1))
		Pwin.addstr(line, int((pcols * 100) + offset + 1), "| %3d%%" % value, curses.color_pair(1))
		Pwin.refresh()
		return Pwin

	def stats_window(self, workers, tasks, completed, errors):
		Lwin = self.window(8, 20, 0, self.winwidth - 20, "Stats", True)
		if workers is None:
			Lwin.addstr(2, 2, "Workers: N/A")
		else:
			Lwin.addstr(2, 2, "Workers: %d" % workers)

		Lwin.addstr(3, 2, "Tasks: %d" % tasks)
		Lwin.addstr(4, 2, "Completed: %d" % completed)
		Lwin.addstr(5, 2, "Errors: %d" % errors)
		Lwin.refresh()
		return Lwin

	def message_box(self, messages):
		height = self.winheight - 8
		msg = messages[-(height - 2):]  # Show the last x messages we can fit
		win = self.window(height, self.winwidth, 8, 0, "Messages", True)
		y = 1
		for line in msg:
			win.addstr(y, 2, line[1][:(self.winwidth - 2)], curses.color_pair(int(line[0])))
			y += 1
		win.refresh()
		return win

	def main(self, *args):
		# Create the stats window
		self.stats_window(None, 0, 0, 0)

		# This is the message box
		self.message_box([[0, "Hello world"]])

		# This is the progress bar
		for x in range(0, 101):
			self.stats_window(None, x * 3000, x * (3000 / 10), x / 10)
			self.percent_progress_bar(x)
			time.sleep(0.05)


if __name__ == "__main__":
	c = cursecons()
	curses.wrapper(c.main)
	time.sleep(1)
