import brain
import classes
import dnd.armor
import dnd.weapon
import dnd.feats
from battle.core import *
from battle.battle import Battle
from battle.grid import *
from battle.character import Character

def draw_cross(grid, x, y, size):
    for i in range(-size, size+1):
        grid.set_terrain(x, y + i, TERRAIN_WALL)
        grid.set_terrain(x+ i, y, TERRAIN_WALL)

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
def make_monk(name, stats=[14, 14, 16, 10, 16, 8]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.wear_item(dnd.armor.robe, ITEM_SLOT_ARMOR)
    char.wear_item(dnd.weapon.kama, ITEM_SLOT_MAIN)
    #char.wear_item(dnd.weapon., ITEM_SLOT_OFFHAND)
    char.add_class_level(classes.Monk, 6)
    char.add_feat(dnd.feats.CombatReflexes())
    char.add_feat(dnd.feats.DeftOpportunist())
    # char.add_feat(dnd.feats.ImprovedTwoWeaponFighting())
    return char