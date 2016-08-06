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
				#No previous database file, we'll create one
				self.conn = sqlite3.connect('lamia.db')
				cur = self.conn.cursor()
				cur.execute('CREATE TABLE rolls (id integer primary key autoincrement, name text not null, roll text not null)')
				cur.execute('CREATE TABLE users (id integer primary key autoincrement, userid text not null)')
				self.conn.commit()
			else:
				self.conn = sqlite3.connect('lamia.db')
		#except:
		#	pass

	def is_user_registered(self, userid):
		"""Returns True if the user with specified userid is already registered, otherwise it returns False"""
		#try:
		cur = self.conn.cursor()
		t = (userid, )
		cur.execute('SELECT * FROM users WHERE userid=?', t)
		retrieved_user = cur.fetchone()
		if (retrieved_user == None): #No such user
			return False
		else:
			return True
		#except:
		#	pass

	def register_user(self, userid):
		"""Registers a new user in the database, returning True if it was successful or False if the user already exists."""
		#try:
		#First, we'll test if an user already exists
		cur = self.conn.cursor()
		t = (userid, )
		cur.execute('SELECT * FROM users WHERE userid=?', t)
		retrieved_user = cur.fetchone()
		if (retrieved_user == None): #No such user, we'll register it
			cur.execute('INSERT INTO users (userid) VALUES (?)', t)
			self.conn.commit()
			return True
		else:
			return False
		#except:
		#	pass

if __name__ == '__main__':
    print "This is not meant to be used directly! Run 'main.py' instead."
