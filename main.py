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
VERSION = "v0.3.0"

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
		logger.info("Read token: %s", config.get('main', 'token'))
		TOKEN = config.get('main', 'token')
		SECRET = config.get('main', 'secret')
	return config


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hiya! Type /help to get a list of all my actions.')
    # If secret is not set, register unconditionally
    if SECRET == "":
    	db = LamiaDB()
    	db.register_user(update.message.from_user.id)
    	db.conn.close()


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="""/roll xdy(D/K)a(+/-)z - Rolls X Y-sided dice with Z modifier.
Other optional arguments:
- Add "!" at the end to use exploding dice.
- Use "D" or "K" to Drop a certain amount of lowest dice or Keep a certain amount of highest dice.
- Use "+" or "-" to add a modifier that adds or substracts that amount to the sum.
/sroll RollName Roll - Lets you store rolls for future use. Give the roll an identifier and then call it by name.""")


def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def rolldie(bot, update, args):
    roll = Roll(args[0])
    #bot.sendMessage(update.message.chat_id, text=' '.join(args))
    if len(roll.result) > 0:
    	bot.sendMessage(update.message.chat_id, text="Your rolls: " + ' '.join(map(str, roll.result)) + " | (" + ("+" if (roll.modifier >= 0) else "") + str(roll.modifier) + ") | =" + str(roll.sum))
    else:
	bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.")

def storedroll(bot, update, args):
	db = LamiaDB()
	#check in which case we're in: is there a single argument?
	if len(args) == 1: #single argument
		#Then we're looking for a previously stored roll
		sroll_name = args[0]
		c = db.conn.cursor()
		t = (sroll_name, )
		c.execute('SELECT roll FROM rolls WHERE name=?', t)
		retrieved_roll = c.fetchone()
		if not (retrieved_roll == None):
			rolldie(bot, update, retrieved_roll)
		else:
			bot.sendMessage(update.message.chat_id, text="Error: Stored roll not found.")

	elif len(args) == 2: #two arguments
		#then we're storing a new roll
		sroll_name = args[0]
		sroll_value = args[1]
		c = db.conn.cursor()
		t = (sroll_name, )
		c.execute('SELECT roll FROM rolls WHERE name=?', t)
		retrieved_roll = c.fetchone()
		if retrieved_roll == None:
			if Roll.is_valid_roll(sroll_value):
				t = (sroll_name, sroll_value, )
				c.execute('INSERT INTO rolls (name, roll) VALUES (?, ?)', t)
				db.conn.commit()
				bot.sendMessage(update.message.chat_id, text="New roll stored.")
			else:
				bot.sendMessage(update.message.chat_id, text="Error: Invalid roll.")
		else:
			bot.sendMessage(update.message.chat_id, text="Error: There is a stored roll with the same name.")
	else:
		bot.sendMessage(update.message.chat_id, text="Error: Invalid number of arguments.")

	#bot.sendMessage(update.message.chat_id, text=' '.join(args))
	db.conn.close()


def main():
	try:
		# Read the configuration for the bot
		config = readconfig()

		# Create the EventHandler and pass it your bot's token.
		updater = Updater(TOKEN)

		# Get the dispatcher to register handlers
		dp = updater.dispatcher

		# on different commands - answer in Telegram
		dp.add_handler(CommandHandler("start", start))
		dp.add_handler(CommandHandler("help", help))
		dp.add_handler(CommandHandler("roll", rolldie, pass_args=True))
		dp.add_handler(CommandHandler("sroll", storedroll, pass_args=True))

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
		logger.info("Token value: %s", TOKEN)
		logger.exception("Exception raised.") 

if __name__ == '__main__':
	main()
