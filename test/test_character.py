from unittest import TestCase
from character import *
from dnd import barbarian, dwarf

class CharacterTest(TestCase):

    def test_character(self):
        tenlon = Character("Tenlon")
        tenlon.set_race(dwarf)
        tenlon.add_class_level(barbarian)
        print(tenlon)
