from sim.character import Feat, Character
from sim.combatant import *
from sim.item import *

import dnd.weapon as weapons


class TwoWeaponFighting(Feat):
    def __init__(self):
        Feat.__init__(self, "twf1")

    def apply(self, combatant):
        def event(c: Combatant, desc: AttackDesc):
            if c._many_weapon_wield:
                desc.attack += 6 if desc.offhand else 2

        combatant.event_manager().on_calc_attack += event


class ImprovedTwoWeaponFighting(Feat):
    """
    Improved two-weapon fighting
    Requirements: Two-Weapon Fighting (PH) , DEX 17, base attack bonus +6
    """
    def __init__(self):
        Feat.__init__(self, "ImprovedTWF")
        self._description = "In addition to the standard single extra attack you get with an off-hand weapon, you get a second attack with it, albeit at a - 5 penalty (see Table 8-10, page 160)."
        self._priority -= 10

    def apply(self, combatant):
        def turn_event(c: Combatant):
            weapon = c.get_offhand_weapon()
            if weapon is not None:
                c.add_bonus_strike(-5, weapon, offhand=True)

        events = combatant.event_manager()
        events.on_turn_start += turn_event


class GreaterTwoWeaponFighting(Feat):
    """
    Greater two-weapon fighting
    Requirements: Improved Two-Weapon Fighting (PH) , Two-Weapon Fighting (PH) , DEX 19, base attack bonus +11,
    """
    def __init__(self):
        Feat.__init__(self, "GreaterTWF")
        self._priority -= 20

    def apply(self, combatant):
        def turn_event(c: Combatant):
            weapon = c.get_offhand_weapon()
            if weapon is not None:
                c.add_bonus_strike(-10, weapon, offhand=True)

        events = combatant.event_manager()
        events.on_turn_start += turn_event


class OversizedTwoWeaponFighting(Feat):
    """
    Oversized two weapon fighting
    """
    def __init__(self):
        Feat.__init__(self, "OversizedTWF")
        self._priority += 10

    def apply(self, combatant):
        def event(c: Combatant, desc: AttackDesc):
            if c._many_weapon_wield and not c.get_offhand_weapon().is_light(combatant):
                desc.attack += 2

        combatant.event_manager().on_calc_attack += event


class Rage(Feat):
    class Effect(Combatant.StatusEffect):
        def __init__(self, level):
            super(Rage.Effect, self).__init__()
            # Rage level
            self._level = level
            self._stat_bonus = 4

            if self._level == 1:
                self._stat_bonus = 6
            elif self._level == 2:
                self._stat_bonus = 8

        def on_start(self, combatant: Combatant, **kwargs):
            combatant.modify_stat(STAT_STR, self._stat_bonus)
            combatant.modify_stat(STAT_CON, self._stat_bonus)
            combatant.modify_save_will(2)
            self.set_duration(2 + combatant.constitution_modifier())

        def on_finish(self, combatant: Combatant, **kwargs):
            combatant.modify_stat(STAT_STR, -self._stat_bonus)
            combatant.modify_stat(STAT_CON, -self._stat_bonus)
            combatant.modify_save_will(2)
            self.set_duration(2 + combatant.constitution_modifier())

    def __init__(self):
        Feat.__init__(self, "b_rage")

    def apply(self, combatant: Character):
        #combatant.add_feat_action(ActivateEffect(), DURATION_STANDARD)
        pass


class MonkBonusAC(Feat):
    """
    Monk AC bonus
    Provides: AC bonus equal to wisdom_mod + monk_lvl/5
    Works only if character has ARMOR_TYPE_NONE armor
    """
    def __init__(self):
        self._bonus = 0

    def apply(self, combatant:Character):
        events = combatant.event_manager()
        events.on_turn_start += self.on_start

    # Called when effect has started
    def on_start(self, combatant, **kwargs):
        armor = combatant.get_armor_type()
        new_bonus = self._bonus
        if armor == Armor.ARMOR_TYPE_NONE:
            monk_levels = combatant.get_class_level("monk")
            new_bonus = math.floor(monk_levels / 5) + combatant.wisdom_modifier()
        else:
            new_bonus = 0

        delta = new_bonus - self._bonus
        # Apply the change
        if delta != 0:
            self._bonus += delta
            combatant.modify_ac_dodge(delta)


class MonkMovement(Feat):
    """
    Monk movement speed bonus
    """
    def __init__(self):
        super(MonkMovement, self).__init__("Monk movement speed bonus")
        self._bonus = 0

    def apply(self, combatant: Combatant):
        events = combatant.event_manager()
        events.on_turn_start += self.on_start

    # Called when effect has started
    def on_start(self, combatant, **kwargs):
        armor = combatant.get_armor_type()
        new_bonus = self._bonus
        if armor == Armor.ARMOR_TYPE_NONE:
            monk_levels = combatant.get_class_level("monk")
            new_bonus = math.floor(monk_levels / 3) * 10
        else:
            new_bonus = 0

        delta = new_bonus - self._bonus
        # Apply the change
        if delta != 0:
            self._bonus += delta
            combatant.modify_move_speed(delta, self)


class CombatReflexes(Feat):
    """
    Combat Reflexes
    Provides: Can execute attacks of opportinuty up to a dex modifier
    """
    def __init__(self):
        super(CombatReflexes, self).__init__("Combat Reflexes")
        self._bonus_attacks = 0

    def apply(self, combatant:Character):
        events = combatant.event_manager()
        events.on_turn_start += self.on_start
        events.on_change_dex += self.on_dex_changed

    def on_dex_changed(self, combatant, effect, old, new):
        mod_new = ability_modifier(new)
        mod_old = ability_modifier(old)
        delta = mod_new - mod_old
        combatant._opportunity_attacks += delta

    def on_start(self, combatant):
        self._bonus_attacks = max(combatant.dexterity_modifier(), 1)
        combatant._opportunity_attacks = self._bonus_attacks


class DeftOpportunist(Feat):
    """
    Deft opportunist
    Provides: "You get a +4 bonus on attack rolls when making attacks of opportunity."
    """
    def __init__(self):
        super(DeftOpportunist, self).__init__("Deft Opportunist")
        "Prerequisite: Combat Reflexes (PH) , DEX 15,"
        self.description = "[General]\nYou are prepared for the unexpected."
        self.description_benefit = "You get a +4 bonus on attack rolls when making attacks of opportunity."

    def apply(self, combatant: Combatant):
        def event(c, desc: AttackDesc):
            if desc.opportunity:
                desc.attack += 4

        combatant.event_manager().on_select_attack_target += event


class ImprovedTrip(Feat):
    """
    Improved trip feat
    """
    def __init__(self):
        super(ImprovedTrip, self).__init__("Improved feat")

    def apply(self, combatant: Combatant):
        def event(c, desc: AttackDesc):
            if desc.method == 'trip':
                desc.check += 4

        combatant.event_manager().on_select_attack_target += event
        combatant.add_status_flag(STATUS_HAS_IMPROVED_TRIP)


class InsightfulStrike(Feat):
    def __init__(self):
        super(InsightfulStrike, self).__init__("Insightful strike")

    def apply(self, combatant: Combatant):
        def event(c, desc: AttackDesc):
            mod = c.intellect_modifier()
            if mod > 0:
                desc.damage.add_die(1, mod)
        combatant.event_manager().on_calc_attack += event


class WeaponFinesse(Feat):
    """
    Can replace strength modifier by dexterity modifier for melee attacks
    """
    def __init__(self):
        super(WeaponFinesse, self).__init__("WeaponFinesse")

    def apply(self, combatant: Combatant):
        def event(c, desc: AttackDesc):
            dex_mod = c.dexterity_modifier()
            str_mod = c.strength_modifier()
            weapon = desc.weapon

            if desc.is_melee() and dex_mod > str_mod and weapon.is_finessable(combatant):
                bonus = dex_mod - str_mod
                desc.attack += bonus

        combatant.event_manager().on_calc_attack += event


class WeaponFocus(Feat):
    def __init__(self, weapon):
        weapon_root = weapon.get_base_root()
        super(WeaponFocus, self).__init__("Weapon focus (%s)" % weapon_root.name)
        self._weapon = weapon_root

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_calc_attack += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        if self._weapon == desc.weapon.get_base_root():
            desc.attack += 1


class PowerCritical(Feat):
    def __init__(self, weapon):
        weapon_root = weapon.get_base_root()
        super(PowerCritical, self).__init__("Power critical (%s)" % weapon_root.name)
        self._weapon = weapon_root

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_calc_attack += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        if self._weapon == desc.weapon.get_base_root():
            desc.critical_confirm_bonus += 4


class PointBlankShot(Feat):
    def __init__(self):
        super(PointBlankShot, self).__init__("Point blank shot")

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_select_attack_target += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        if desc.ranged() and desc.range < 30:
            desc.attack += 1


class PreciseShot(Feat):
    def __init__(self):
        super(PointBlankShot, self).__init__("Point blank shot")

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_select_attack_target += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        # Fixing -4 penalty
        if desc.ranged() and desc.range < 5:
            desc.attack += 4


class SpinningHalberd(Feat):
    def __init__(self, weapon=weapons.halberd):
        super(SpinningHalberd, self).__init__("Spinning halberd")
        weapon_root = weapon.get_base_root()
        self._weapon = weapon_root
        self._brief = "You have mastered the style of fighting with a halberd, and can use all parts of the weapon blade, spike, hook, or butt to strike devastating blows"
        self._desc = "When you make a full attack with your halberd, you gain a +1 dodge bonus to your Armor Class as well as an additional attack with the weapon at a -5 penalty. This attack deals points of bludgeoning damage equal to 1d6 + 1/2 your Strength modifier."

    def apply(self, combatant: Combatant):
        def turn_event(c: Combatant):
            weapon = c.get_main_weapon()
            if self._weapon == weapon.get_base_root():
                # TODO: add proper haft strike
                c.add_bonus_strike(-5, weapon)

        def on_start_defence(c: Combatant, effect):
            if isinstance(effect, StyleDefenciveFight):
                c.modify_ac_dodge(1, self)

        def on_stop_defence(c: Combatant, effect):
            if isinstance(effect, StyleDefenciveFight):
                c.modify_ac_dodge(-1, self)

        events = combatant.event_manager()
        events.on_turn_start += turn_event
        events.on_effect_start += on_start_defence
        events.on_effect_stop += on_stop_defence


class FlurryOfBlows(Feat):
    def __init__(self):
        super(FlurryOfBlows, self).__init__("Flurry of blows")

    def apply(self, combatant: Combatant):
        combatant.allow_effect_activation(StyleFlurryOfBlows(), self)


# Timed activation
# Stops after a set of rounds
class Rage(Feat):
    def __init__(self):
        super(Rage, self).__init__("Rage")

    def apply(self, combatant: Combatant):
        pass
        #combatant.allow_effect_activation(StatusRage, self)