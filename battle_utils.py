import brain
import dnd.armor
import dnd.feats
import dnd.weapon
from battle.character import Character
from battle.core import *
from battle.grid import *
from battle.combatant import *
from dnd import classes


def draw_cross(grid, x, y, size):
    for i in range(-size, size+1):
        grid.set_terrain(x, y + i, TERRAIN_WALL)
        grid.set_terrain(x+ i, y, TERRAIN_WALL)


def draw_block(grid, type, x0, y0, width, height):
    for x in range(x0, x0+width):
        for y in range(y0, y0 + height):
            grid.set_terrain(x, y, type)


# Create shield fighter
def make_shield_fighter(name, stats=[18, 13, 16, 10, 10, 10]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, ITEM_SLOT_ARMOR)
    char.wear_item(dnd.armor.tower_shield, ITEM_SLOT_OFFHAND)
    char.wear_item(dnd.weapon.longsword, ITEM_SLOT_MAIN)
    char.add_class_level(classes.Fighter, 6)
    return char


# Create dual weapons fighter
def make_twf_fighter(name, stats=[18, 13, 16, 10, 10, 10]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, ITEM_SLOT_ARMOR)
    char.wear_item(dnd.weapon.longsword, ITEM_SLOT_MAIN)
    char.wear_item(dnd.weapon.shortsword, ITEM_SLOT_OFFHAND)
    char.add_class_level(classes.Fighter, 6)
    char.add_feat(dnd.feats.TwoWeaponFighting())
    char.add_feat(dnd.feats.ImprovedTwoWeaponFighting())
    return char

# Create dual weapons fighter
def make_archer(name, stats=[13, 18, 16, 10, 10, 10]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.add_class_level(classes.Fighter, 6)
    char.add_feat(dnd.feats.WeaponFocus(dnd.weapon.longbow_composite))
    char.add_feat(dnd.feats.ImprovedTwoWeaponFighting())

    char.wear_item(dnd.armor.banded_mail, ITEM_SLOT_ARMOR)
    char.wear_item(dnd.weapon.longbow_composite, ITEM_SLOT_MAIN)

    return char


# Create dual weapons fighter
def make_monk(name, stats=[14, 14, 16, 10, 16, 8]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.wear_item(dnd.armor.robe, ITEM_SLOT_ARMOR)
    char.wear_item(dnd.weapon.kama, ITEM_SLOT_MAIN)
    char.add_class_level(classes.Monk, 6)
    char.add_feat(dnd.feats.CombatReflexes())
    char.add_feat(dnd.feats.DeftOpportunist())

    char.allow_effect_activation(battle.combatant.StyleFlurryOfBlows())

    return char