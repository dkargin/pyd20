from unittest import TestCase

import core
from character import Character

import dnd.armor
import dnd.weapon
from dnd import classes

char1 = Character("Bob")
char1.set_stats(18, 13, 16, 10, 10, 10)
char1.wear_item(dnd.armor.full_plate, core.ITEM_SLOT_ARMOR)
char1.wear_item(dnd.weapon.glaive, core.ITEM_SLOT_MAIN)
char1.add_class_level(classes.Fighter, 6)

# Create shield fighter
def make_shield_fighter(name, stats=[18, 13, 16, 10, 10, 10], **kwargs):
    char = Character(name)
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, core.ITEM_SLOT_ARMOR)
    char.wear_item(dnd.armor.tower_shield, core.ITEM_SLOT_OFFHAND)
    char.wear_item(dnd.weapon.longsword, core.ITEM_SLOT_MAIN)
    char.add_class_level(classes.Fighter, 6)
    return char

# Create dual weapons fighter
def make_twf_fighter(name, stats=[18, 13, 16, 10, 10, 10], **kwargs):
    char = Character(name, **kwargs)
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, core.ITEM_SLOT_ARMOR)
    char.wear_item(dnd.weapon.longsword, core.ITEM_SLOT_MAIN)
    char.wear_item(dnd.weapon.shortsword, core.ITEM_SLOT_OFFHAND)
    char.add_class_level(classes.Fighter, 6)
    char._twf_skill = 1
    #char.add_feat(feats.TWF)
    return char


char2 = make_shield_fighter('Roy')
char3 = make_twf_fighter('Dancey')


# Just prints generated attack sequence
class AttackGeneratorTest(TestCase):
    def test_attack_sequence(self):
        print(char1.print_character())
        print(char2.print_character())
        print(char3.print_character())
