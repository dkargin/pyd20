from unittest import TestCase

from battle.actions import *
from battle.grid import Grid
import battle.events as events

class BattleTest(TestCase):

    def random_character(self):
        from test.test_character import CharacterTest
        ct = CharacterTest()
        return ct.random_character()

    def test_battle(self):
        battle = Battle(Grid.create_with_dimension(6, 6))
        battle.add_combatant(self.random_character(), 1, 1)
        battle.add_combatant(self.random_character(), 5, 5)

        for event in battle.battle_generator():
            if isinstance(event, events.RoundEnd):
                alive = [c for c in battle.combatants if c.is_active()]
                if len(alive) <= 1:
                    print("Battle has concluded. Alive=%s" % str(alive))

