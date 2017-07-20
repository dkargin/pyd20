import brain
import dnd.armor
import dnd.feats
import dnd.weapon
from sim.character import Character
from sim.core import *
from sim.grid import *
from sim.combatant import *
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
def make_shield_fighter(name, stats=[18, 13, 16, 10, 10, 10], **kwargs):
    char = Character(name, brain=brain.MoveAttackBrain(), **kwargs)
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, ITEM_SLOT_ARMOR)
    char.wear_item(dnd.armor.tower_shield, ITEM_SLOT_OFFHAND)
    char.wear_item(dnd.weapon.longsword, ITEM_SLOT_MAIN)
    char.add_class_level(classes.Fighter, 6)
    return char


# Create dual weapons fighter
def make_twf_fighter(name, stats=[18, 13, 16, 10, 10, 10], **kwargs):
    char = Character(name, brain=brain.MoveAttackBrain(), **kwargs)
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, ITEM_SLOT_ARMOR)
    char.wear_item(dnd.weapon.bastard_sword, ITEM_SLOT_MAIN)
    char.wear_item(dnd.weapon.longsword, ITEM_SLOT_OFFHAND)
    char.add_class_level(classes.Fighter, 6)
    # 1,1,2,3,4,6,6
    char.add_feat(dnd.feats.TwoWeaponFighting())
    char.add_feat(dnd.feats.ImprovedTwoWeaponFighting())
    char.add_feat(dnd.feats.OversizedTwoWeaponFighting())
    #char.add_feat(dnd.feats.Dodge())
    #char.add_feat(dnd.feats.Mobility())
    #char.add_feat(dnd.feats.())

    return char


# Create dual weapons fighter
def make_archer(name, stats=[13, 18, 16, 10, 10, 10]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.add_class_level(classes.Fighter, 6)
    char.add_feat(dnd.feats.WeaponFocus(dnd.weapon.longbow_composite))
    char.add_feat(dnd.feats.PointBlankShot())
    char.add_feat(dnd.feats.PreciseShot())
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
    char.add_feat(dnd.feats.ImprovedTrip())
    return char


'''
Owlbear skeleton: CR 2; Large undead; HD 5d12; hp 32; Init +6; Spd 30 ft. (6 squares);
AC 13 (-1 size, +2 dex, +2 natural), touch 11, flat-footed 11;
Base Atk +2; Grp +11;
Atk +6 melee (1d6+5, claw); Full Atk +6 melee (1d6+5, 2 claws) and +1 melee (1d8+2, bite);
Space/Reach 10 ft./5 ft.; SA -; SQ Damage reduction 5/bludgeoning, darkvision 60 ft., immunity to cold, undead traits; AL NE;
SV Fort +1, Ref +3, Will +4; Str 21, Dex 14, Con -, Int -, Wis 10, Cha 1

Skills and Feats: ; Improved Initiative
'''