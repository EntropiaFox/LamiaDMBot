#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Storage handling component for LamiaDMBot

import os, sqlite3, logging

class LamiaDB():
	"""Database handler for LamiaDMBot"""

	def __init__(self, dbname='lamia.db'):
		"""Constructor for the LamiaDB database handler"""
		# Enable logging
		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

		self.logger = logging.getLogger(__name__)

		if not os.path.isfile(dbname):
			#No previous database file, we'll create one
			print "Initializing database..."
			self.conn = sqlite3.connect(dbname)
			self.conn.isolation_level = None #Hahahaha REAL FUCKING FUNNY PYTHON
			cur = self.conn.cursor()
			cur.execute('PRAGMA foreign_keys = ON')
			cur.execute('CREATE TABLE users (userid integer primary key)')
			cur.execute('CREATE TABLE rolls (id integer primary key autoincrement, name text not null, roll text not null, users_id integer, foreign key(users_id) references users(userid))')
			cur.execute('CREATE TABLE characters (id integer primary key autoincrement, name text not null, users_id integer, foreign key(users_id) references users(userid))')
			cur.execute('CREATE TABLE attributes (id integer primary key autoincrement, attributename text not null, attributevalue text, characters_id integer, foreign key(characters_id) references characters(id))')
			self.conn.commit()
			print "Done."
		else:
			self.conn = sqlite3.connect(dbname)
			self.conn.execute('PRAGMA foreign_keys = ON')
			self.conn.isolation_level = None #Hahahaha REAL, REAL FUCKING FUNNY PYTHON

	def is_user_registered(self, userid):
		"""Returns True if the user with specified userid is already registered, otherwise it returns False"""
		cur = self.conn.cursor()
		t = (userid, )
		cur.execute('SELECT * FROM users WHERE userid=?', t)
		retrieved_user = cur.fetchone()
		if not (retrieved_user == None): #No such user
			return True
		else:
			return False

	def register_user(self, userid):
		"""Registers a new user in the database, returning True if it was successful or False if the user already exists or the register failed."""
		try:
		#First, we'll test if an user already exists
			cur = self.conn.cursor()
			t = (userid, )
			if not (self.is_user_registered(userid)): #No such user, we'll register it
				cur.execute('begin')
				cur.execute('INSERT INTO users (userid) VALUES (?)', t)
				self.conn.commit()
				return True
			else:
				return False
		except Exception as e:
			self.logger.exception("Exception in call to 'register_user'")
			self.conn.rollback()
			return False

	def is_roll_registered(self, userid, rollname):
		"""Returns True if a given roll has already been registered in the database, otherwise it returns False"""
		cur = self.conn.cursor()
		t = (userid, rollname, )
		cur.execute('SELECT * FROM rolls WHERE users_id=? AND name=?', t)
		retrieved_roll = cur.fetchone()
		if not (retrieved_roll == None):
			return True
		else:
			return False

	def register_roll(self, userid, rollname, rollparam):
		"""Registers a new roll in the database, returning True if it was successful and False if it wasn't"""
		try:
			cur = self.conn.cursor()
			t = (rollname, rollparam, userid, )
			if not (self.is_roll_registered(userid, rollname)):
				cur.execute('begin')
				cur.execute('INSERT INTO rolls (name, roll, users_id) VALUES (?, ?, ?)', t)
				self.conn.commit()
				return True
			else:
				return False
		except Exception as e:
			self.logger.exception("Exception in call to 'register_roll'")
			self.conn.rollback()
			return False

	def fetch_roll(self, userid, rollname):
		"""Recalls a single roll stored in the database, returning the roll's parameters (value) if found and None if it wasn't"""
		cur = self.conn.cursor()
		t = (rollname, userid, )
		cur.execute('SELECT roll FROM rolls where name=? AND users_id=?', t)
		retrieved_roll = cur.fetchone()
		return retrieved_roll

	def fetch_all_rolls(self, userid):
		"""Recalls all rolls of a given user stored in the database, returning a dictionary in the format {rollname=rollparam}"""
		retrieved_rolls = {}

		cur = self.conn.cursor()
		t = (userid, )
		for row in cur.execute('SELECT name, roll FROM rolls WHERE users_id=?', t):
			retrieved_rolls[row[0]] = row[1]
		return retrieved_rolls

	def delete_roll(self, userid, rollname):
		"""Deletes a roll parametrized by userid and name. Returns True if the delete was successful and False if it wasn't."""
		try:
			cur = self.conn.cursor()
			t = (userid, rollname, )
			if self.is_roll_registered(userid, rollname):
				cur.execute('begin')
				cur.execute('DELETE FROM rolls WHERE users_id=? AND name=?', t)
				self.conn.commit()
				return True
			else:
				return False
		except Exception as e:
			self.logger.exception("Exception in call to 'delete_roll'")
			self.conn.rollback()
			return False

	def is_character_registered(self, userid, charactername):
		"""Returns True if the character with specified associated userid is already registered, otherwise it returns False"""
		cur = self.conn.cursor()
		t = (charactername, userid, )
		cur.execute('SELECT * FROM characters WHERE name=? AND users_id=?', t)
		retrieved_character = cur.fetchone()
		if not (retrieved_character == None): #No such character
			return True
		else:
			return False


	def register_character(self, userid, charactername):
		"""Registers a new character in the database, returning True if it was successful and False if it wasn't"""
		try:
			cur = self.conn.cursor()
			t = (charactername, userid, )
			if not (self.is_character_registered(userid, charactername)):
				cur.execute('begin')
				cur.execute('INSERT INTO characters (name, users_id) VALUES (?, ?)', t)
				self.conn.commit()
				return True
			else:
				return False
		except Exception as e:
			self.logger.exception("Exception in call to 'register_character'")
			self.conn.rollback()
			return False

	def fetch_character(self, userid, charactername):
		"""Returns a dictionary with all of a given character's attributes in the format {attribute=value} with the first attribute being its name.
		If such character does not exist, return an empty dictionary."""
		character_attributes = {}
		cur = self.conn.cursor()
		if(self.is_character_registered(userid, charactername)): #Character registered exists
			t = (userid, charactername, )
			character_attributes['name'] = charactername
			current_character = self.character_id_from_name(userid, charactername)
			t = (current_character, )
			for row in cur.execute('SELECT attributename, attributevalue FROM attributes WHERE characters_id=?', t):
				character_attributes[row[0]] = row[1]
		return character_attributes

	def fetch_all_characters(self, userid):
		"""Returns a list with all characters registered under the same users. If a given user does not exist or has no characters registered, return
		an empty list."""
		character_list = []
		cur = self.conn.cursor()
		t = (userid, )
		if(self.is_user_registered(userid)):
			for row in cur.execute('SELECT name FROM characters WHERE users_id=?', t):
				character_list.append(row[0])
		return character_list

	def character_id_from_name(self, userid, charactername):
		"""Returns a given character's id if it can be found"""
		cur = self.conn.cursor()
		t = (userid, charactername, )
		cur.execute('SELECT id FROM characters WHERE users_id=? AND name=?', t) #First, we'll get the character's id
		current_character = cur.fetchone()
		return current_character[0]


	def delete_character(self, userid, charactername):
		"""Removes a character belonging to a given user, returning True if it was a success or False if it wasn't."""
		try:
			cur = self.conn.cursor()
			current_character = self.character_id_from_name(userid, charactername)
			t = (current_character, )
			cur.execute('begin')
			cur.execute('DELETE FROM attributes WHERE characters_id=?', t) #With this, we'll delete all the attributes first
			cur.execute('DELETE FROM characters WHERE id=?', t) #And then the character itself
			self.conn.commit()
			return True #Looking good? Commit and return True
		except Exception as e: #No? We'll undo the mess we made and return False
			self.logger.exception("Exception in call to 'delete_character'")
			self.conn.rollback()
			return False

	def add_attribute(self, userid, charactername, attributename, attributevalue):
		"""Adds an attribute to a character, returning True if it was a success and False if it wasn't."""
		try:
			cur = self.conn.cursor()
			current_character = self.character_id_from_name(userid, charactername)
			t = (attributename, current_character, )
			cur.execute('SELECT * FROM attributes WHERE attributename=? AND characters_id=?', t)
			current_attribute = cur.fetchone()
			if(current_attribute == None):
				t = (attributename, attributevalue, current_character, )
				cur.execute('begin')
				cur.execute('INSERT INTO attributes (attributename, attributevalue, characters_id) values (?, ?, ?)', t)
				self.conn.commit()
				return True
			else:
				self.conn.rollback()
				return False
		except Exception as e:
			self.logger.exception("Exception in call to 'add_attribute'")
			self.conn.rollback()
			return False

	def change_attribute(self, userid, charactername, attributename, attributevalue):
		"""Changes the current value of a given attribute, returning True if it was a success and False if it wasn't."""
		try:
			cur = self.conn.cursor()
			current_character = self.character_id_from_name(userid, charactername)
			t = (attributevalue, current_character, attributename, )
			cur.execute('begin')
			cur.execute('UPDATE attributes SET attributevalue=? WHERE characters_id=? AND attributename=?', t)
			self.conn.commit()
			return True
		except Exception as e:
			self.logger.exception("Exception in call to 'change_attribute'")
			self.conn.rollback()
			return False

	def remove_attribute(self, userid, charactername, attributename):
		"""Deletes a given character's attribute, returning True if it was a success and False if it wasn't."""
		try:
			cur = self.conn.cursor()
			current_character = self.character_id_from_name(userid, charactername)
			t = (attributename, current_character, )
			cur.execute('begin')
			cur.execute('DELETE FROM attributes WHERE attributename=? AND characters_id=?', t)
			self.conn.commit()
			return True
		except Exception as e:
			self.logger.exception("Exception in call to 'remove_attribute'")
			self.conn.rollback()
			return False

if __name__ == '__main__':
    print "This is not meant to be used directly! Run 'main.py' instead."
