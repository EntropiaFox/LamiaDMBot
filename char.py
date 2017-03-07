#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Character handler component for LamiaDMBot

class Character:
	"""Basic character definition class"""


	def __init__(self, attlist={}):
		self.attlist = {}
		try:
			self.attlist = attlist
		except:
			pass


	def getAttribute(self, attname): #Gets a specific attribute by name. Returns False if such attribute does not exist
		if attname in self.attlist:
			return self.attlist[attname]
		else:
			return False


	def setAttribute(self, attname, attval): #Sets a specific attribute by name. Returns True if said attribute exists, and False if it doesn't
		if attname in self.attlist:
			self.attlist[attname] = attval
			return True
		else:
			return False


if __name__ == '__main__':
	print "This is not meant to be used directly! Run 'main.py' instead."