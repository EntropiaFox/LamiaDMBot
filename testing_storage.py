#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Unit testing for storage component

from storage import LamiaDB

db = LamiaDB(':memory:')
#User Registration
assert db.register_user('1') == True
assert db.is_user_registered('1') == True
assert db.is_user_registered('2') == False
#Roll registration
assert db.register_roll('1', 'test', '1d20') == True
assert db.register_roll('1', 'test', '1d20') == False
assert db.register_roll('1', 'test2', '1d10') == True
assert db.register_roll('21', 'test', '1d20') == False
assert db.is_roll_registered('1', 'test') == True
#Roll recalling
assert db.fetch_roll('1', 'test') == (u'1d20', )
assert db.fetch_all_rolls('1') == {u'test': u'1d20', u'test2': u'1d10'}
#Roll deleting
assert db.delete_roll('1', 'test2') == True
assert db.fetch_roll('1', 'test2') == None
#Character handling
db.register_character('1', 'testchar')
db.add_attribute('1', 'testchar', 'testatt', 'testval')
db.fetch_character('1', 'testchar')