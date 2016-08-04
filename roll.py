#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Dice roll handler component for LamiaDMBot

import random

class Roll:
	"""Roll handler for LamiaDMBot"""
		
	def __init__(self, rollparams):
		self.result = []
		self.sum = 0
		self.modifier = 0
		self.exploding = False
		try:
			roll_multiplier = rollparams.split("d")[0]
			roll_basedie = rollparams.split("d")[1]
			#Let's start parsing the roll
			#Is the very last character '!'? Exploding dice
			if rollparams.endswith("!"):
				self.exploding = True
				roll_basedie = roll_basedie[:-1]
			
			#Does the last element have a modifier? Add it and remove it from the string
			if len(roll_basedie.split("+")) == 2:
				self.modifier = int(roll_basedie.split("+")[1])
				roll_basedie = roll_basedie.split("+")[0]
			elif len(roll_basedie.split("-")) == 2:
				self.modifier = int(roll_basedie.split("-")[1])*(-1)
				roll_basedie = roll_basedie.split("-")[0]

			#Let's now cast as integers
			roll_multiplier = int(roll_multiplier)
			roll_basedie = int(roll_basedie)

			x = 0

			while x < roll_multiplier:
				self.result.append(random.randint(1, roll_basedie))
				if (self.result[-1] == roll_basedie) and (self.exploding == True):
					roll_multiplier+=1
				x+=1
			self.sum = sum(self.result)+self.modifier
		except:
			pass

	@staticmethod
	def isvalidroll(rollparams):
		try:
			roll_multiplier = rollparams.split("d")[0]
			roll_basedie = rollparams.split("d")[1]
			#Let's start parsing the roll
			#Is the very last character '!'? Exploding dice
			if rollparams.endswith("!"):
				roll_basedie = roll_basedie[:-1]
			#Does the last element have a modifier? Add it and remove it from the string
			if len(roll_basedie.split("+")) == 2:
				modifier = int(roll_basedie.split("+")[1])
				roll_basedie = roll_basedie.split("+")[0]
			elif len(roll_basedie.split("-")) == 2:
				modifier = int(roll_basedie.split("+")[1])
				roll_basedie = roll_basedie.split("-")[0]

			#Let's now cast as integers
			roll_multiplier = int(roll_multiplier)
			roll_basedie = int(roll_basedie)
			
			#Everything looks fine? Return True
			return True

		except:
			#No? Then return false
			return False

if __name__ == '__main__':
    print "This is not meant to be used directly! Run 'main.py' instead."