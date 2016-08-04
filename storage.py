#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Storage handling component for LamiaDMBot

import os, sqlite3

class LamiaDB:
	"""Database handler for LamiaDMBot"""

	def __init__(self):
		#try:
			if not os.path.isfile('lamia.db'):
				#No previous database file
				self.conn = sqlite3.connect('lamia.db')
				cur = self.conn.cursor()
				cur.execute('CREATE TABLE rolls (id integer primary key autoincrement, name text not null, roll text not null)')
				self.conn.commit()
			else:
				self.conn = sqlite3.connect('lamia.db')
		#except:
		#	pass

if __name__ == '__main__':
    print "This is not meant to be used directly! Run 'main.py' instead."
