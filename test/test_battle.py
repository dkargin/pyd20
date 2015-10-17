from unittest import TestCase
from battle.battle import *
from battle.actions import *
from grid import Grid


class BattleTest(TestCase):

    def random_character(self):
        from test.test_character import CharacterTest
        ct = CharacterTest()
        return ct.random_character()

    def test_battle(self):
        battle = Battle(Grid.create_with_dimension(6, 6))
        battle.add_combatant(self.random_character(), 1, 1)
        battle.add_combatant(self.random_character(), 5, 5)
        print(battle.grid)
        battle.next_round()
        print(battle.grid)
