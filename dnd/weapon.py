from battle.core import *
from battle.dice import *

from .item import Item

REACH_NEAR = 1
REACH_FAR = 2
REACH_UNIVERSAL = 3


class Weapon(Item):
    """
    Weapon class
    """
    def __init__(self, base=None, **kwargs):
        Item.__init__(self, base, **kwargs)
        # If weapon is double-sided
        self._double = kwargs.get("double", False)
        self._damage = kwargs.get("damage", d6)
        # Off-side weapon damage
        self._damage_off = kwargs.get("damage_off", d6)
        # Monster size, which considers this weapon 'Light'
        self._light = kwargs.get("light", SIZE_MEDIUM)
        # Can be gripped by two hands
        self._twohanded = kwargs.get("twohanded", False)
        # Critical hit info
        self.crit_mult = kwargs.get("crit_mult", 2)
        self.crit_range = kwargs.get("crit_range", 1)
        # Additionan reach
        self._reach = kwargs.get("reach", REACH_NEAR)
        # Magic enchantment
        self._enchantment = kwargs.get("enchantment", 0)
        # Throwing range increment
        self._range = kwargs.get("range", 0)
        self._finisse = kwargs.get("finisse", False)
        self._trip = kwargs.get("trip", False)

    def enchant(self, level):
        self._enchantment = level

    def is_critical(self, roll):
        return roll > (20 - self.crit_range)

    def is_ranged(self):
        return self._range > 0

    def is_weapon(self):
        return True

    def damage(self, combatant, target=None):
        return self._damage.copy()

    def has_reach(self):
        return self._reach > REACH_NEAR

    def has_reach_near(self):
        return (self._reach & REACH_NEAR) is not 0

    def has_reach_far(self):
        return (self._reach & REACH_FAR) is not 0

    # Check if that weapon is light for that combatant
    def is_light(self, combatant):
        return self._light <= combatant._size

    # Check if weapon finisse is appliable to a weapon
    def is_finissable(self, combatant):
        return self._finisse or self.is_light(combatant)

    # Returns if weapon is twohanded
    def is_twohanded(self):
        return self._twohanded


# Simple weapons
dagger = Weapon(name='dagger', damage=d4,
                light=SIZE_SMALL,
                twohanded=False,
                crit_mult=2, crit_range=2,
                range=10)
# Light martial
kukri = Weapon(name='Kukri', damage=d4,
               light=SIZE_MEDIUM,
               twohanded=False,
               crit_mult=2,
               crit_range=3,
               range=0)

kama = Weapon(name='kama', damage=d6,
               light=SIZE_SMALL,
               twohanded=False,
               crit_mult=2,
               crit_range=1,
               range=0)

quarterstaff = Weapon(name='quarterstaff', damage=d6,
              light=SIZE_SMALL,
              twohanded=False,
              crit_mult=2,
              crit_range=1,
              range=0)

shortsword = Weapon(name='Shord sword',
                    damage=d6,
                    light=SIZE_MEDIUM,
                    twohanded=False,
                    crit_mult=2, crit_range=2,
                    range=0)
# Medium martial
longsword = Weapon(name='Long sword', damage=d8, light=SIZE_LARGE,
                        twohanded=False,
                        crit_mult=2, crit_range=2,
                        range=0)
rapier = Weapon(name='Rapier', damage=d6, light=SIZE_MEDIUM,
                     twohanded=False,
                     crit_mult=2, crit_range=3,
                     finisse=True,range=0)

scimitar = Weapon(name='Scimitar', damage=Dice("d6"), light=SIZE_LARGE,
                  twohanded=False,
                  crit_mult=2, crit_range=3,
                  range=0)
# Twohanded melee
falchion = Weapon(name='Falchion', damage=Dice("2d6"), light=SIZE_HUGE,
                  twohanded=True,
                  crit_mult=2, crit_range=3)

glaive = Weapon(name='Glaive',
                damage=Dice("d10"),
                light=SIZE_HUGE,
                twohanded=True,
                crit_mult=3, crit_range=1,
                reach=REACH_UNIVERSAL)

guisarme  = Weapon(name='Guisarme',
                damage=Dice("d10"),
                light=SIZE_HUGE,
                twohanded=True,
                crit_mult=3, crit_range=1,
                reach=REACH_UNIVERSAL, trip=True)

halberd = Weapon(name='Halberd', damage=Dice("d10"), light=SIZE_LARGE,
                  twohanded=True,
                  crit_mult=3, crit_range=1, trip=True)

greatsword = Weapon(name='Greatsword',
                    damage=Dice("2d6"),
                    light=SIZE_HUGE,
                    twohanded=True,
                    crit_mult=2, crit_range=1)

scythe = Weapon(name='Scythe',
                    damage=Dice("1d4"),
                    light=SIZE_HUGE,
                    twohanded=True,
                    crit_mult=4, crit_range=1)

