#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# LamiaDMBot's main class based upon echobot2.py

"""
LamiaDMBot's main class based upon echobot2.py

Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging, sqlite3, ConfigParser, os
from roll import *
from storage import *
from char import *
from collections import OrderedDict

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#Token declaration
TOKEN = "TOKEN"

#Optional secret declaration, so only those who know it may use the bot
SECRET = ""

#Version information
VERSION = "v0.5.2unstable"

# Define a few helper functions

def readconfig(config_filename='lamia.cfg'):
	config = ConfigParser.ConfigParser()
	if not os.path.isfile(config_filename): #if the config file doesn't exist already, we'll create one
		config_file = open(config_filename, 'w')
		config.add_section('main')
		config.set('main', 'TOKEN', 'TOKEN')
		config.set('main', 'SECRET', '')
		config.set('main', 'ratelimit', '1000')
		config.write(config_file)
		config_file.close()
	else:
		global TOKEN, SECRET
		config.read(config_filename)
		#logger.info("Read token: %s", config.get('main', 'token'))
		TOKEN = config.get('main', 'token')
		SECRET = config.get('main', 'secret')
	return config


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update, args):
	bot.sendMessage(update.message.chat_id, text='Hiya! Type /help to get a list of all my actions.' \
	+ (" A password has been set in order to register with this bot, please ask the maintainer about it." if SECRET else ""))
	# If secret is not set, register unconditionally. If secret is set, register when user knows said secret
	if SECRET == "":
		db = LamiaDB()
		if db.register_user(update.message.from_user.id):
			bot.sendMessage(update.message.chat_id, text='New user registered. Now you can store rolls and characters!')
		db.conn.close()
	elif len(args) > 0:
		if args[0] == SECRET:
			db = LamiaDB()
			if db.register_user(update.message.from_user.id):
				bot.sendMessage(update.message.chat_id, text='New user registered. Now you can store rolls and characters!')
			db.conn.close()

def help(bot, update):
	bot.sendMessage(update.message.chat_id, text="""/start Secret - Allows you to register with the bot. A password may have been specified by the bot's maintainer.
/roll xdy - Rolls X Y-sided dice.
Other optional arguments, in order of precedence:
- Add "!" at the end to use exploding dice.
- Use "+" or "-" to add a modifier that adds or substracts that amount to the sum.
- Use ">" or "<" to count successes when rolling over or rolling under the specified amount. In this mode, the modifier adds or substracts successes.
- Use "D" or "K" to Drop a certain amount of lowest dice or Keep a certain amount of highest dice.
The bot supports FATE-style dice. In order to use them, use the xdF notation. For example, /roll 4dF tells the bot to roll four FATE dice.
/aroll Roll/RollName - Roll with advantage (The higher of two rolls is selected).
/droll Roll/RollName - Roll with disadvantage (The lower of two rolls is selected).
/sroll RollName Roll - Lets you store rolls for future use. Give the roll an identifier and then call it by name. Requires user registration.
/sroll RollName - Lets you recall a stored roll.
/listroll - Provides a list of all the stored rolls you have.
/delroll Roll - Lets you delete a stored roll.
/newchar CharacterName Attributename Attributevalue - Lets you register a new character. Requires user registration.
/char CharacterName - Displays the name and attributes of a given character.
/listchar - Provides a list of all the characters you have.
/delchar CharacterName - Lets you delete a stored character.
/attr CharacterName Attributename Attributevalue - Adds or changes the given character's attribute.
/delattr CharacterName Attributename - Deletes the given character's attribute.
/about - Shows the bot's current running version and copyright info.""")


def echo(bot, update):
	bot.sendMessage(update.message.chat_id, text=update.message.text)


def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def rolldie(bot, update, args):
	roll = Roll(args[0])
	#bot.sendMessage(update.message.chat_id, text=' '.join(args))
	if len(roll.result) > 0:
		if roll.rollunder == 0 and roll.rollover == 0:
			bot.sendMessage(update.message.chat_id, text=roll.rollparams + " | Your rolls: " + ' '.join(map(str, roll.result)) + \
			" (" + ("+" if (roll.modifier > 0) else "") + \
			str(roll.modifier) + ") = " + str(roll.sum), \
			reply_to_message_id=update.message.message_id)
		else:
			bot.sendMessage(update.message.chat_id, text=roll.rollparams + " | Your rolls: " + ' '.join(map(str, roll.result)) + \
			" (" + ("+" if (roll.modifier > 0) else "") + \
			str(roll.modifier) + ") \n" + str(roll.sum) + " successes, " + str(roll.fail) + " failures.", \
			reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.", reply_to_message_id=update.message.message_id)

def aroll(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	#First, we'll test if it's a valid roll outright
	if Roll.is_valid_roll(args[0]):
		roll1 = Roll(args[0])
		roll2 = Roll(args[0])
	else: #We'll now test if it could be a recalled roll. TODO: Fix edge case in which a valid stored roll's name can be in itself a valid roll, don't wanna do this shit right now
		sroll = db.fetch_roll(userid, args[0])[0]
		roll1 = Roll(sroll)
		roll2 = Roll(sroll)
	#Now, which one is the highest?
	if roll1.sum >= roll2.sum:
		roll1_sum = "[" + str(roll1.sum) + "]"
		roll2_sum = str(roll2.sum)
	else:
		roll2_sum = "[" + str(roll2.sum)+ "]"
		roll1_sum = str(roll1.sum)
	if len(roll1.result) > 0:
		bot.sendMessage(update.message.chat_id, text="Rolling with advantage: " + roll1.rollparams + "\n" + \
		roll1_sum + " | " + roll2_sum, reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.", reply_to_message_id=update.message.message_id)
	db.conn.close()

def droll(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	#First, we'll test if it's a valid roll outright
	if Roll.is_valid_roll(args[0]):
		roll1 = Roll(args[0])
		roll2 = Roll(args[0])
	else: #We'll now test if it could be a recalled roll. TODO: Fix edge case in which a valid stored roll's name can be in itself a valid roll, don't wanna do this shit right now
		sroll = db.fetch_roll(userid, args[0])[0]
		roll1 = Roll(sroll)
		roll2 = Roll(sroll)
	#Now, which one is the lowest?
	if roll1.sum < roll2.sum:
		roll1_sum = "[" + str(roll1.sum) + "]"
		roll2_sum = str(roll2.sum)
	else:
		roll2_sum = "[" + str(roll2.sum)+ "]"
		roll1_sum = str(roll1.sum)
	if len(roll1.result) > 0:
		bot.sendMessage(update.message.chat_id, text="Rolling with disadvantage: " + roll1.rollparams + "\n" + \
		roll1_sum + " | " + roll2_sum, reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.", reply_to_message_id=update.message.message_id)
	db.conn.close()

def storedroll(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	#check in which case we're in: is there a single argument?
	if len(args) == 1: #single argument
		#Then we're looking for a previously stored roll
		sroll_name = args[0]
		retrieved_roll = db.fetch_roll(userid, sroll_name)
		if not (retrieved_roll == None):
			rolldie(bot, update, retrieved_roll)
		else:
			bot.sendMessage(update.message.chat_id, text="Error: Stored roll not found.", reply_to_message_id=update.message.message_id)

	elif len(args) == 2: #two arguments
		#then we're storing a new roll
		sroll_name = args[0]
		sroll_value = args[1]
		if not db.is_roll_registered(userid, sroll_name):
			if Roll.is_valid_roll(sroll_value):
				if db.register_roll(userid, sroll_name, sroll_value):
					bot.sendMessage(update.message.chat_id, text="New roll stored.", reply_to_message_id=update.message.message_id)
				else:
					bot.sendMessage(update.message.chat_id, text="Error trying to register roll. Are you registered yet?", \
						reply_to_message_id=update.message.message_id)
			else:
				bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.", reply_to_message_id=update.message.message_id)
		else:
			bot.sendMessage(update.message.chat_id, text="Error: There is a stored roll with the same name.", reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.", reply_to_message_id=update.message.message_id)

	#bot.sendMessage(update.message.chat_id, text=' '.join(args))
	db.conn.close()

def listroll(bot, update):
	db = LamiaDB()
	userid = update.message.from_user.id
	roll_list = db.fetch_all_rolls(userid).keys()
	bot.sendMessage(update.message.chat_id, text="Your stored rolls: " + ' '.join(map(str, roll_list)), reply_to_message_id=update.message.message_id)
	db.conn.close()

def delroll(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	if len(args) == 1: #command takes a single argument
		sroll_name = args[0]
		if db.delete_roll(userid, sroll_name):
			bot.sendMessage(update.message.chat_id, text="Roll deleted.", reply_to_message_id=update.message.message_id)
		else:
			bot.sendMessage(update.message.chat_id, text="Error: Roll not found.", reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.", reply_to_message_id=update.message.message_id)
	db.conn.close()

def char(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	if len(args) == 1: #command takes a single argument
		charname = args[0]
		chardict = db.fetch_character(userid, charname)
		chardict = OrderedDict(sorted(chardict.items(), key=lambda t: t[0])) #Order dictionary by key
		if chardict == {}:
			bot.sendMessage(update.message.chat_id, text="Error: Character not found.", reply_to_message_id=update.message.message_id)
		else:
			output = ""
			for key, value in chardict.iteritems():
				output += (key + ": " + value + "\n")
			bot.sendMessage(update.message.chat_id, text=output, reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.", reply_to_message_id=update.message.message_id)
	db.conn.close()


def newchar(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	if len(args) >= 1: #command takes at least one argument
		charname = args[0]
		attriter = iter(args[1:])
		attrdict = dict(zip(attriter, attriter))
		reg = db.register_character(userid, charname)
		if reg and attrdict != {}: #Character registation was a success and there's at least one attribute value
			for key, value in attrdict.iteritems():
				db.add_attribute(userid, charname, key, value)
			bot.sendMessage(update.message.chat_id, text="Character registered successfully.", reply_to_message_id=update.message.message_id)
		elif reg:
			bot.sendMessage(update.message.chat_id, text="Character registered successfully.", reply_to_message_id=update.message.message_id)
		else:
			bot.sendMessage(update.message.chat_id, text="Error while attempting to register a new character.", reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.", reply_to_message_id=update.message.message_id)
	db.conn.close()


def listchar(bot, update):
	db = LamiaDB()
	userid = update.message.from_user.id
	character_list = db.fetch_all_characters(userid)
	bot.sendMessage(update.message.chat_id, text="Your characters: " + ' '.join(map(str, character_list)), reply_to_message_id=update.message.message_id)

def charattr(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	if len(args) >= 3: #command takes at least three arguments
		charname = args[0]
		attriter = iter(args[1:])
		attrdict = dict(zip(attriter, attriter))
		for key, value in attrdict.iteritems():
			if not db.add_attribute(userid, charname, key, value):
				if not db.change_attribute(userid, charname, key, value):
					bot.sendMessage(update.message.chat_id, text="Error while attempting to record or change an attribute.", \
						reply_to_message_id=update.message.message_id)
		bot.sendMessage(update.message.chat_id, text="Attributes changed.", reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.", reply_to_message_id=update.message.message_id)
	db.conn.close()

def delchar(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	if len(args) == 1: #command takes a single argument
		if not db.delete_character(userid, args[0]):
			bot.sendMessage(update.message.chat_id, text="Error while attempting to delete a character.", reply_to_message_id=update.message.message_id)
		else:
			bot.sendMessage(update.message.chat_id, text="Character deleted.", reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.", reply_to_message_id=update.message.message_id)
	db.conn.close()


def delcharattr(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	if len(args) == 2: #command takes three arguments
		if db.remove_attribute(userid, args[0], args[1]):
			bot.sendMessage(update.message.chat_id, text="Attribute removed.", reply_to_message_id=update.message.message_id)
		else:
			bot.sendMessage(update.message.chat_id, text="Error removing a character attribute.", reply_to_message_id=update.message.message_id)
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.", reply_to_message_id=update.message.message_id)
	db.conn.close()

def aboutbot(bot, update):
	bot.sendMessage(update.message.chat_id, text="LamiaDMBot " + VERSION + "\nBy EntropiaFox\nReleased under the terms of the GPL v3 License", \
		reply_to_message_id=update.message.message_id)

def main():
	try:
		# Read the configuration for the bot
		config = readconfig()

		# Create the EventHandler and pass it your bot's token.
		updater = Updater(TOKEN)

		# Get the dispatcher to register handlers
		dp = updater.dispatcher

		# on different commands - answer in Telegram
		dp.add_handler(CommandHandler("start", start, pass_args=True))
		dp.add_handler(CommandHandler("help", help))
		dp.add_handler(CommandHandler("roll", rolldie, pass_args=True))
		dp.add_handler(CommandHandler("aroll", aroll, pass_args=True))
		dp.add_handler(CommandHandler("droll", droll, pass_args=True))
		dp.add_handler(CommandHandler("sroll", storedroll, pass_args=True))
		dp.add_handler(CommandHandler("listroll", listroll))
		dp.add_handler(CommandHandler("delroll", delroll, pass_args=True))
		dp.add_handler(CommandHandler("char", char, pass_args=True))
		dp.add_handler(CommandHandler("newchar", newchar, pass_args=True))
		dp.add_handler(CommandHandler("listchar", listchar))
		dp.add_handler(CommandHandler("delchar", delchar, pass_args=True))
		dp.add_handler(CommandHandler("attr", charattr, pass_args=True))
		dp.add_handler(CommandHandler("delattr", delcharattr, pass_args=True))
		dp.add_handler(CommandHandler("about", aboutbot))

		# on noncommand i.e message - echo the message on Telegram
		#dp.add_handler(MessageHandler([Filters.text], echo))

		# log all errors
		dp.add_error_handler(error)

		# Start the Bot
		updater.start_polling()

		# Run the bot until the you presses Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		updater.idle()

	except:
		#Exception handling
		logger.exception("Exception raised.")

if __name__ == '__main__':
	main()
