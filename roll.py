#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Dice roll handler component for LamiaDMBot

import random

class ValueOverRatelimit(Exception):
	"""Exception returned whenever a parameter (Number of dice, dice sides, etc.) goes over the rate limit.
	This should eventually go in its own module."""

	def __init__(self):
		Exception.__init__(self, "A parameter was used with a value over the rate limit.")

class Roll:
	"""Roll handler for LamiaDMBot"""
	
	RATELIMIT = 1000 #Any of a roll's parameters cannot be larger than this
	REPEATLIMIT = 50 #A roll cannot be repeated any more than this amount

	def __init__(self, rollparams):
		self.rollparams = rollparams
		self.result = []
		self.sum = 0 #counts successes in dicepool mode
		self.fail = 0 #counts failures in dicepool mode, otherwise set to 0
		self.modifier = 0
		self.repeat = 1
		self.fate = False
		self.exploding = False
		self.highest = False #TODO: Drop Highest and Drop Lowest modes
		self.lowest = False
		self.coin = False #TODO: Coinflip mode and until heads/tails mode ("xd2c", "1d2ch", "1d2ct")
		self.drop = 0
		self.keep = 0
		self.rollover = 0
		self.rollunder = 0
		self.optwarnings = ""
		try:
			roll_multiplier = rollparams.split("d")[0]
			roll_basedie = rollparams.split("d")[1]
			#Let's start parsing the roll

			if len(roll_basedie.split("&")) != 1: #How many repeats?
				self.repeat = int(roll_basedie.split("&")[1])
				if self.repeat > self.REPEATLIMIT:
					raise ValueOverRatelimit()
				roll_basedie = roll_basedie.split("&")[0] #Pass the rest

			#Is the very last character '!'? Exploding dice
			if rollparams.endswith("!"):
				self.exploding = True
				roll_basedie = roll_basedie[:-1]

			#Does the last element have a modifier? Add it and remove it from the string
			if "+" in roll_basedie:
				self.modifier = int(roll_basedie.split("+")[1])
				roll_basedie = roll_basedie.split("+")[0]
			elif "-" in roll_basedie:
				self.modifier = int(roll_basedie.split("-")[1])*(-1)
				roll_basedie = roll_basedie.split("-")[0]

			if ">" in roll_basedie: #We're in roll over/roll under mode
				self.rollover = int(roll_basedie.split(">")[1])
				roll_basedie = roll_basedie.split(">")[0]
			elif "<" in roll_basedie:
				self.rollunder = int(roll_basedie.split("<")[1])
				roll_basedie = roll_basedie.split("<")[0]


			#Does the last element have a Drop or Keep modifier? Add it and remove from the string
			if len(roll_basedie.split("K")) == 2:
				self.keep = int(roll_basedie.split("K")[1])
				roll_basedie = roll_basedie.split("K")[0]
			if len(roll_basedie.split("D")) == 2:
				self.drop = int(roll_basedie.split("D")[1])
				roll_basedie = roll_basedie.split("D")[0]

			#Before attempting to cast as integers, are we using FATE-style dice?
			if "F" in roll_basedie:
				roll_multiplier = int(roll_multiplier)
				roll_basedie = 6
				self.fate = True
			else:
			#Let's now cast as integers
				roll_multiplier = int(roll_multiplier)
				roll_basedie = int(roll_basedie)
			if (roll_multiplier > self.RATELIMIT) or (roll_basedie > self.RATELIMIT):
			#Values over the rate limit shall raise an exception
				raise ValueOverRatelimit()
			#Exploding dice with a size of one are considered invalid as to prevent things seizing up
			if roll_basedie == 1 and self.exploding:
				raise ValueOverRatelimit()

			x = 0
			dice_explosions = 0

			while x < roll_multiplier:
				if self.fate:
					self.result.append((random.randint(1,6) % 3) - 1)
				else:
					self.result.append(random.randint(1, roll_basedie))
				if (self.result[-1] == roll_basedie) and (self.exploding == True):
					#Prevent far too many dice explosions that might cause the bot to seize up
					if dice_explosions <= self.RATELIMIT:
						roll_multiplier+=1
						dice_explosions+=1
					else:
						self.optwarnings = "Warning: Exploding dice total above rate limit!"
				x+=1

			if self.drop != 0: #There's a Drop operation to be done
				self.result.sort() #Let's sort the list in ascending order
				self.result = self.result[self.drop:]
			if self.keep != 0: #There's a Keep operation to be done
				self.result.sort()
				self.result = self.result[((self.keep)*(-1)):]
			
			if self.rollover == 0 and self.rollunder == 0: #We're not in dicepool mode
				self.sum = sum(self.result)+self.modifier
			else:
				if self.rollover:
					for i in self.result:
						if i >= self.rollover: 
							self.sum+=1
						else:
							self.fail+=1
				elif self.rollunder:
					for i in self.result:
						if i <= self.rollunder:
							self.sum+=1 
						else:
							self.fail+=1
				self.sum+=self.modifier

		except Exception as e:
			pass

	@staticmethod
	def is_valid_roll(rollparams):
		try:
			test = Roll(rollparams)
			if len(test.result) > 0:
				return True
			else:
				return False
		except:
			return False

class Rolltable:
	"""Roll table handler for LamiaDMBot"""
	ENTRYLIMIT = 20 #The roll table must not contain more than this number of entries

	def __init__(self, rollparams, **kwargs):
		self.roll = Roll(rollparams)
		self.rolltableparams=kwargs

if __name__ == '__main__':
	print ("This is not meant to be used directly! Run 'main.py' instead.")