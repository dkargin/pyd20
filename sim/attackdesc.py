import copy
import sim.item
from .dice import *


class AttackDesc:
    """
    Attack description structure
    Keeps all the data that can describe any sort of attack with d20 roll
    Each AttackDesc passes several stages before actual hit:
        - Attack is generated as part of BAB chain when character starts its turn
        - Picked target for an attack. Target-specific feats apply its effects
        - Resolve attack and on-hit events
        - Apply damage

    :type target: Combatant
    :type damage: Dice
    :type bonus_damage: Dice
    """
    def __init__(self, weapon: sim.item.Weapon, **kwargs):
        self.attack = kwargs.get('attack', 0)
        self.damage = kwargs.get('damage', Dice())
        # Diced bonus damage, like sneak attack, elemental damage and so on
        self.bonus_damage = Dice()
        # Estimated strike probability
        self.prob = 0
        self.damage_multiplier = 1
        self.critical_confirm_bonus = 0
        self.two_handed = kwargs.get('two_handed', False)
        self.weapon = weapon
        self.touch = kwargs.get('touch', False)
        # Attack target
        self.target = None
        self.opportunity = False
        self.spell = False
        self.ranged = False
        self.offhand = kwargs.get('offhand', False)
        self.range = 0
        # Should this attack provoke AoO, i.e unarmed or ranged attack in melee
        self.provoke = False
        # Custom attack method
        self.method = "strike"
        # Value for opposed check. Used for:
        # - trip attacks
        # - bull rush
        # - disarm
        # - sunder
        self.check = 0

    # Is melee attack
    def is_melee(self):
        return not self.ranged

    # If ranged attack
    def is_ranged(self):
        return self.ranged

    def copy(self):
        return copy.copy(self)

    def text(self):
        dmg_min, dmg_max = self.damage.get_range()
        weapon_name = self.weapon.name if self.weapon is not None else "null weapon"
        if self.prob != 0:
            return "attack with %s roll=%d prob=%d dam=%s->%d-%d" % \
                   (weapon_name, self.attack, self.prob, str(self.damage), dmg_min, dmg_max)
        else:
            return "attack with %s roll=%d dam=%s->%d-%d" % \
                   (weapon_name, self.attack, str(self.damage), dmg_min, dmg_max)

    '''
    def roll_attack(self):
        result = d20.roll()
        return self.attack + result, result
    '''

    def roll_damage(self):
        return self.damage.roll()

    def roll_bonus_damage(self):
        return self.bonus_damage.roll()

    # Calculates hit probability
    def hit_probability(self, armor_class):
        delta = 20 + self.attack - armor_class
        if delta < 1:
            delta = 1
        if delta > 19:
            delta = 19
        return delta / 20.0

    # Calculate estimated damage per round
    def estimated_damage(self, source, target):
        ac = target.get_touch_armor_class(source) if self.touch else target.get_armor_class(source)
        prob = self.hit_probability(ac)
        # TODO: calculate critical damage bonus
        damage = self.damage.mean() + self.bonus_damage.mean()
        return prob * damage, prob

    def is_critical(self, roll):
        return self.weapon.is_critical(roll)

    def get_target(self):
        """
        Get target of attack
        :return: Combatant
        """
        return self.target

    def attack_roll_info(self, roll, ac):
        return "%d(r%d%+d) vs AC=%d" % (self.attack + roll, roll, self.attack, ac)

    def update_target(self, target):
        self.target = target

    def __repr__(self):
        return self.text()
