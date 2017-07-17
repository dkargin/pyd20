from battle.core import *
from battle.dice import *


class Item(object):
    """
    Represents base class for any item
    :type _name: str
    :type AC: int
    """
    def __init__(self, base = None, **kwargs):
        self._name = kwargs.get('name', 'noname')
        self._weight = kwargs.get("weight", 10)
        self._hardiness = 10
        # Base item type
        self._base = base
        self._effects = []

    def weight(self):
        return self._weight

    def on_equip(self, combatant):
        pass

    def on_remove(self, combatant):
        pass

    def is_weapon(self):
        return False

    def is_shield(self):
        return False

    @property
    def name(self):
        return self._name

    # Get base item
    def get_base_root(self):
        if self._base is None:
            return self
        return self._base.get_base_root()


class Weapon(Item):
    """
    Weapon class
    """
    REACH_NEAR = 1
    REACH_FAR = 2
    REACH_UNIVERSAL = 3

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
        self._two_handed = kwargs.get("two_handed", False)
        # Critical hit info
        self.crit_mult = kwargs.get("crit_mult", 2)
        self.crit_range = kwargs.get("crit_range", 1)
        # Weapon reach type
        self._reach = kwargs.get("reach", Weapon.REACH_NEAR)
        # Magic enchantment
        self._enchantment = kwargs.get("enchantment", 0)
        # Throwing range increment
        self._range = math.ceil(kwargs.get("range", 0)/5)
        self._finesse = kwargs.get("finesse", False)
        self._trip = kwargs.get("trip", False)
        # Clip size
        self._clip = kwargs.get("clip", 1)
        # Ammo type
        self._ammo = kwargs.get("ammo", None)
        self._reload = kwargs.get('reload', ACTION_TYPE_FREE)

    def can_trip(self):
        return self._trip

    def is_unarmed(self):
        return False

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
        return self._reach > Weapon.REACH_NEAR

    def has_reach_near(self):
        return (self._reach & Weapon.REACH_NEAR) is not 0

    def has_reach_far(self):
        return (self._reach & Weapon.REACH_FAR) is not 0

    # Check if that weapon is light for that combatant
    def is_light(self, combatant):
        return self._light <= combatant._size_type

    # Check if weapon finisse is appliable to a weapon
    def is_finessable(self, combatant):
        return self._finesse or self.is_light(combatant)

    # Returns if weapon is two handed
    def is_two_handed(self):
        return self._two_handed


class Armor(Item):
    """
    Represents armor
    :type _name: str
    :type AC: int
    """
    ARMOR_TYPE_NONE = 0
    ARMOR_TYPE_LIGHT = 1
    ARMOR_TYPE_MEDIUM = 2
    ARMOR_TYPE_HEAVY = 3
    ARMOR_TYPE_SHIELD = 4

    def __init__(self, base=None, **kwargs):
        Item.__init__(self, base, **kwargs)
        self.AC = kwargs.get("AC", 0)
        self._max_dex = kwargs.get("dex", 100)
        # Base item type
        self.check_penalty = kwargs.get("check", 0)
        self.speed = kwargs.get("speed", 0)
        # Arcane spell failure
        self.arcane_fail = kwargs.get('arcane_fail', 0)
        self._enchantment = 0
        self._deflection_bonus = 0
        self._cover = kwargs.get('cover', False)
        self._armor_type = kwargs.get('type', Armor.ARMOR_TYPE_NONE)

    def get_dex_bonus(self, dex):
        return min(self._max_dex, dex)

    def armor_type(self):
        return self._armor_type

    def is_shield(self):
        return self._armor_type == Armor.ARMOR_TYPE_SHIELD

    def on_equip(self, combatant):
        combatant.modify_ac_armor(self.AC + self._enchantment)
        combatant.modify_ac_dex(self._max_dex)
        if self._armor_type >= Armor.ARMOR_TYPE_MEDIUM:
            combatant.add_status_flag(STATUS_HEAVY_ARMOR)

    def on_remove(self, combatant):
        if self._move_penalty:
            combatant.remove_status_flag(STATUS_HEAVY_ARMOR)

    def __str__(self):
        return "%s (%d:%d)" % (self.name, self.AC+self._enchantment, self._max_dex)
