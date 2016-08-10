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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#Token declaration
TOKEN = "TOKEN"

#Optional secret declaration, so only those who know it may use the bot
SECRET = ""

#Version information
VERSION = "v0.3.1"

# Define a few helper functions

def readconfig(config_filename='lamia.cfg'):
	config = ConfigParser.ConfigParser()
	if not os.path.isfile(config_filename): #if the config file doesn't exist already, we'll create one
		config_file = open(config_filename, 'w')
		config.add_section('main')
		config.set('main', 'TOKEN', 'TOKEN')
		config.set('main', 'SECRET', '')
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
    bot.sendMessage(update.message.chat_id, text='Hiya! Type /help to get a list of all my actions.')
    # If secret is not set, register unconditionally. If secret is set, register when user knows said secret
    if (SECRET == "") or (args[0] == SECRET):
    	db = LamiaDB()
    	if db.register_user(update.message.from_user.id):
    		bot.sendMessage(update.message.chat_id, text='New user registered. Now you can store rolls and characters!')
    	db.conn.close()



def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="""/roll xdy(D/K)a(+/-)z - Rolls X Y-sided dice with Z modifier.
Other optional arguments:
- Add "!" at the end to use exploding dice.
- Use "D" or "K" to Drop a certain amount of lowest dice or Keep a certain amount of highest dice.
- Use "+" or "-" to add a modifier that adds or substracts that amount to the sum.
/sroll RollName Roll - Lets you store rolls for future use. Give the roll an identifier and then call it by name. Requires user registration.
/sroll RollName - Lets you recall a stored roll.
/listroll - Provides a list of all the stored rolls you have.
/delroll Roll - Lets you delete a stored roll.
/newchar CharacterName - Lets you register a new character. Requires user registration. (TO BE IMPLEMENTED)
/char CharacterName - Displays the name and attributes of a given character. (TO BE IMPLEMENTED)""")


def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def rolldie(bot, update, args):
    roll = Roll(args[0])
    #bot.sendMessage(update.message.chat_id, text=' '.join(args))
    if len(roll.result) > 0:
    	bot.sendMessage(update.message.chat_id, text="Your rolls: " + ' '.join(map(str, roll.result)) + " | (" + ("+" if (roll.modifier > 0) else "") + str(roll.modifier) + ") | =" + str(roll.sum))
    else:
	bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.")

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
			bot.sendMessage(update.message.chat_id, text="Error: Stored roll not found.")

	elif len(args) == 2: #two arguments
		#then we're storing a new roll
		sroll_name = args[0]
		sroll_value = args[1]
		if not db.is_roll_registered(userid, sroll_name):
			if Roll.is_valid_roll(sroll_value):
				if db.register_roll(userid, sroll_name, sroll_value):
					bot.sendMessage(update.message.chat_id, text="New roll stored.")
				else:
					bot.sendMessage(update.message.chat_id, text="Error trying to register roll. Are you registered yet?")
			else:
				bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.")
		else:
			bot.sendMessage(update.message.chat_id, text="Error: There is a stored roll with the same name.")
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.")

	#bot.sendMessage(update.message.chat_id, text=' '.join(args))
	db.conn.close()

def listroll(bot, update):
	db = LamiaDB()
	userid = update.message.from_user.id
	roll_list = db.fetch_all_rolls(userid).keys()
	bot.sendMessage(update.message.chat_id, text="Your stored rolls: " + ' '.join(map(str, roll_list)))
	db.conn.close()

def delroll(bot, update, args):
	db = LamiaDB()
	userid = update.message.from_user.id
	if len(args) == 1: #command takes a single argument
		sroll_name = args[0]
		if db.delete_roll(userid, sroll_name):
			bot.sendMessage(update.message.chat_id, text="Roll deleted.")
		else:
			bot.sendMessage(update.message.chat_id, text="Error: Roll not found.")
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.")

def char(bot, update, args):
	pass

def newchar(bot, update, args):
	pass

def listchar(bot, update):
	pass


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
		dp.add_handler(CommandHandler("sroll", storedroll, pass_args=True))
		dp.add_handler(CommandHandler("listroll", listroll))
		dp.add_handler(CommandHandler("delroll", delroll, pass_args=True))

		# on noncommand i.e message - echo the message on Telegram
		dp.add_handler(MessageHandler([Filters.text], echo))

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
